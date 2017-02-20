import requests
import requests_cache
import re
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from collections import OrderedDict
from operator import itemgetter
from urllib.error import URLError


requests_cache.install_cache("meetup_polls", expire_after=180)

votes_re = re.compile("(?P<n_votes>\d+) votes?")

def get_polls(group, poll_id):
    res = requests.get(f"https://www.meetup.com/{group}/polls/{poll_id}/")
    soup = BeautifulSoup(res.text, "lxml")

    votes = []
    if not soup.select(".poll .line"):
        raise URLError("Poll doesn't exists")
    for entry in soup.select(".poll .line"):
        count_text = entry.find(class_="count").text.strip()
        match = votes_re.match(count_text) or {"n_votes": 0}
        votes.append((entry.find("label").text.strip(), int(match["n_votes"])))

    votes.sort(key=itemgetter(1), reverse=True)
    votes = OrderedDict(votes)

    return votes


default_font = ImageFont.truetype("fonts/helvetica-normal.ttf", 20)

def generate_image(votes, bar_width=200, bar_height=20, line_height=50,
                   side_margin=50, margin_between=20, bar_colour="#4C72B0",
                   text_colour="#000000", back_colour="#FFFFFF",
                   border_colour="#000000", separator_colour="#CCCCCC",
                   font=default_font):

    max_vote = max(votes.values())
    longest_label = max(votes, key=len)
    longest_counter = f"{max_vote} votes"

    label_width, _ = font.getsize(longest_label)
    counter_width, _ = font.getsize(longest_counter)
    width = side_margin * 2 + margin_between * 2 + label_width + \
        bar_width + counter_width
    height = side_margin * 2 + line_height * len(votes)

    im = Image.new("RGB", (width, height), color=back_colour)
    draw = ImageDraw.Draw(im)

    bar_x = (side_margin + label_width + margin_between)
    space_between = (line_height - bar_height) / 2

    for i, (label, count) in enumerate(votes.items()):
        bar_y = side_margin + line_height * i

        draw.rectangle([(bar_x, bar_y),
                        (bar_x + bar_width * count / max(max_vote, 1), bar_y + \
                         bar_height)], fill=bar_colour)

        draw.rectangle([(bar_x, bar_y),
                        (bar_x + bar_width, bar_y + bar_height)],
                       outline=border_colour)

        draw.text([side_margin, bar_y], label, fill=text_colour, font=font)

        plural = "s" if count != 1 else ""
        draw.text([bar_x + bar_width + margin_between, bar_y],
                  f"{count} vote{plural}", fill=text_colour, font=font)

        if i + 1 != len(votes):
            draw.line([(side_margin, bar_y + bar_height + space_between),
                       (width - side_margin, bar_y + bar_height + space_between)],
                      fill=separator_colour)

    return im


if __name__ == "__main__":
    votes = get_polls("Taipei-py", "804752")
    im = generate_image(votes)
    im.save("taipei-804752.png")
