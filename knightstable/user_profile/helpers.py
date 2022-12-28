import os
from PIL import Image
import secrets
from bs4 import BeautifulSoup
import requests

# Profile Picture saving
def save_pfp(pfp, app):
    # Create unique hex
    hex = secrets.token_hex(7)

    # Get extention of the image
    _, f_ext = os.path.splitext(pfp.filename)

    # Create file name
    filename = hex + f_ext

    # Make path
    path = os.path.join(app.root_path, "static/img/pfp", filename)

    # Deciding output size
    output_size = (221, 228)
    print(output_size)
    # Opening image with pillow
    i = Image.open(pfp)
    # Resizing
    i.resize(output_size)

    # Saving resized image into path
    i.save(path)


def get_uscf_rating(id):
    # Getting response form url
    response = requests.get("https://www.uschess.org/msa/MbrDtlMain.php?" + str(id))
    # bs4
    content = BeautifulSoup(response.text, "html.parser")
    rating = str(content.find("nobr").text).split()[0]
    return rating
