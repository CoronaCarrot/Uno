# Imports
import asyncio
import traceback
import discord
from discord.ext import commands
import json
import os
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
import glob
import os
from datetime import datetime
from termcolor import colored

import sys

class Log(object):
    def __init__(self):
        self.orgstdout = sys.stdout

        if not os.path.exists("Logs"):
            os.mkdir("Logs")
        if not os.path.exists("Logs/latest.log"):
            open("Logs/latest.log", "w").close()

        # append latest.log to DD-MM-YYYY.log
        with open("Logs/latest.log", "r", encoding="utf-8") as f:
            with open("Logs/{}.log".format(datetime.now().strftime("%d-%m-%Y")), "a", encoding="utf-8") as f2:
                f2.write(f.read())
                f.close()
                f2.close()
        # clear latest.log
        with open("Logs/latest.log", "w", encoding="utf-8") as f:
            f.write("")
            f.close()
        # open latest.log
        self.log = open("Logs/latest.log", "a", encoding="utf-8")

    def write(self, msg):
        self.orgstdout.write(msg)
        self.log.write(msg)  
        self.log.close()
        self.log = open("Logs/latest.log", "a", encoding="utf-8")




    def flush(self):
        pass

sys.stdout = Log()
# log errors
sys.excepthook = lambda *args: print("".join(traceback.format_exception(*args)))

config_exists = os.path.exists('config.json')

if config_exists:
    pass
else:
    createconfig = open("config.json", "w")
    json.dump(
        {
            "botToken": "BotToken",
            "BotOwner": 646069031014760448,
            "AdminGuild": 983116313444634665,
            "Guild": 983116313444634665,
            "DevelopmentMode": False,
            "database": {
                "uri": False,
                "mongoUsername": "MongoUsername",
                "mongoPassword": "MongoPassword",
                "mongoHost": "MongoHost",
                "mongoPort": "MongoPort",
                "mongoDatabase": "MongoDatabase"
            },
            "Version": "1.0.0"
        },
        createconfig,
    indent=4,
    )
    createconfig.close()

    
url = ""
# Handle mongodb connection
class MongoConnection:
    def __init__(self, bot, config):

        def generate_url():
            credentials = config["database"]
            global url
            url = "mongodb+srv://{username}:{password}@{host}/{database}".format(
                username=credentials["mongoUsername"],
                password=credentials["mongoPassword"],
                host=credentials["mongoHost"],
                port=credentials["mongoPort"],
                database=credentials["mongoDatabase"],
            ) if credentials["uri"] else "mongodb://{username}:{password}@{host}:{port}/{database}".format(
                username=credentials["mongoUsername"],
                password=credentials["mongoPassword"],
                host=credentials["mongoHost"],
                port=credentials["mongoPort"],
                database=credentials["mongoDatabase"],
            )
            url += "?authSource=admin&retryWrites=true&w=majority"
            
            return url
        

        self.bot = bot
        self.client = AsyncIOMotorClient(generate_url()) # Mongo connection client
        self.db = self.client[config['database']["mongoDatabase"]] # The actual mongo database we will be adding stuff to
        self.botinfo = self.db.botinfo # Mongo levels collection
        self.servers = self.db.servers
        self.users = self.db.users


# Bot subclass
class GameBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=["<@986352022401994762>", "<@!986352022401994762>", "!"], intents=discord.Intents.all())
        configfile = open("config.json")
        load = json.load(configfile)
        self.uptime = discord.utils.utcnow()
        self.database = MongoConnection(self, load)
        print(colored("[?] ", "cyan") + "Connected to Database")
        self.config = json.load(open("config.json"))

        #await self.load_extension("jishaku") # for debugging
        # custom cog loader that took fucking years to perfect
        for filename in glob.iglob("Modules/**", recursive=True):
            if filename.endswith(".py"):
                try:
                    file = os.path.basename(filename)
                    fn = filename.replace('/', '.').replace('\\', '.').replace(f'.{file}','')
                    cog = f"{fn}.{file.replace('.py', '')}"
                    self.load_extension(cog)
                
                
                except Exception as e:
                    print(colored("[!] ", "red") + "Failed to load {}\n\n{}".format(cog, e.with_traceback(traceback.print_exc())))
        print(colored("[?] ", "cyan") + "Loaded {} cogs".format(len(self.cogs)))

    async def on_ready(self):
    
        a = open("config.json")
        # config should be file name, () gotta be var above
        configjson = json.load(a)
        # closing the file to prevent json corruption from leaving the file open
        a.close()
    
        status = await bot.database.botinfo.find_one({"_botid": bot.user.id})
        if not status:
            statusdict = {"botstatus": {"status": "Edit this with /setstatus", "type": "Playing"}}
            await bot.database.botinfo.update_one({"_botid": bot.user.id}, {"$set": statusdict}, upsert=True) # Write the data to the db, making sure to set upsert to True incase the guild ID is not in the DB
        status = status
        await bot.change_presence(activity=discord.Activity(name=status["botstatus"]["status"], type=discord.ActivityType.listening if status["botstatus"]["type"] == "Listening" else discord.ActivityType.watching if status["botstatus"]["type"] == "Watching" else discord.ActivityType.playing))
        # datetime object containing current date and time for uptime
        uptimeutc = datetime.utcnow()
        uptime = uptimeutc.timestamp()
        await bot.database.botinfo.update_one({"_botid": bot.user.id}, {"$set": {"uptime": uptime}}, upsert=True)

        await asyncio.sleep(1)
        print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
        print("┃ " + colored("● Database Details:", "blue"))
        print("┃   " + colored("⁃ Host: ", "yellow") +  configjson["database"]["mongoHost"] + ":" + configjson["database"]["mongoPort"])
        print("┃   " + colored("⁃ Username: ", "yellow") +  configjson["database"]["mongoUsername"])
        print("┃   " + colored("⁃ Database: ", "yellow") +  configjson["database"]["mongoDatabase"])
        print("┃   " + colored("⁃ URL: ", "yellow") + colored("hidden", "white", attrs=["concealed"]))
        print("┃ ")
        print("┃ " + colored("● Bot Details:", "blue"))
        print("┃   " + colored("⁃ Bot Username: ", "yellow") + bot.user.name + "(" + str(bot.user.id) + ")") 
        print("┃   " + colored("⁃ Bot Prefix: ", "yellow") + "Slash commands")
        print("┃   " + colored("⁃ Cogs Loaded: ", "yellow") + str(len(bot.cogs)))
        print("┃   " + colored("⁃ Bot Status: ", "yellow") + status["botstatus"]["type"] + " " + status["botstatus"]["status"])
        print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
        

    async def on_message(self, message):
        if message.author.bot == False and self.user.mentioned_in(message) and str(message.content).startswith(self.user.mention):
            embed = discord.Embed(description="My prefix is `/`\nyou can see my commands by typing `/` in chat", color=0xff3030)
            await message.reply(embed=embed, mention_author=False)

        else:
            await self.process_commands(message)



# Start the bot
bot = GameBot()
# making the file into a var, configjson can be anything
configjson = open("config.json")
# config should be file name, () gotta be var above
config = json.load(configjson)
# closing the file to prevent json corruption from leaving the file open
configjson.close()
#config = the var thats in config = json.load(configjson)
bot.run(config["botToken"])