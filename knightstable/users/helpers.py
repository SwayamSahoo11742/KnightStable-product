from bs4 import BeautifulSoup
import requests


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
        title = event_names[i].text
        date = event_dates[i].text
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
    rating = str(content.find("nobr").text).split()[0]
    return rating
