from selenium import webdriver
import time
from bs4 import BeautifulSoup
import sqlite3
from selenium.webdriver.common.by import By

# Connecting to Database
db = sqlite3.connect("games.db")

# Using selenium to update JS
driver = webdriver.Chrome()
url = "https://old.chesstempo.com/chess-openings.html"
driver.maximize_window()
driver.get(url)

# Giving timr to load
time.sleep(2)

# Connecting parser


# Getting the page buttons

for i in range(2, 41):
    time.sleep(2)
    my_element = driver.find_element(By.XPATH, f"//a[text()='{str(i)}']")
    my_element.click()
    content = driver.page_source.encode("utf-8").strip()
    soup = BeautifulSoup(content, "html.parser")

    openings = soup.find_all("table")[1]
    rows = openings.find_all("tr")

    # Making a list for buffer work for ease of understandability
    opening_list = []

    # Making a list of dicts for each of the openings
    opening_dict = []

    # Getting the html data for all the openings (each row in table)
    for row in rows:
        divs = list(row.find_all("div"))
        opening_list.append(divs)

    # Deleting firt one because its useless
    del opening_list[0]

    # loopping through html tags
    for i in opening_list:
        try:
            # Configuring color
            color = None
            if "white" in str(i[1]):
                color = "white"
            else:
                color = "black"

            # Making a dict data for the opening
            data = {
                "name": str(i[0].text),
                "color": color,
                "win_rate": str(i[8].text),
                "draw_rate": str(i[9].text),
                "loss_rate": str(i[10].text),
                "moves": str(i[11].text),
            }

            # Appending dict to master dict
            opening_dict.append(data)
        except:
            print("nope")

    # Getting sql cursor
    cursor = db.cursor()

    # Declaring query
    query = "INSERT INTO opening (name, color, win_rate, draw_rate, loss_rate, moves) VALUES (?,?,?,?,?,?)"

    # Looping through each opening and adding it to database
    for opening in opening_dict:
        # Declaring data tuple
        data_tuple = (
            opening["name"],
            opening["color"],
            opening["win_rate"],
            opening["draw_rate"],
            opening["loss_rate"],
            opening["moves"],
        )
        cursor.execute(query, data_tuple)

    # Closing cursor and commiting changes
    cursor.close()
    db.commit()
