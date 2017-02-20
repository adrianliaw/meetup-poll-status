from flask import Flask, make_response, abort
from gen_image import get_polls, generate_image
from io import BytesIO
from urllib.error import URLError


app = Flask(__name__)

@app.route("/")
def index():
    return "VOTE DAT"

@app.route("/<group>/<poll_id>")
def make_image(group, poll_id):
    try:
        votes = get_polls(group, poll_id)
    except URLError:
        abort(404)
    im = generate_image(votes)
    catcher = BytesIO()
    im.save(catcher, "png")
    res = make_response(catcher.getvalue())
    res.content_type = f"image/png"
    return res
