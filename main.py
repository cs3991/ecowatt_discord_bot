#!/usr/bin/env python3
import logging
import os
from datetime import datetime, timedelta

import discord
from discord.ext import tasks
from dotenv import load_dotenv

from ecowatt_api import EcoWattAPIRepository, EcoWattValue

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1025470081930641530

# Discord messages are limited to 2000 characters. This also includes space for 6 '`' characters for a code block
MAX_MESSAGE_LEN = 2000 - 6

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('alerte_ecowatt.main')

# Create the bot and specify to only look for messages starting with '#'
intents = discord.Intents.default()
# intents.message_content = True
bot = discord.Client(intents=intents)

ecowatt_repository = EcoWattAPIRepository()


@bot.event
async def on_ready():
    logger.info(f'{bot.user.name} has connected to Discord and is in the following channels:')
    for guild in bot.guilds:
        logger.info(f' |  - {guild.name}')
    repeated_task.start()


@tasks.loop(hours=1)
async def repeated_task():
    if datetime.now().hour == 19:
        signals = ecowatt_repository.fetch_ecowatt_values()
        channel = bot.get_channel(CHANNEL_ID)
        for signal in signals:
            if signal.value != EcoWattValue.GREEN and signal.day == (datetime.today() + timedelta(days=1)).date():
                await channel.send(signal.pretty_print())

bot.run(TOKEN)
