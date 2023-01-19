import discord
import config
import traceback

from typing import Literal, Optional
from config import DB
from discord.ext import commands, tasks

THIS_GUILD = discord.Object(id=950937956682698861)


class FeedBackModal(discord.ui.Modal, title="Give Feedback"):
    crystal = discord.ui.TextInput(
        label="Discord Name",
        placeholder="(Please exclude the identifier after your username.)"
    )

    comment = discord.ui.TextInput(
        label="Comment?",
        placeholder="What are you suggesting?"
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your feedback, {self.crystal.value}!', ephemeral=True)
    
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)

class FeedBackButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Show Feedback Form", style=discord.ButtonStyle.green, custom_id="feedbackpersist:green")
    async def show_feedback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.send_modal(FeedBackModal())

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cur = DB.cursor(buffered=True)
        self.db_reconnect.start()
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        insert = "INSERT INTO viewed (user, value) values (%s, %s)"
        values = (member.name, 0)
        self.cur.execute(insert, values)
        DB.commit()

    @commands.command(name="sync")
    @commands.has_role('Citrusy Admin')
    async def sync(self, ctx):
        ctx.bot.tree.copy_global_to(guild=discord.Object(id=config.THIS_GUILD))
        await ctx.bot.tree.sync(guild=discord.Object(id=config.THIS_GUILD))
    
    @commands.hybrid_command(name="feedback")
    async def feedback(self, ctx):
        view = FeedBackButton()
        await ctx.send(view=view)
    
    @commands.hybrid_command(name="sync_db", description="Resyncs all users to the database.")
    @commands.has_role('Citrusy Admin')
    async def update_users_table(self, ctx):
        self.cur.execute("DELETE FROM `viewed` WHERE `value` = 0 or `value` = 1")
        DB.commit()

        for guild in self.bot.guilds:
            for member in guild.members:
                insert = "INSERT INTO viewed (user, value) values (%s, %s)"
                values = (member.name, 0)
                self.cur.execute(insert, values)
                DB.commit()
                
        await ctx.send('Database resynced.')

    
    @tasks.loop(hours=4)
    async def db_reconnect(self):
        await self.bot.wait_until_ready()
        DB.ping(True)
        print("Mysql connection reestablished.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
