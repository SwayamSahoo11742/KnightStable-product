import re
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
    path = os.path.join(app.root_path, 'static/img/pfp', filename)

    # Deciding output size
    output_size = (221,228)
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

def get_tournaments(max):
    event_list = []
    # get url response
    response = requests.get("https://calendar.fide.com/")
    # bs4
    content = BeautifulSoup(response.text, "html.parser")

    # Getting event name and dates
    event_names = content.find_all(class_="session-title")
    event_dates = content.find_all(class_="session-time")
    # Looping through "max" number of times
    for i in range(max):
        # Getting title and date and link
        title =  event_names[i].text 
        date =  event_dates[i].text
        link = event_names[i].a["href"]

        # Creating and inserting to a temp dict
        event_dict = {}
        event_dict["name"] = title
        event_dict["date"] = date
        event_dict["link"] = link
        # Appending temp dict to the main list
        event_list.append(event_dict)
    return event_list

def get_uscf_rating(id):
    # Getting response form url
    response = requests.get("https://www.uschess.org/msa/MbrDtlMain.php?" + str(id))
    # bs4
    content = BeautifulSoup(response.text, "html.parser")
    rating= str(content.find("nobr").text).split()[0]
    return rating

