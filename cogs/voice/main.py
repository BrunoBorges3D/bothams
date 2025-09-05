"""
VoiceFive, A Py-Cord Cog (Gear) Made to mange temp channels 

Main File | main.py
"""
import discord
import asyncio
from cogs.voice.Embeds import Embeds
from cogs.voice.Views import Views
from cogs.voice.DataBase import DataBase

db = DataBase()

# Change this for your own (IF YOU WANT)
DEFAULT_PERMISSIONS = discord.Permissions()
DEFAULT_PERMISSIONS.administrator = True

class Control(discord.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    temp_voice = discord.SlashCommandGroup(name="voice", description="To manage temp voice channels on your server", guild_only=True, default_member_permissions=DEFAULT_PERMISSIONS)
    @temp_voice.command(name="setup",description="To setup temp channels on your server", guild_only=True)
    async def setup(self, ctx: discord.ApplicationContext):
        await ctx.response.defer()
        if isinstance(ctx.channel, discord.DMChannel):
            return await ctx.respond("You can't setup temp channels in DMs!")
        category = await ctx.guild.create_category(name="Temp Voice")
        channel = await category.create_voice_channel(name="Join To Create")
        await db.add_guild(guild_id=ctx.guild.id, vc_id=channel.id, vc_category_id=category.id, channel_limit=0, channel_bitrate=3,)
        return await ctx.respond(f"Done setup the temp voice channel, this is the {channel.mention}!")

    # -- Events -- #

    @discord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Views.Dropdown())
        print("[🔵] Loadded Presistent View")

    @discord.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """This Function is called when a member joins or leaves a voice channel"""
        try:
            guild_settings = await db.get_guild(member.guild.id)
            before_channel = before.channel
            after_channel = after.channel
            
            if before_channel == after_channel:
                return
            
            # Log when member leaves any voice channel
            if before_channel:
                channel_data = await db.get_channel(None, before_channel.id, member.guild.id)
                if channel_data:  # If this is a temp channel
                    if channel_data[0] == member.id:  # If member is owner
                        # Check if there are other members in the channel
                        if len(before_channel.members) > 0:
                            try:
                                # Send transfer ownership embed
                                transfer_embed = Embeds.TransferOnLeaveEmbed(owner=member)
                                transfer_view = Views.TransferOnLeave(
                                    owner=member,
                                    channel_id=before_channel.id,
                                    guild_id=member.guild.id
                                )
                                await before_channel.send(
                                    embed=transfer_embed,
                                    view=transfer_view,
                                    allowed_mentions=discord.AllowedMentions.none()
                                )
                                
                                # Log leaving
                                log_embed = Embeds.LogEmbed("leave", user=member)
                                await before_channel.send(
                                    embed=log_embed,
                                    allowed_mentions=discord.AllowedMentions.none()
                                )
                                
                                # Save channel name
                                await db.save_last_channel_name(member.id, member.guild.id, before_channel.name)
                                return  # Don't delete channel yet
                            except:
                                pass
                        
                        # If no other members or failed to send transfer embed
                        try:
                            log_embed = Embeds.LogEmbed("leave", user=member)
                            await before_channel.send(
                                embed=log_embed,
                                allowed_mentions=discord.AllowedMentions.none()
                            )
                        except:
                            pass
                            
                        # Save the current channel name before deleting
                        await db.save_last_channel_name(member.id, member.guild.id, before_channel.name)
                        await db.delete_channel(member.id, before_channel.id, member.guild.id)
                        await before_channel.delete()
                    else:  # If member is not owner, just log the leave
                        try:
                            log_embed = Embeds.LogEmbed("leave", user=member)
                            await before_channel.send(
                                embed=log_embed,
                                allowed_mentions=discord.AllowedMentions.none()
                            )
                        except:
                            pass
            
            # Log when member joins/creates channel
            if after_channel:
                if after_channel.id in map((lambda x: x[1] if x else []), guild_settings):
                    # This is the "Join to Create" channel
                    saved_name = await db.get_saved_channel_name(member.id, member.guild.id)
                    channel_name = saved_name if saved_name else f"{member.display_name}'s Voice"
                    
                    temp_channel = await after_channel.clone(name=channel_name)
                    await member.move_to(temp_channel)
                    await db.create_channel(member.id, temp_channel.id, member.guild.id, channel_name)
                    
                    # Send welcome embed
                    embed = Embeds.Panel(member=member)
                    await temp_channel.send(embed=embed, view=Views.Dropdown())
                    
                    # Send join log
                    log_embed = Embeds.LogEmbed("join", user=member)
                    await temp_channel.send(embed=log_embed, allowed_mentions=discord.AllowedMentions.none())
                else:
                    # Check if joining existing temp channel
                    channel_data = await db.get_channel(None, after_channel.id, member.guild.id)
                    if channel_data:  # If this is a temp channel
                        try:
                            log_embed = Embeds.LogEmbed("join", user=member)
                            await after_channel.send(embed=log_embed, allowed_mentions=discord.AllowedMentions.none())
                        except:
                            pass
                            
        except Exception as e:
            print(f"Error in voice state update: {str(e)}")

    @discord.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        if not isinstance(before, discord.VoiceChannel):
            return
            
        channel_data = await db.get_channel(None, before.id, before.guild.id)
        if not channel_data:
            return
            
        changes = {}
        if before.bitrate != after.bitrate:
            changes.update({'bitrate': after.bitrate, 'old_bitrate': before.bitrate})
        if before.user_limit != after.user_limit:
            changes.update({'user_limit': after.user_limit, 'old_limit': before.user_limit})
        if before.name != after.name:
            changes.update({'name': after.name, 'old_name': before.name})
            
        if changes:
            try:
                async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update):
                    editor = entry.user
                    break
                else:
                    editor = after.guild.me
                    
                log_embed = Embeds.LogEmbed("update", editor=editor, **changes)
                await after.send(embed=log_embed, allowed_mentions=discord.AllowedMentions.none())
            except Exception as e:
                print(f"Error sending update log: {str(e)}")

    @discord.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if not channel.id in map((lambda x: x[1] if x else []), (await db.get_guild(channel.guild.id))):
            return
        return await db.remove_guild(channel.guild.id, channel.id)
    
    @discord.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        if not guild.id in map((lambda x: x[0] if x else []), (await db.get_guild(guild.id))):
            return
        return await asyncio.gather(*(db.remove_guild(guild.id, channel_id) for channel_id in map(lambda x: x[1] if x else [], await db.get_guild(guild.id))))
        #            ~~^~~ goodluck understanding what's going on :3

# - Do You know What Girl Called "Lisa"?
# - No!

def setup(bot: discord.Bot):
    bot.add_cog(Control(bot))
