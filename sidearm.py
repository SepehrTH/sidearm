#!/usr/bin/env python3

import argparse
from sidearm.core import init, sync, install_or_update, add


def main():
    parser = argparse.ArgumentParser(description="Sidearm: Personal pentesting tool manager")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init", help="Initialize Sidearm and set directories")
    subparsers.add_parser("sync", help="Sync the tools with tools.json and latest versions")
    subparsers.add_parser("add", help="Adding a tool. No arguments needed.")


    install_parser = subparsers.add_parser("get", help="Install/Update a specific tool by name")
    install_parser.add_argument("tool_name", help="Name of the tool to install/Update")

    args = parser.parse_args()

    if args.command == 'init':
        init()
    elif args.command == "sync":
        sync()
    elif args.command == "add":
        add()
    elif args.command == "get":
        install_or_update(args.tool_name)

if __name__ == "__main__":
    main()