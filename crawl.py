#!/bin/python3

import time
import datetime
import sqlite3

from selenium.webdriver import Chrome
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pyautogui import press

try:
    db = sqlite3.connect(database="./db.sqlite3")
    print("DB Connected.")
except sqlite3.Error:
    print("DB ERROR!")
    exit(-1)


def get_trends_web():

    
    try:
        driver = Chrome()
        print("Driver Created.")
    except Exception as e:
        print("DRIVER ERROR!", e)
        exit(-1)

    urls = []
    try:
        driver.get("https://www.g2g.com/trending/game-coins")
        wait = WebDriverWait(driver=driver, timeout=10)
        driver.maximize_window()
        wait.until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
        print("Page Loaded.")
        press("f12")
        time.sleep(10)
        # import time
    except Exception as e:
        print("GET ERROR!", e)
        exit(-1)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "swiper-wrapper")))
        trends_boards = driver.find_element(
            by=By.CLASS_NAME, value="swiper-wrapper"
        ).find_elements(by=By.TAG_NAME, value="a")
        print(len(trends_boards), "swiper-wrapper Found.")
        for trend_board in trends_boards:
            trends_name = trend_board.find_element(
                by=By.CLASS_NAME, value="ellipsis-2-lines"
            ).text
            trend_url = trend_board.get_attribute("href")
            try:
                print(trends_name, trend_url)
                db.execute(
                    "INSERT INTO game('name', 'url') VALUES (?, ?)",
                    (trends_name, trend_url),
                )
                db.commit()
            except sqlite3.IntegrityError as e:
                print("UNIQUE ERROR!", e)
                # continue
            finally:
                urls.append((trends_name, trend_url))
                # print('f')
                # print(urls)
    except:
        print("swiper-wrapper NOT FOUND!")

    print("DONE")
    # driver.__exit__()
    return urls


def get_offers_web(game_name, games_url):

    id_query = "SELECT id, name FROM game WHERE name = " + "'" + game_name + "'"

    game_id = db.execute(id_query).fetchall()[0][0]

    page_number = 1

    while True:

        try:
            driver = Chrome()
            print("Driver Created.")
        except Exception as e:
            print("DRIVER ERROR!", e)
            exit(-1)

        try:
            print("Page", page_number)
            driver.get(games_url + "?page=" + str(page_number))
            wait = WebDriverWait(driver=driver, timeout=10)
            driver.maximize_window()
        except Exception as e:
            print("GET ERROR!", e)
            return

        try:
            wait.until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )

            press("f12")
            time.sleep(10)

            # offers_boxes = driver.find_elements(by=By.CLASS_NAME, value="col-xs-12")

            offers_boxes = driver.find_elements(
                by=By.CSS_SELECTOR, value=".col-xs-12.col-sm-6.col-md-3"
            )

            if len(offers_boxes) == 0:
                print("NOTHING!")
                # page_number = 1
                break

            print("Found", len(offers_boxes), "offers.")

            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "ellipsis-2-lines"))
            )

            # print("TEST")
            for offer_box in offers_boxes:
                title = (
                    offer_box.find_element(
                        by=By.CSS_SELECTOR, value=".text-body1.ellipsis-2-lines"
                    )
                    .find_element(by=By.TAG_NAME, value="span")
                    .text
                )
                price = (
                    offer_box.find_element(
                        by=By.CSS_SELECTOR, value=".col-grow.order-last"
                    )
                    .find_elements(by=By.TAG_NAME, value="span")[1]
                    .text
                )

                # print('IDddddd', game_id)

                data = (title, price, datetime.datetime.now().timestamp(), game_id)

                # print(data, sep="\t")

                try:
                    db.execute(
                        "INSERT INTO offer('name', 'price', 'time', 'gameid') VALUES (?, ?, ?, ?)",
                        data,
                    )
                    # print('YO')
                    db.commit()
                    # print('toto')
                except Exception as e:
                    print("UNIQUE ERROR!", e)
                    continue

        except Exception as e:
            print("CRAWL ERROR!", e)
            continue

        page_number += 1

        # driver.close()


def main():
    trends = get_trends_web()
    # print(trends)
    for game in trends:
        if game[0]:
            print("Get offers from game", game[0])
            get_offers_web(game[0], game[1])

    print("Finish")

    db.commit()

    # db.close()
