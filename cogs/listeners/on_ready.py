import discord
import aiosqlite
import os
from colorama import Fore
from prettytable import PrettyTable

database_file = 'voice.db'

# Drop and recreate tables
querys = [
"""
DROP TABLE IF EXISTS channels;
""",
"""
DROP TABLE IF EXISTS guilds;
""",
"""
DROP TABLE IF EXISTS rejected_users;
""",
"""
CREATE TABLE IF NOT EXISTS channels (
    user_id INTEGER,
    channel_id INTEGER,
    guild_id INTEGER,
    channel_name TEXT
);
""",
"""
CREATE TABLE IF NOT EXISTS guilds (
    guild_id INTEGER,
    vc_id INTEGER,
    vc_category_id INTEGER,
    channel_limit INTEGER,
    channel_bitrate INTEGER
);
""",
"""
CREATE TABLE IF NOT EXISTS rejected_users (
    user_id INTEGER,
    channel_id INTEGER,
    guild_id INTEGER
);
""",
"""
CREATE TABLE IF NOT EXISTS last_channel_names (
    user_id INTEGER,
    guild_id INTEGER,
    channel_name TEXT,
    PRIMARY KEY (user_id, guild_id)
);
"""]

class ReadyListener(discord.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @discord.Cog.listener()
    async def on_ready(self):
        # Delete existing database if exists
        if os.path.exists(database_file):
            os.remove(database_file)
            
        async with aiosqlite.connect(database_file) as conn:
            for query in querys:
                try:
                    async with conn.execute(query) as cursor:
                        await conn.commit()
                except Exception as e:
                    print(f"Query error: {e}")
                    continue
                    
        guilds_count = len(self.bot.guilds)
        bot_data = await self.bot.application_info()
        owner: discord.User = bot_data.owner
        table = PrettyTable()
        table.field_names = ["Bot User", "Bot ID", "Owner User", "Owner ID", "Guild Count"]
        table.add_row([f"{self.bot.user}", f"{self.bot.user.id}", f"{owner}", f"{owner.id}", f"{guilds_count}"])
        print(Fore.CYAN, table)
        print("Logged In Successfully")
        
def setup(bot: discord.Bot):
    bot.add_cog(ReadyListener(bot))
        
    