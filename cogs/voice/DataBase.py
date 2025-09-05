"""
Database Quering Helper For VoiceFive Cog

DataBaseUtil | DataBase.py

DataBase Info:
    ╚voice.db
        ║
        ╠═ channels
        ║   ╠═ user_id 
        ║   ╠═ channel_id
        ║   ╚═ guild_id
        ║
        ╠═ guilds
        ║   ╠═ guild_id
        ║   ╠═ vc_id
        ║   ╠═ vc_category_id
        ║   ╠═ channel_limit
        ║   ╚═ channel_bitrate
        ║
        ╚═ rejected_users <- Unused

"""
import aiosqlite
import asyncio

DATABASE_FILE = 'voice.db'

COMMIT = 'commit'
FETCHONE = 'fetchone'
FETCHALL = 'fetchall'

class DataBase():
    """Pretty dumb `class` to handle the db calls"""
    def __init__(self):
        pass
    
    @classmethod
    async def create_conn(self):
        try:
            return await aiosqlite.connect(DATABASE_FILE)
        except Exception as e:
            print(f"Failed to connect to database: {str(e)}")
            raise e

    @classmethod
    async def execute(self, query: str, values: tuple, type: str):
        db = await self.create_conn()
        try:
            async with db.cursor() as cursor:
                await cursor.execute(query, values)
                if type == COMMIT:
                    await db.commit()
                    return True
                elif type == FETCHONE:
                    return await cursor.fetchone()
                else:
                    return await cursor.fetchall()
        except Exception as e:
            print(f"Database error: {str(e)}")
            raise e
        finally:
            await db.close()

    @classmethod
    async def get_guild(self, guild_id):
        return await self.execute(
            query='SELECT * FROM guilds WHERE guild_id = ?',
            values=(guild_id,),
            type=FETCHALL,
            )

    @classmethod
    async def create_channel(self, user_id, channel_id, guild_id, channel_name=None):
        try:
            return await self.execute(
                query="INSERT INTO channels (user_id, channel_id, guild_id, channel_name) VALUES (?,?,?,?)",
                values=(user_id, channel_id, guild_id, channel_name),
                type=COMMIT,
            )
        except Exception as e:
            print(f"Error creating channel: {e}")
            # Fallback to old structure if needed
            return await self.execute(
                query="INSERT INTO channels (user_id, channel_id, guild_id) VALUES (?,?,?)",
                values=(user_id, channel_id, guild_id),
                type=COMMIT,
            )

    @classmethod
    async def delete_channel(self, user_id, channel_id, guild_id):
        return await self.execute(
            query="DELETE FROM channels WHERE user_id = ? AND channel_id = ? AND guild_id = ?",
            values=(user_id, channel_id, guild_id),
            type=COMMIT,
            )

    @classmethod
    async def get_channel(self, user_id, channel_id, guild_id):
        query, values = ("SELECT * FROM channels WHERE channel_id = ? AND guild_id = ?", (channel_id, guild_id,)) if not user_id else ("SELECT * FROM channels WHERE user_id = ? AND channel_id = ? AND guild_id = ?", (user_id, channel_id, guild_id))
        return await self.execute(
            query=query,
            values=values,
            type=FETCHONE,
            )

    @classmethod
    async def get_rejected_user(self, user_id, channel_id, guild_id):
        return await self.execute(
            query="SELECT * FROM rejected_users WHERE user_id = ? AND channel_id = ? AND guild_id = ?",
            values=(user_id, channel_id, guild_id),
            type=FETCHONE,
            )

    @classmethod
    async def add_user_to_rejected(self, user_id, channel_id, guild_id):
        return await self.execute(
            query="INSERT INTO rejected_users VALUES (?,?,?)",
            values=(user_id, channel_id, guild_id),
            type=COMMIT,
            )

    @classmethod
    async def remove_user_from_reject(self, user_id, channel_id, guild_id):
        return await self.execute(
            query="DELETE FROM rejected_users WHERE user_id = ? AND channel_id = ? AND guild_id = ?",
            values=(user_id, channel_id, guild_id),
            type=COMMIT,
            )

    @classmethod
    async def add_guild(self, guild_id, vc_id, vc_category_id, channel_limit, channel_bitrate):
        return await self.execute(
            query="INSERT INTO guilds VALUES (?,?,?,?,?)",
            values=(guild_id, vc_id, vc_category_id, channel_limit, channel_bitrate),
            type=COMMIT,
            )

    @classmethod
    async def remove_guild(self, guild_id, vc_id):
        return await self.execute(
            query="DELETE FROM guilds WHERE guild_id = ? AND vc_id = ?",
            values=(guild_id, vc_id,),
            type=COMMIT,
            )

    @classmethod
    async def update_channel_name(self, user_id, channel_id, guild_id, channel_name):
        return await self.execute(
            query="UPDATE channels SET channel_name = ? WHERE user_id = ? AND channel_id = ? AND guild_id = ?",
            values=(channel_name, user_id, channel_id, guild_id),
            type=COMMIT,
        )

    @classmethod
    async def get_last_channel_name(self, user_id, guild_id):
        try:
            result = await self.execute(
                query="SELECT channel_name FROM channels WHERE user_id = ? AND guild_id = ? ORDER BY rowid DESC LIMIT 1",
                values=(user_id, guild_id),
                type=FETCHONE,
            )
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting last channel name: {e}")
            return None

    @classmethod
    async def save_last_channel_name(self, user_id, guild_id, channel_name):
        """Save the last channel name for a user"""
        try:
            # First delete any existing saved name
            await self.execute(
                query="DELETE FROM last_channel_names WHERE user_id = ? AND guild_id = ?",
                values=(user_id, guild_id),
                type=COMMIT
            )
            # Wait a bit to ensure the delete is complete
            await asyncio.sleep(0.1)
            
            # Then insert the new one
            return await self.execute(
                query="INSERT INTO last_channel_names (user_id, guild_id, channel_name) VALUES (?,?,?)",
                values=(user_id, guild_id, channel_name),
                type=COMMIT
            )
        except Exception as e:
            print(f"Error saving last channel name: {e}")
            # Try one more time after a short delay
            try:
                await asyncio.sleep(0.5)
                await self.execute(
                    query="INSERT INTO last_channel_names (user_id, guild_id, channel_name) VALUES (?,?,?)",
                    values=(user_id, guild_id, channel_name),
                    type=COMMIT
                )
            except Exception as e2:
                print(f"Second attempt failed: {e2}")
            return None

    @classmethod
    async def get_saved_channel_name(self, user_id, guild_id):
        """Get the saved channel name for a user"""
        try:
            result = await self.execute(
                query="SELECT channel_name FROM last_channel_names WHERE user_id = ? AND guild_id = ?",
                values=(user_id, guild_id),
                type=FETCHONE
            )
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting saved channel name: {e}")
            return None
