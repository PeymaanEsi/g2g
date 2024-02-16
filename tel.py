TOKEN = "6863511511:AAHL0A0qEtjGIciV6VSLUMgZSUBNfonD0kE"

ID = "24655557"

HASH = "d9d6471436f1e5bcac3cdfef6bf8b8e1"

import sqlite3
import time
import datetime
from math import ceil

import aiosqlite

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers.message_handler import MessageHandler


app = Client("gameg0bot", api_id=ID, api_hash=HASH, bot_token=TOKEN)


# Define a command handler
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        """
👋درود👋
🤖به بات GaemG0 خوش اومدید🤖
🤑برای دیدن قیمت آفرها🤑
 👇لطفا روی دستور زیر کلیک کنید👇
/search
"""
    )


@app.on_message(filters.command("offer"))
async def offer_command(client, message):
    try:
        db = await aiosqlite.connect(database="./db.sqlite3")
        print("DB Connected.")
    except sqlite3.Error:
        print("DB ERROR!")
        exit(-1)
    games = await db.execute("SELECT name, id FROM game")
    games = await games.fetchall()
    # print(games)
    inlines = []
    for game in games:
        if game[0]:
            inlines.append([InlineKeyboardButton(game[0], callback_data=str(game[1]))])
    keyboard = InlineKeyboardMarkup(inlines)

    await message.reply_text("Select a game:", reply_markup=keyboard)

    await db.close()


# Define a callback query handler
@app.on_callback_query()
async def callback_query_handler(client, callback_query):
    try:
        db = await aiosqlite.connect(database="./db.sqlite3")
        print("DB Connected.")
    except sqlite3.Error:
        print("DB ERROR!")
        exit(-1)

    # print(callback_query.data)

    # current_time = datetime.datetime.now()

    # Calculate the time one hour ago
    # one_hour_ago = current_time - datetime.timedelta(hours=1)

    # Get the timestamp for one hour ago
    # timestamp_one_hour_ago = one_hour_ago.timestamp()

    # print(current_time.timestamp(), timestamp_one_hour_ago)

    offers = await db.execute(
        "SELECT name, price FROM offer WHERE gameid = ? ORDER BY time DESC LIMIT 500",
        (callback_query.data, ),
    )

    data = await offers.fetchall()

    # Paginate the data
    page_size = 40  # You can adjust the number of items per page
    num_pages = ceil(len(data) / page_size)

    page = int(callback_query.data) if callback_query.data.isdigit() else 1
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    current_page_data = data[start_index:end_index]

    # Create a new InlineKeyboardMarkup for pagination
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton("Previous", callback_data=str(page - 1))
        )
    if page < num_pages:
        pagination_buttons.append(
            InlineKeyboardButton("Next", callback_data=str(page + 1))
        )

    pagination_keyboard = InlineKeyboardMarkup([pagination_buttons])

    # print(current_page_data)

    msg = ""

    for o in current_page_data:
        o = str(o)
        o = o.replace("(", "")
        o = o.replace(")", "")
        o = o.replace("'", "")
        o += '\n'
        o = '🗾' + o
        o = o.replace('[', '🌐: [')
        o = o.replace('Alliance', '🤺')
        o = o.replace('Horde', '👹')
        o = o.replace(',', ', 💵: ')
        # print(o)
        msg += o

    msg = msg + '\n Page: ' + str(page)

    # Send the data with pagination
    await client.send_message(
        callback_query.from_user.id,
        text=msg,
        reply_markup=pagination_keyboard,
    )

# app.add_handler(MessageHandler("start"))
# app.add_handler(MessageHandler("offer"))

# Run the bot
app.run()
