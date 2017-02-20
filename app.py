from flask import Flask, make_response, abort
from gen_image import get_polls, generate_image, default_font
from io import BytesIO
from urllib.error import URLError
from PIL import ImageFont


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
    try:
        "".join(votes.keys()).encode("ascii")
    except UnicodeEncodeError:
        font = ImageFont.truetype("fonts/儷黑-pro.ttf")
    else:
        font = default_font
    im = generate_image(votes, font=font)
    catcher = BytesIO()
    im.save(catcher, "png")
    res = make_response(catcher.getvalue())
    res.content_type = f"image/png"
    return res
