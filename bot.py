# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01
import threading
import time
import requests

def keep_alive():
    urls = [
        "https://exotic-darb-monish2807-df2d5a43.koyeb.app/",
        "https://scornful-andreana-moxi35-c66f799a.koyeb.app/"  # Replace with your second bot's URL
    ]
    
    while True:
        for url in urls:
            try:
                requests.get(url)
            except:
                pass
        time.sleep(90)  # Ping every 90 seconds

threading.Thread(target=keep_alive, daemon=True).start()

# Clone Code Credit : YT - @Tech_VJ / TG - @VJ_Bots / GitHub - @VJBots

import sys, glob, importlib, logging, logging.config, pytz, asyncio
from pathlib import Path

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)

from pyrogram import Client, filters, idle
from database.users_chats_db import db
from info import *  # Import your info.py variables here
from utils import temp
from typing import Union, Optional, AsyncGenerator
from Script import script 
from datetime import date, datetime 
from aiohttp import web
from plugins import web_server
from plugins.clone import restart_bots

from TechVJ.bot import TechVJBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

# ADD THESE IMPORTS for MongoDB
from pymongo import MongoClient, UpdateOne

# MongoDB Connection from info.py
client = MongoClient(DATABASE_URI)   # Using the MONGO_DB_URI variable from info.py
db = client['moxi_movies']           # Using the MONGO_DB_NAME from info.py
collection = db['Telegram_files']    # Using the MONGO_COLLECTION from info.py

OWNER_ID = 6476946240  # Replace with your Telegram ID if not in info.py

# CAPTION REMOVAL COMMAND
@TechVJBot.on_message(filters.command("removecaption") & filters.user(OWNER_ID))
async def fast_remove_caption(client, message):
    msg = await message.reply("Starting fast removal of `caption` fields... Please wait...")

    batch_size = 1000
    total_modified = 0
    total_docs = collection.count_documents({"caption": {"$exists": True}})
    removed_count = 0

    if total_docs == 0:
        await msg.edit_text("No documents with captions found!")
        return

    await msg.edit_text(f"Removing captions... {removed_count}/{total_docs} (0%) done...")

    while True:
        docs = list(collection.find({"caption": {"$exists": True}}, {"_id": 1}).limit(batch_size))
        if not docs:
            break

        operations = [UpdateOne({"_id": doc["_id"]}, {"$unset": {"caption": ""}}) for doc in docs]
        result = collection.bulk_write(operations)

        removed_count += result.modified_count
        progress = int((removed_count / total_docs) * 100)

        await msg.edit_text(f"Removing captions... {removed_count}/{total_docs} ({progress}%) done...")

    await msg.edit_text(f"Bulk Removal Completed!\nModified {removed_count} documents.")


ppath = "plugins/*.py"
files = glob.glob(ppath)
TechVJBot.start()
loop = asyncio.get_event_loop()

async def start():
    print('\n')
    print('Initalizing Your Bot')
    bot_info = await TechVJBot.get_me()
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Tech VJ Imported => " + plugin_name)
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    me = await TechVJBot.get_me()
    temp.BOT = TechVJBot
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    logging.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    try:
        await TechVJBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    except:
        print("Make Your Bot Admin In Log Channel With Full Rights")
    for ch in CHANNELS:
        try:
            k = await TechVJBot.send_message(chat_id=ch, text="**Bot Restarted**")
            await k.delete()
        except:
            print("Make Your Bot Admin In File Channels With Full Rights")
    try:
        k = await TechVJBot.send_message(chat_id=AUTH_CHANNEL, text="**Bot Restarted**")
        await k.delete()
    except:
        print("Make Your Bot Admin In Force Subscribe Channel With Full Rights")
    if CLONE_MODE == True:
        print("Restarting All Clone Bots.......")
        await restart_bots()
        print("Restarted All Clone Bots.")
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
