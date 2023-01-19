import config
import discord

from config import DB
from discord import app_commands
from discord.ext import commands, tasks

class CrystalNotification(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cur = DB.cursor()

    @discord.ui.button(label="View Crystal", style=discord.ButtonStyle.blurple, custom_id="crystalpersist:green")
    async def show_crystal(self, interaction: discord.Interaction, button: discord.Button):
        self.cur.execute('select * from crystals order by RAND() limit 1')
        for type, description in self.cur.fetchall():
            self.cur.execute('select * from viewed')
            for user, value in self.cur.fetchall():
                if user == interaction.user.name and value == True:
                    await interaction.response.send_message("Please wait till tomorrow to use this feature.", ephemeral=True)
                elif user == interaction.user.name and value == False:
                    embed = discord.Embed(color=0xFAFA33)
                    embed.add_field(name="Crystal", value=type, inline=False)
                    embed.add_field(name="What it does", value=description, inline=False)
                    update = "UPDATE viewed SET value = 1 WHERE user = '{0}'".format(interaction.user.name)
                    self.cur.execute(update)
                    DB.commit()
                    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Button, /) -> None:
        # We don't need to know if the action has already been responded to.
        return

class Crystals(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__()
        self.crystal.start()
        self.cur = DB.cursor()

    @tasks.loop(hours=24)
    async def crystal(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(950937956682698862)
        channel = self.bot.get_channel(config.CRYSTAL_CHANNEL)
        async for m in channel.history(limit=1):
            if m:
                await m.delete()
                
                for u in guild.members:
                    update = "UPDATE viewed SET value = '{0}' WHERE user = '{1}'".format(0, u.name)
                    self.cur.execute(update)
                    print(self.cur.fetchall())
                    DB.commit()

                await channel.send("The crystal of the day is ready!", view=CrystalNotification())

async def setup(bot: commands.Bot):
    await bot.add_cog(Crystals(bot), guild=discord.Object(id=950937956682698862))
