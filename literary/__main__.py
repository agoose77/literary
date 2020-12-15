import argparse

from .commands import build, test


def run(argv=None):
    parser = argparse.ArgumentParser(description="Top-level literary executable")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in build, test:
        sub_parser = command.configure(subparsers)
        sub_parser.set_defaults(run=command.run)

    args = parser.parse_args(argv)
    args.run(args)


if __name__ == "__main__":
    run()
