import random
from flask import Flask, render_template, request, redirect, url_for, session
from tasks import TRUTHS, DARES

app = Flask(__name__)
app.secret_key = "change-this-to-any-random-text"


def next_player():
    queue = session.get("queue", [])

    # when everyone has played, shuffle all names again for a new round
    if not queue:
        queue = session["players"][:]
        random.shuffle(queue)

        # avoid the same person playing last in one round and first in the next
        if len(queue) > 1 and queue[-1] == session.get("current"):
            queue[0], queue[-1] = queue[-1], queue[0]

    player = queue.pop()
    session["queue"] = queue
    return player


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    names = request.form.getlist("player")
    names = [n.strip() for n in names if n.strip()]

    session["players"] = names
    session["queue"] = []
    session["used"] = {}
    session["current"] = None
    session["current"] = next_player()
    session["kind"] = None
    session["task"] = None
    return redirect(url_for("game"))


@app.route("/game")
def game():
    if not session.get("players"):
        return redirect(url_for("index"))

    return render_template(
        "game.html",
        player=session["current"],
        kind=session["kind"],
        task=session["task"],
    )


@app.route("/choose", methods=["POST"])
def choose():
    kind = request.form.get("kind")

    if kind == "Truth":
        pool, prefix = TRUTHS, "T"
    else:
        kind, pool, prefix = "Dare", DARES, "D"

    player = session["current"]
    used = session.get("used", {})
    seen = used.get(player, [])

    # tasks this player has not received yet
    options = [i for i in range(len(pool)) if f"{prefix}{i}" not in seen]

    # if this player has received every truth (or dare), start that list again
    if not options:
        seen = [s for s in seen if not s.startswith(prefix)]
        options = list(range(len(pool)))

    i = random.choice(options)
    seen.append(f"{prefix}{i}")
    used[player] = seen

    session["used"] = used
    session["task"] = pool[i]
    session["kind"] = kind
    return redirect(url_for("game"))


@app.route("/complete", methods=["POST"])
def complete():
    session["current"] = next_player()
    session["kind"] = None
    session["task"] = None
    return redirect(url_for("game"))


if __name__ == "__main__":
    app.run(debug=True)