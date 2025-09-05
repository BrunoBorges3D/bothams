"""
Embed Views file helper, contain all the embed views for VoiceFive other files

Embeds helper | Embeds.py

"""
import discord


class Embeds():
    """Class contains all the embed objects for VoiceFive"""
    class Panel(discord.Embed):
        """Discord Embed that will be called when a user create's a temp channel"""
        def __init__(self, member: discord.Member):
            super().__init__(title="Welcome!", color=discord.Color.blurple())
            self.add_field(
                name="Temp Channel Created",
                value=f"""
User {member.mention} has Created this temp channel
- Channel Owner Can Control Over Their Channel By The Following Select Menu's!
                """)

    class Info(discord.Embed):
        """Discord Embed can be called to display a temp channel info"""
        def __init__(self, interaction: discord.Interaction, channel: discord.VoiceChannel, channel_data):
            super().__init__(title='Channel Information', color=discord.Color.blurple())
            self.add_field(name="Channel Name", value=f"{channel.name}")
            self.add_field(name="Channel Creator", value=f"<@{channel_data[0]}>\nID: `{channel_data[0]}`")
            self.add_field(name="", value="", inline=False) # discord.Embed() ☕
            self.add_field(name="Created At", value=f"<t:{int(channel.created_at.timestamp())}:R>")
            self.add_field(name="Is NSFW", value=f"{'Nope' if not channel.is_nsfw() else 'Yup'}")
            self.add_field(name="", value="", inline=False)
            self.add_field(name="Channel bitrate", value=f"{int(channel.bitrate / 1000)}Kbps || {'Low Quality' if channel.bitrate < 60000 else 'Mid Quality' if channel.bitrate < 90000 else 'High Quality'}")
            self.add_field(name="Video Quality", value=f"{'Full Quality' if channel.video_quality_mode == discord.VideoQualityMode.full else 'Normal Quality'}")
            self.add_field(name="", value="", inline=False)
            self.add_field(name="User Limit", value=f"{'Unlimited' if channel.user_limit == 0 else channel.user_limit}")
            try: slowmode_delay = channel.slowmode_delay # For now, there is no attr for slowmode, hopefully my PR on #2112 get megred
            except: slowmode_delay = False
            self.add_field(name="Slowmode Delay", value=f"{'```Error: Cannot Get This Info, Later Could Be Patched```' if not slowmode_delay else 'No Slowmode' if slowmode_delay == 0 else slowmode_delay}")
            self.add_field(name="", value="", inline=False)
            self.add_field(name="Users Here", value=f"**`{list(map((lambda x: x.display_name), channel.members))}`**") # made this better by using a map() with lambda; no var
            self.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)


    class DeleteWarning(discord.Embed):
        """Discord Embed that will be used to warn the owner with wrong bot usage"""
        def __init__(self, user: discord.Member = None):
            super().__init__(title="Warning :warning:", color=discord.Color.red())
            self.add_field(name="Info", value=f"> User {user.mention} has deleted the temp channel parent!") if user else None
            self.add_field(
                name="Message",
                value=f"""
> Please resetup your server temp channels
- If you want to edit the channel's preferences you can just edit its name/prefrences or anything!
- Editing the channel's name/prefrences will make it's child's same is its parent.
- To change the temp channel category you can just place it at any category but **DO NOT** let it without category!
                """)

    class ClearWarning(discord.Embed):
        """Discord Embed that will be used to warn the temp channel owner for clearing the channel content"""
        def __init__(self):
            super().__init__(title="Warning :warning:", color=discord.Color.red())
            self.add_field(
                name="Message",
                value=f"""
> You Are About Deleting All Channel Messages, There No Way To Restore The Deleted Messages!
                """)

    class LogEmbed(discord.Embed):
        """Discord Embed untuk menampilkan log aktivitas voice channel"""
        def __init__(self, action_type: str, **kwargs):
            color_map = {
                "join": discord.Color.green(),
                "leave": discord.Color.red(),
                "update": discord.Color.blue(),
                "transfer": discord.Color.gold()
            }
            super().__init__(color=color_map.get(action_type, discord.Color.greyple()))
            
            if action_type == "join":
                self.description = f"🎙️ {kwargs.get('user').mention} joined the voice channel"
            
            elif action_type == "leave":
                self.description = f"🚪 {kwargs.get('user').mention} left the voice channel"
            
            elif action_type == "update":
                changes = []
                if kwargs.get('bitrate'):
                    changes.append(f"Bitrate: {kwargs.get('old_bitrate')/1000}kbps ➜ {kwargs.get('bitrate')/1000}kbps")
                if kwargs.get('user_limit') is not None:
                    old_limit = "unlimited" if kwargs.get('old_limit') == 0 else kwargs.get('old_limit')
                    new_limit = "unlimited" if kwargs.get('user_limit') == 0 else kwargs.get('user_limit')
                    changes.append(f"User Limit: {old_limit} ➜ {new_limit}")
                if kwargs.get('name'):
                    changes.append(f"Name: {kwargs.get('old_name')} ➜ {kwargs.get('name')}")
                
                self.description = f"⚙️ Channel settings updated by {kwargs.get('editor').mention}\n" + "\n".join(changes)
            
            elif action_type == "transfer":
                self.description = f"👑 Channel ownership transferred from {kwargs.get('old_owner').mention} to {kwargs.get('new_owner').mention}"
            
            self.set_footer(text=f"Time: {discord.utils.utcnow().strftime('%H:%M:%S')}")

    class TransferOnLeaveEmbed(discord.Embed):
        """Discord Embed untuk transfer ownership saat owner leave"""
        def __init__(self, owner: discord.Member):
            super().__init__(title="Transfer Ownership Required", color=discord.Color.yellow())
            self.description = f"""
🚨 {owner.mention} (Owner) has left the voice channel!
To keep this channel active, please select new owner using the button below.
Channel will be deleted in 5 minutes if no new owner is selected.
"""
