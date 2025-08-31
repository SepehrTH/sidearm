import os, json
import subprocess
import tempfile
import shutil

CONFIG_DIR = os.path.expanduser("~/.sidearm")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")



def init():
    if os.path.exists(CONFIG_DIR):
        ans = input(f"[!] Config directory already exists at {CONFIG_FILE}. Overwrite? (y/[N]) ").strip()
        if ans.lower() != 'y':
            print("[*] Keeping existing configuration.")
            return

    os.makedirs(CONFIG_DIR, exist_ok=True)
    print(f"[+] Created config directory at {CONFIG_DIR}")

    default_tools_dir = os.path.expanduser('~/tools')
    default_bin_dir = os.path.join(default_tools_dir, "bin")

    tools_dir = input(f"Tools directory [{default_tools_dir}](Enter if fine): ") or default_tools_dir
    bin_dir = input(f"Bin directory [{default_bin_dir}](Enter if fine): ") or default_bin_dir

    os.makedirs(tools_dir, exist_ok=True)
    os.makedirs(bin_dir, exist_ok=True)

    tools_config = os.path.join(tools_dir, "tools.json")
    if not os.path.exists(tools_config):
        with open(tools_config, "w") as f:
            json.dump([], f, indent=2)

    config = {"tools_dir": tools_dir, "bin_dir": bin_dir}

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

    print(f"[+] Sidearm initialized. Tools will be installed in {tools_dir}.")
    print(f"You can edit the {tools_dir}/tools.json and then run ]\"sidearm sync\" if you have a ready config file.")
    print("You can the bin directory to path by executing the following command or pasting into ~/.profile :")
    print(f'\texport PATH="{bin_dir}:$PATH"')


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def get_dirs():
    config = load_config()
    return config["tools_dir"], config["bin_dir"]

def atomic_write_json(data, path):
    """
    Safely write JSON data to a file. 
    Ensures we never leave a half-written tools.json if interrupted.
    """
    dir_name = os.path.dirname(path)
    with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False) as tmp:
        json.dump(data, tmp, indent=2)
        temp_name = tmp.name

    # Replace old file atomically
    shutil.move(temp_name, path)

def install_or_update(name):
    TOOLS_DIR, BIN_DIR = get_dirs()
    tools_file = os.path.join(TOOLS_DIR, "tools.json")
    with open(tools_file) as f:
        tools = json.load(f)

    tool = next((t for t in tools if t["name"] == name), None)
    if not tool:
        print(f"[!] Tool '{name}' not found in tools.json")
        return
    
    repo = tool['repo'].strip().rstrip('/')

    if tool['type'] == 'git':
        dest = os.path.join(TOOLS_DIR, name)
        if os.path.exists(dest):
            print(f"[=] Updating {name}")
            try:
                subprocess.run(f"git -C {dest} pull", shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"[!] Failed to update {name}: {e}")

        else:
            print(f"[+] Installing {name}")
            try:
                subprocess.run(f"git clone {repo} {dest}", shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"[!] Failed to clone {name}: {e}")
                
        os.makedirs(BIN_DIR, exist_ok=True)

        exec_dest = os.path.join(dest, tool['exec'])

        symlink_dest = os.path.join(BIN_DIR, tool['name'])

        if not os.path.exists(exec_dest):
            print(f"[!] Executable {exec_dest} does not exist, skipping symlink")
        else:
            if os.path.exists(symlink_dest):
                os.remove(symlink_dest)

            print(f"[+] Adding symlink to {symlink_dest}")
            os.symlink(exec_dest, symlink_dest)

    elif tool['type'] == 'go':
        # Addin @latest to the end of repo if there is no version.
        if '@' not in repo:
            repo += '@latest'

        try:
            subprocess.run(f"go install {repo}", shell=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to install {tool['name']}: {e}")
        
    

def add():
    TOOLS_DIR, BIN_DIR = get_dirs()
    tools_config = os.path.join(TOOLS_DIR, "tools.json")

    ty = ''
    while ty not in ['git', 'go']:
        ty = input("Enter the repo type: (go/git) ").strip()

    repo = input('Enter repo: ').strip().rstrip('/')
    
    name = input("Enter the name of the repo: ")
    
    exec_path = input("Enter the relative path of the executable file from the repo: (ex: a.py) ") if ty=='git' else ''

    new_tool = {
        "name": name,
        "type": ty,
        "repo": repo,
        "exec": exec_path
    }

    with open(tools_config, "r") as f:
        tools = json.load(f)

    tools.append(new_tool)
    
    atomic_write_json(tools, tools_config)

    install_or_update(name)


def validate_tool(tool):
    """
    Validate a tool entry from tools.json.
    Returns (True, None) if valid, (False, error_message) if not.
    """
    required_common = ["name", "type", "repo"]
    for key in required_common:
        if key not in tool or not isinstance(tool[key], str) or not tool[key].strip():
            return False, f"Missing or invalid '{key}' field"

    if tool["type"] not in ["git", "go"]:
        return False, f"Invalid type '{tool['type']}', must be 'git' or 'go'"

    if tool["type"] == "git":
        if "exec" not in tool or not isinstance(tool["exec"], str) or not tool["exec"].strip():
            return False, "Git tool must specify non-empty 'exec' field"

    return True, None


def sync():
    TOOLS_DIR, BIN_DIR = get_dirs()
    tools_config = os.path.join(TOOLS_DIR, "tools.json")
    with open(tools_config) as f:
        tools = json.load(f)

    for tool in tools:
        valid, error = validate_tool(tool)
        if not valid:
            print(f"[!] Skipping invalid entry: {error}")
            continue
        install_or_update(tool["name"])
        print(f"{tool['name']} => Done")
    print('All done.')