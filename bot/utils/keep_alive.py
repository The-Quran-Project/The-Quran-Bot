import flask
import time
import threading

start = time.time()


def secondsToTime(s):
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    d = int(d)
    h = int(h)
    m = int(m)
    s = int(s)

    result = ""
    if d > 0:
        result += f"{d} day{'s' if d > 1 else ''}"
    if h > 0:
        result += f" {h} hour{'s' if h > 1 else ''}"
    if m > 0:
        result += f" {m} minute{'s' if m > 1 else ''}"
    if not result:
        result = "0 minutes"
    return result.strip()


def runFlask(host: str = "0.0.0.0", port: int = 8080):
    print("Running Flask APP")
    app = flask.Flask("Quran Bot")

    @app.route("/")
    def index():
        return f"""<h1 style="font-family:Arial;text-align:center;">Running for {secondsToTime(time.time()-start)}</h1>"""

    threading.Thread(target=app.run, args=(host, port)).start()
