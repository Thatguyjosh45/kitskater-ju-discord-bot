import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
import random

# Replace 'YOUR_BOT_TOKEN' with your bot token
TOKEN = 'YOUR_BOT_TOKEN'

# Set command prefix (not used for slash commands)
bot = commands.Bot(command_prefix='|', intents=discord.Intents.all())

# Initialize SlashCommand
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}! Bot is ready.')

# Help command
@slash.slash(name="help", description="Displays a list of available commands.")
async def _help(ctx: SlashContext):
    help_message = """
    **Help Command**
    Here are the available commands:
    - `/help`: Displays this message.
    - `/kick <member> [reason]`: Kicks a member from the server.
    - `/ban <member> [reason]`: Bans a member from the server.
    - `/unban <member#discriminator>`: Unbans a member from the server.
    - `/clear <amount>`: Clears a specified number of messages.
    - `/roll [sides=6]`: Rolls a die with a specified number of sides (default is 6).
    - `/meme`: Sends a random meme.
    - `/greet`: Sends a random greeting.
    """
    await ctx.send(help_message)

# Moderation commands
@slash.slash(name="kick", description="Kicks a member from the server.")
@commands.has_permissions(kick_members=True)
async def _kick(ctx: SlashContext, member: discord.Member, reason: str = None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked.')

@slash.slash(name="ban", description="Bans a member from the server.")
@commands.has_permissions(ban_members=True)
async def _ban(ctx: SlashContext, member: discord.Member, reason: str = None):
    await member.ban(reason=reason)
    await ctx.send(f'User {member} has been banned.')

@slash.slash(name="unban", description="Unbans a member from the server.")
@commands.has_permissions(ban_members=True)
async def _unban(ctx: SlashContext, member: str):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'User {user} has been unbanned.')
            return

@slash.slash(name="clear", description="Clears a specified number of messages.")
@commands.has_permissions(manage_messages=True)
async def _clear(ctx: SlashContext, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'{amount} messages have been cleared.', delete_after=5)

# Fun commands
@slash.slash(name="roll", description="Rolls a die with a specified number of sides.")
async def _roll(ctx: SlashContext, sides: int = 6):
    result = random.randint(1, sides)
    await ctx.send(f'🎲 You rolled a {result}!')

@slash.slash(name="meme", description="Sends a random meme.")
async def _meme(ctx: SlashContext):
    memes = [
        "https://i.imgur.com/W3duR07.png",  # Example meme URLs
        "https://i.imgur.com/5KX04Fk.jpg",
        "https://i.imgur.com/qlA5hZt.png"
    ]
    await ctx.send(random.choice(memes))

@slash.slash(name="greet", description="Sends a random greeting.")
async def _greet(ctx: SlashContext):
    greetings = ["Hello!", "Hi there!", "Hey!", "Howdy!", "What's up?"]
    await ctx.send(random.choice(greetings))

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the necessary permissions to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You missed a required argument for this command.")
    else:
        await ctx.send("An error occurred. Please try again.")

# Run the bot
bot.run(TOKEN)
