#!/usr/bin/env python3
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Sequence

import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
from requests import HTTPError

from ecowatt_api import EcoWattAPIRepository, EcoWattValue, EcoWattDay

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TEST_GUILD_ID = os.getenv('TEST_GUILD_ID')

# Discord messages are limited to 2000 characters. This also includes space for 6 '`' characters for a code block
MAX_MESSAGE_LEN = 2000 - 6

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

invite_link = "https://discord.com/api/oauth2/authorize?client_id=1025428488703971389&permissions=3072&scope=bot"
bot = commands.Bot(intents=intents, command_prefix='!',
                   help_command=commands.DefaultHelpCommand(no_category='Commandes'))
tree = bot.tree
test_guild = discord.Object(id=TEST_GUILD_ID)
ecowatt_repository = EcoWattAPIRepository()


@bot.event
async def on_ready() -> None:
    logging.info(f'{bot.user.name} est connecté dans les guildes suivantes :')
    for guild in bot.guilds:
        logging.info(f'|   - {guild.name}')
    # Lorsque l'on modifie les commandes, il faut les resynchroniser sur toutes les guildes. On ne le fait pas tout
    # le temps, car l'api est limitée
    # bot.tree.copy_global_to(guild=test_guild)
    # await tree.sync(guild=test_guild)
    # await tree.sync()
    repeated_task.start()  # Start the repeating task


@tasks.loop(hours=1)
async def repeated_task() -> None:
    if datetime.now().hour == 18:
        message: Optional[str] = None
        logging.info("Task started")
        try:
            signals: tuple[EcoWattDay] = ecowatt_repository.fetch_ecowatt_values()
            for signal in signals:
                if signal.value != EcoWattValue.GREEN and signal.day == (datetime.today() + timedelta(days=1)).date():
                    message: str = signal.pretty_print() + ' @everyone '
            guilds: Sequence[discord.Guild] = bot.guilds
            if message is not None:
                for guild in guilds:
                    await guild.system_channel.send(message)
                logging.info(f"Jour tendu trouvé, message envoyé à {len(guilds)} guildes :\n{message}")
        except HTTPError:
            logging.error("Erreur lors de la récupération des données")


ecowatt_group = app_commands.Group(name="ecowatt", description="Prévisions Ecowatt")


def _get_ecowatt_message_for_day(days_from_today: int) -> str:
    try:
        signals: tuple[EcoWattDay] = ecowatt_repository.fetch_ecowatt_values()
        message: Optional[str] = None
        for signal in signals:
            if signal.day == (datetime.today() + timedelta(days=days_from_today)).date():
                message = signal.pretty_print()
        return message
    except HTTPError:
        logging.error('Erreur lors de la récupération des données')
        return "😭 Quelque chose s'est mal passé, veuillez réessayer dans 15 minutes"


@ecowatt_group.command()
async def tomorrow(interaction) -> None:
    """Affiche les prévisions d'alerte Ecowatt pour demain"""
    message: str = _get_ecowatt_message_for_day(1)
    await interaction.response.send_message(f'{message}')


@ecowatt_group.command()
async def today(interaction) -> None:
    """Affiche les prévisions d'alerte Ecowatt pour aujourd'hui"""
    message: str = _get_ecowatt_message_for_day(0)
    await interaction.response.send_message(f'{message}')


@tree.command()
async def invite(interaction) -> None:
    """Affiche le lien d'invitation du bot"""
    await interaction.response.send_message(f"Le lien d'invitation du bot est : {invite_link}")


bot.tree.add_command(ecowatt_group)
bot.run(TOKEN)
