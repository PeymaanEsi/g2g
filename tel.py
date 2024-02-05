TOKEN = "6255848310:AAHkqJORIdCX85-3EvBlyLYevh_Q4liQHcA"

ID = "24523436"

HASH = "3ee21bc315a5d5eedc469e3493b40472"

import sqlite3
import time
import datetime
from math import ceil

import aiosqlite

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


app = Client("gameg0bot", api_id=ID, api_hash=HASH, bot_token=TOKEN)


# Define a command handler
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "Hi, I'm GameG0 Bot. Select A Game To See Offers With /offer."
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

    current_time = datetime.datetime.now()

    # Calculate the time one hour ago
    one_hour_ago = current_time - datetime.timedelta(hours=1)

    # Get the timestamp for one hour ago
    timestamp_one_hour_ago = one_hour_ago.timestamp()

    # print(current_time.timestamp(), timestamp_one_hour_ago)

    offers = await db.execute(
        "SELECT name, price FROM offer WHERE gameid = ? AND time < ?",
        (callback_query.data, timestamp_one_hour_ago),
    )

    data = await offers.fetchall()

    # Paginate the data
    page_size = 5  # You can adjust the number of items per page
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

    # Send the data with pagination
    await client.send_message(
        callback_query.from_user.id,
        text=current_page_data[:100],
        reply_markup=pagination_keyboard,
    )

# Run the bot
app.run()
