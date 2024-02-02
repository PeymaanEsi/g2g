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
    except:
        print("DRIVER ERROR!")
        exit(-1)

    wait = WebDriverWait(driver=driver, timeout=10)

    driver.maximize_window()

    urls = []
    try:
        driver.get("https://www.g2g.com/trending/game-coins")
        wait.until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
        print("Page Loaded.")
        press("f12")
        # import time
        # time.sleep(1000)
    except:
        print("GET ERROR!")
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
                print(urls)
    except:
        print("swiper-wrapper NOT FOUND!")
    
    print('DONE')
    # driver.__exit__()
    return urls

def get_offers_web(games_url):

    page_number = 1

    print("Page", page_number)

    while True:

        try:
            driver = Chrome()
            print("Driver Created.")
        except:
            print("DRIVER ERROR!")
            exit(-1)

        wait = WebDriverWait(driver=driver, timeout=10)

        driver.maximize_window()

        try:
            driver.get(games_url + '?page=' + str(page_number))
        except Exception as e:
            print("GET ERROR!", e)
            return

        time.sleep(5)

        wait.until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )

        # offers_boxes = driver.find_elements(by=By.CLASS_NAME, value="col-xs-12")

        offers_boxes = driver.find_elements(
            by=By.CSS_SELECTOR, value=".col-xs-12.col-sm-6.col-md-3"
        )

        if len(offers_boxes) == 0:
            print("NOTHING!")
            page_number = 1
            break

        print("Found", len(offers_boxes), "offers.")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ellipsis-2-lines")))

        for offer_box in offers_boxes:
            title = (
                offer_box.find_element(
                    by=By.CSS_SELECTOR, value=".text-body1.ellipsis-2-lines"
                )
                .find_element(by=By.TAG_NAME, value="span")
                .text
            )
            price = (
                offer_box.find_element(by=By.CSS_SELECTOR, value=".col-grow.order-last")
                .find_elements(by=By.TAG_NAME, value="span")[1]
                .text
            )
            currency = (
                offer_box.find_element(by=By.CSS_SELECTOR, value=".col-grow.order-last")
                .find_elements(by=By.TAG_NAME, value="span")[2]
                .text
            )

            count = offer_box.find_element(
                by=By.CSS_SELECTOR, value=".g-chip-counter"
            ).text

            print(title, price, currency, datetime.datetime.now().timestamp(), sep="\t")
            
        page_number += 1

        driver.close()




trends=get_trends_web()
print(trends)
for game in trends:
    print('Get offers from game', game[0])
    get_offers_web(game[1])