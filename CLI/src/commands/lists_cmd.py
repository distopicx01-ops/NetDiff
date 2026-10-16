from tools import load


def add_parser(sub):
    for command, folder in (("whitelist", "white-list"), ("blacklist", "black-list")):
        p = sub.add_parser(command, help=f"Maneja la {folder}")
        p.add_argument("action", choices=["add", "remove", "show"])
        p.add_argument("ip", nargs="?")
        p.set_defaults(func=run, folder=folder)


def run(args):
    tool = load(args.folder)
    if args.action == "show":
        for ip in tool.get_all():
            print(ip)
    elif not args.ip:
        print("Falta la IP")
    elif args.action == "add":
        tool.add(args.ip)
        print(f"{args.ip} agregada")
    else:
        tool.remove(args.ip)
        print(f"{args.ip} quitada")