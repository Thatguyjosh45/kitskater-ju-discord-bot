import discord
from discord.ext import commands
import random

# Replace 'YOUR_BOT_TOKEN' with your bot token
TOKEN = 'YOUR_BOT_TOKEN'

# Set command prefix
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}! Bot is ready.')

# Moderation commands
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'User {member} has been banned.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'User {user} has been unbanned.')
            return

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'{amount} messages have been cleared.', delete_after=5)

# Fun commands
@bot.command()
async def roll(ctx, sides: int = 6):
    result = random.randint(1, sides)
    await ctx.send(f'🎲 You rolled a {result}!')

@bot.command()
async def meme(ctx):
    memes = [
        "https://i.imgur.com/W3duR07.png",  # Example meme URLs
        "https://i.imgur.com/5KX04Fk.jpg",
        "https://i.imgur.com/qlA5hZt.png"
    ]
    await ctx.send(random.choice(memes))

@bot.command()
async def greet(ctx):
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
