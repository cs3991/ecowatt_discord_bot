#!/usr/bin/env python3
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Sequence

import discord
from discord.ext import tasks
from dotenv import load_dotenv
from requests import HTTPError

from ecowatt_api import EcoWattAPIRepository, EcoWattValue, EcoWattDay

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

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
async def on_ready() -> None:
    logger.info(f'{bot.user.name} est connecté dans les guildes suivantes :')
    for guild in bot.guilds:
        logger.info(f' |  - {guild.name}')
    repeated_task.start()


@tasks.loop(hours=1)
async def repeated_task() -> None:
    if datetime.now().hour == 18:
        message: Optional[str] = None
        logger.info("Task started")
        try:
            signals: tuple[EcoWattDay] = ecowatt_repository.fetch_ecowatt_values()
            for signal in signals:
                if signal.value != EcoWattValue.GREEN and signal.day == (datetime.today() + timedelta(days=1)).date():
                    message: str = signal.pretty_print() + ' @everyone '
            guilds: Sequence[discord.Guild] = bot.guilds
            if message is not None:
                for guild in guilds:
                    await guild.system_channel.send(message)
                logger.info(f'Jour tendu trouvé, message envoyé à {len(guilds)} guildes :\n{message}')
        except HTTPError:
            logger.error('Erreur lors de la récupération des données')


bot.run(TOKEN)
