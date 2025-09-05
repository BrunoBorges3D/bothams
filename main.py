import discord
import os

# Create intents with only non-privileged intents
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

def load_cogs():
    # Loading the cogs like this kinda better O.O
    [bot.load_extension(f"cogs.{folder}.__init__") for folder in os.listdir("cogs") if not "." in folder]

load_cogs()

bot.run("MTMyNzI1OTE0NzIwODc1NzI4OA.GDyTSj.k1NBlst6gadubnfbiTYWvIYTxvcJMZQJAFQ8FM")
