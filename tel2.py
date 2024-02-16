import sqlite3

import aiosqlite

from telethon.sync import TelegramClient, events

# Replace these values with your own API ID and Hash
api_id = "24655557"
api_hash = "d9d6471436f1e5bcac3cdfef6bf8b8e1"

import aiosqlite
from telethon.sync import TelegramClient, events

# Create a TelegramClient instance
client = TelegramClient("GameG0Bot", api_id, api_hash)


async def search_in_database(query):
    try:
        db = await aiosqlite.connect(database="./db.sqlite3")
        print("DB Connected.")
    except sqlite3.Error:
        print("DB ERROR!")
        exit(-1)

    # Execute a query to search for the given name in the database
    cursor = await db.execute(
        "SELECT name, price FROM offer WHERE name LIKE ? ORDER BY time DESC LIMIT 1",
        ("%" + query + "%",),
    )

    # Fetch the results
    data = await cursor.fetchall()

    msg = ""

    for o in data:
        o = str(o)
        # print(repr(o), type(o))
        o = o.replace("(", "")
        o = o.replace(")", "")
        o = o.replace("'", "")
        o += "\n"
        o = "🗾" + o
        o = o.replace("[", "🌐: [")
        o = o.replace("Alliance", "🤺")
        o = o.replace("Horde", "👹")
        o = o.replace(",", ", 💵: ")
        # print(o)
        msg += o

    return msg


@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(
        """
👋درود👋
🤖به بات GaemG0 خوش اومدید🤖
🤑برای دیدن قیمت آفرها🤑
 👇لطفا روی دستور زیر کلیک کنید👇
/search
"""
    )


@client.on(events.NewMessage(pattern="/search"))
async def search(event):
    await event.respond("Please enter the name or keyword you want to search:")
    await client.send_typing(event.chat_id)


@client.on(events.NewMessage)
async def handle_message(event):
    if event.text.startswith("/search"):
        query = event.text.split("/search", 1)[1].strip()
        results = await search_in_database(query)
        if results:
            await event.respond(f'Search results for "{query}": {results}')
        else:
            await event.respond(f'No results found for "{query}"')


async def main():
    await client.start()
    await client.run_until_disconnected()


if __name__ == "__main__":
    client.loop.run_until_complete(main())
