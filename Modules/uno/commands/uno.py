from platform import python_build, python_version
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)
from discord.ext import commands
from discord.ui import View, Button
import discord
import json
from Modules.uno.handlers.core import Game, Player
import os

decks = []

for i in list(os.walk("Modules/uno/decks"))[0][1]:
    # if the folder contains a manifest.json
    if "manifest.json" in list(os.walk(f"Modules/uno/decks/{i}"))[0][2]:
        # add the deck to the list of decks
        decks.append(i)





class uno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # slash group
    @slash_command(guild_ids=[json.load(open("config.json"))["Guild"]] if json.load(open("config.json"))["Guild"] != "Global" else None, name="uno", description="Play uno with up to 8 players.")  # Create a slash command for the supplied guilds.
    async def _uno(self, interaction: discord.Interaction):
        await interaction.response.defer()

        users = []
        users.append(interaction.user)

        def gamelobby(deck = json.load(open(f"Modules/uno/decks/Default/manifest.json", encoding='utf-8')), deckfile = "Default"):

            embed=discord.Embed(title="Uno Game Lobby", colour=0xffffff)
            embed.add_field(name="Players", value=str("`👑` `" if len(users) > 0 else "`❌` `") + "\n`👤` `".join([str(user.display_name + "#" + user.discriminator + "`") for user in users] if len(users) > 0 else ["No players`"]), inline=False)
            embed.add_field(name="Using Deck", value=str("`" + str(deck["emoji"] + "` `") + str(str(deck["name"]) + "`\n**Author**: `" + deck["author"] + "`")) if deck != "Default" else "Default Deck", inline=False)
            embed.set_footer(text="players: {}/8".format(len(users)))
            # get deck logo from deckfile/icon.png
            logo = discord.File(f"Modules/uno/decks/{deckfile}/icon.png", filename="icon.png")
            embed.set_thumbnail(url="attachment://icon.png")

            return embed, logo

        class gameButtons(View):
            def __init__(self, timeout=120):
                super().__init__(timeout=timeout)
                
                self.deck = json.load(open(f"Modules/uno/decks/Default/manifest.json", encoding='utf-8'))
                self.deckfile = "Default"

            @discord.ui.select(placeholder="Select A Deck", min_values=1, max_values=1, options=[discord.SelectOption(label=json.load(open(f"Modules/uno/decks/{deck}/manifest.json", encoding='utf-8'))["name"], emoji=json.load(open(f"Modules/uno/decks/{deck}/manifest.json", encoding='utf-8'))["emoji"], default=False, value=deck) for deck in decks])
            async def rating_callback(self, select, interaction):
                await interaction.response.defer()
                self.deck = json.load(open(f"Modules/uno/decks/{select.values[0]}/manifest.json", encoding='utf-8'))
                self.deckfile = select.values[0]
                embed, logo = gamelobby(deck = self.deck, deckfile = self.deckfile)
                await ui.edit(embed=embed, files=[logo])

            @discord.ui.button(label="Join Game", style=discord.ButtonStyle.green)
            async def join(self, button: discord.ui.Button, interaction: discord.Interaction):
                await interaction.response.defer(ephemeral=True)
                if interaction.user not in users:
                    # if users is at max size
                    if len(users) == 8:
                        await interaction.followup.send("The game is full.", ephemeral=True)
                        return

                    users.append(interaction.user)
                    # add to users list on embed
                    embed, logo = gamelobby(deck = self.deck, deckfile = self.deckfile)
                    await ui.edit(embed=embed, files=[logo])
                    await interaction.followup.send("You have joined the game.", ephemeral=True)
                else:
                    # leave game
                    users.remove(interaction.user)
                    # remove from users list on embed
                    embed, logo = gamelobby(deck = self.deck, deckfile = self.deckfile)

                    await ui.edit(embed=embed, files=[logo])
                    await interaction.followup.send("You have left the game.", ephemeral=True)

            @discord.ui.button(label="Start", style=discord.ButtonStyle.blurple)
            async def start(self, button: discord.ui.Button, interaction: discord.Interaction):
                # if game leader (user at pos 0 in list)
                if interaction.user == users[0]:
                    # if there is only one player
                    await interaction.response.defer(ephemeral=True)
                    if len(users) == 1:
                        await interaction.followup.send("You can only play if you have friends...", ephemeral=True)
                        return
                    await interaction.followup.send("Game starting...", ephemeral=True)
                    for i in self.children:
                        i.disabled = True
                    await ui.edit(view=self)
                    # start game
                    players = []
                    for user in users:
                        players.append(Player(user))
                    game = Game(players, self.deckfile)
                    await game.start()
                else:
                    await interaction.response.send_message("You are not the game leader.", ephemeral=True)

            # on timeout
            async def on_timeout(self):
                for i in self.children:
                    i.disabled = True
                await ui.edit(view=self)


        embed, logo = gamelobby()
        # send
        ui = await interaction.followup.send(embed=embed, view=gameButtons(), file=logo, ephemeral=True)



def setup(bot):
    bot.add_cog(uno(bot))