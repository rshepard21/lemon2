import os
import discord

import config

from discord.ext import commands

THIS_GUILD = discord.Object(id=950937956682698862)

class Lemon(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!!", intents=discord.Intents.all())

    async def on_ready(self):
        print('Ready to begin my lemony day!')

    async def setup_hook(self) -> None:
        for f in os.listdir('./cogs'):
            if f.endswith('.py'):
                await self.load_extension(f'cogs.{f[:-3]}')

client = Lemon()
client.run(config.BOT_AUTH_CODE)