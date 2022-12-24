import re
import os
from PIL import Image
import secrets

# Profile Picture saving
def save_pfp(pfp, app):
    # Create unique hex
    hex = secrets.token_hex(7)

    # Get extention of the image
    _, f_ext = os.path.splitext(pfp.filename)

    # Create file name
    filename = hex + f_ext

    # Make path
    path = os.path.join(app.root_path, 'static/img/pfp', filename)

    # Deciding output size
    output_size = (150,150)
    print(output_size)
    # Opening image with pillow
    i = Image.open(pfp)
    # Resizing
    i.resize(output_size)

    # Saving resized image into path
    i.save(path)

    return filename

# Removing eval lines
def strip_eval(x):
    # remove curly braces and number in them
    x = re.sub("\{.*?\}", "", x)
    # Remove random eval numbers
    x = re.sub(".\.\.\.", "", x)
    # Remove random periods
    x = re.sub("\$.", "", x)
    # Join together to get rid of whitespace
    x = " ".join(x.split())
    return x

# Capitalizing
def cap(x):
    return x.capitalize()


# CHecking for login
def attempt(dictionary, x):
    try:
        # If logged exitss
        dictionary[x]
        # user is logged in
        return True
    except:
        # If logged does not exit
        # User is not logged in
        return False
