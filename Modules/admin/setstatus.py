from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)
from discord.ext import commands
from discord.commands import option
import discord
import json
import os


class setstatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[json.load(open("config.json"))["AdminGuild"]], name="setstatus", description="set the status of the bot")  # Create a slash command for the supplied guilds.
    @option(
        "type",
        description="Select the type of status you want to set the bot to.",
        autocomplete=discord.utils.basic_autocomplete(["Playing", "Listening", "Watching"]),
        # Demonstrates passing a static iterable discord.utils.basic_autocomplete
    )
    async def _setstatus(self, interaction: discord.Interaction, type: str, status: str):
        # if bot owner
        if interaction.author.id == json.load(open("config.json"))["BotOwner"]:
            await interaction.response.defer(ephemeral=True)
            statusdict = {"botstatus": {"status": status, "type": type}}
            await interaction.bot.database.botinfo.update_one({"_botid": interaction.bot.user.id}, {"$set": statusdict}, upsert=True)
            statusdb = await interaction.bot.database.botinfo.find_one({"_botid": interaction.bot.user.id})
            await interaction.bot.change_presence(activity=discord.Activity(name=statusdb["botstatus"]["status"], type=discord.ActivityType.listening if statusdb["botstatus"]["type"] == "Listening" else (discord.ActivityType.watching if statusdb["botstatus"]["type"] == "Watching" else discord.ActivityType.playing))) # Write the data to the db, making sure to set upsert to True incase the guild ID is not in the DB
            embed=discord.Embed(title="Status Updated", colour=0x91ccec)
            embed.set_image(url=f"attachment://MemberListUser.png")
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("_ _", delete_after=1)

def setup(bot):
    bot.add_cog(setstatus(bot))