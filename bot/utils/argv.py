import argparse

parser = argparse.ArgumentParser()


parser.add_argument(
    "-l",
    "--local",
    help="If you want to run the bot locally or not. (1=true, 0=false)",
    type=int,
    required=False,
    default=0,
)

parser.add_argument(
    "-sf",
    "--stop-flask",
    help="If you want to stop the flask server. (1=true, 0=false)",
    type=int,
    required=False,
    default=0,
)

parser.add_argument(
    "-st",
    "--stop-thread",
    help="If you want to stop the thread of MongoDB database [Warning: Database won't be updated!]. (1=true, 0=false)",
    type=int,
    required=False,
    default=0,
)


parser.add_argument(
    "-fm",
    "--fix-mongo",
    help="use dns resolver for pymongo (1=true, 0=false)",
    type=int,
    required=False,
    default=0,
)


arguments = parser.parse_args()


class Obj:
    ARG_LOCAL = arguments.local
    ARG_STOP_FLASK = arguments.stop_flask
    ARG_STOP_THREAD = arguments.stop_thread
    ARG_FIX_MONGO = arguments.fix_mongo

    def __init__(self):
        pass


def getArguments():
    return Obj()
