import argparse

from CLI.src.commands import check_cmd, deep_cmd, diff_cmd, lists_cmd, scan_cmd

COMMANDS = [scan_cmd, diff_cmd, deep_cmd, check_cmd, lists_cmd]


def build_parser():
    parser = argparse.ArgumentParser(prog="netdiff", description="Que cambio en mi red?")
    sub = parser.add_subparsers(dest="command")
    for command in COMMANDS:
        command.add_parser(sub)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()