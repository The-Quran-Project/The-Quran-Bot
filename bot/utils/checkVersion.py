import sys


def checkVersion():
    if sys.version_info < (3, 12):
        print("", "-" * 33, sep="\n")
        print(f"{'Warning':*^33}")
        print("-" * 33, "", sep="\n")

        print(
            "This bot should run on Python 3.12 | Some features may not work on older versions"
        )
        print(
            "You are running Python {}.{} | Consider upgrading".format(
                sys.version_info[0], sys.version_info[1]
            )
        )

        print("", "-" * 33, "-" * 33, "", sep="\n")
