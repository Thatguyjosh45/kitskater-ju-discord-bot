import random
import discord # type: ignore
from discord.ext import commands # type: ignore
import asyncio

intents = discord.Intents.default()
intents.members = True  # Enable member intents

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f"Logged in as {bot.user}")

# Add moderation commands here
@bot.tree.command(name="kick", description="Kick a member from the server.")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member} has been kicked. Reason: {reason}")

@bot.tree.command(name="ban", description="Ban a member from the server.")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member} has been banned. Reason: {reason}")


@bot.tree.command(name="unban", description="Unban a user by their username and discriminator.")
async def unban(interaction: discord.Interaction, username: str, discriminator: str):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    banned_users = await interaction.guild.bans()
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (username, discriminator):
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"Unbanned {user.name}#{user.discriminator}.")
            return

    await interaction.response.send_message("User not found in the ban list.", ephemeral=True)

@bot.tree.command(name="timeout", description="Put a user in timeout for a specified duration.")
async def timeout(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    try:
        # Duration is in seconds
        await member.timeout(duration=duration, reason=reason)
        await interaction.response.send_message(f"{member.mention} has been put in timeout for {duration} seconds. Reason: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to timeout {member.mention}: {str(e)}")

@bot.tree.command(name="clear", description="Delete a specific number of messages in this channel.")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    if amount < 1 or amount > 100:
        await interaction.response.send_message("You can delete between 1 and 100 messages at a time.", ephemeral=True)
        return

    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"Deleted {len(deleted)} messages.", ephemeral=True)

@bot.tree.command(name="lock", description="Lock this channel, preventing users from sending messages.")
async def lock_channel(interaction: discord.Interaction, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"🔒 This channel has been locked. Reason: {reason}")

@bot.tree.command(name="unlock", description="Unlock this channel, allowing users to send messages.")
async def unlock_channel(interaction: discord.Interaction, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = True
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"🔓 This channel has been unlocked. Reason: {reason}")

warnings = {}  # Dictionary to track user warnings

@bot.tree.command(name="warn", description="Warn a user for inappropriate behavior.")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    if member.id not in warnings:
        warnings[member.id] = []
    warnings[member.id].append(reason)

    await interaction.response.send_message(f"⚠️ {member.mention} has been warned. Reason: {reason}")

@bot.tree.command(name="warnings", description="View warnings for a specific user.")
async def view_warnings(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    user_warnings = warnings.get(member.id, [])
    if not user_warnings:
        await interaction.response.send_message(f"{member.mention} has no warnings.")
    else:
        await interaction.response.send_message(
            f"⚠️ {member.mention} has the following warnings:\n" +
            "\n".join([f"{idx + 1}. {warning}" for idx, warning in enumerate(user_warnings)])
        )

@bot.tree.command(name="addrole", description="Add a role to a user.")
async def add_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    await member.add_roles(role)
    await interaction.response.send_message(f"✅ {role.name} has been added to {member.mention}.")

@bot.tree.command(name="removerole", description="Remove a role from a user.")
async def remove_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    await member.remove_roles(role)
    await interaction.response.send_message(f"✅ {role.name} has been removed from {member.mention}.")

@bot.tree.command(name="serverinfo", description="Get information about the server.")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title="Server Information", color=discord.Color.blue())
    embed.add_field(name="Server Name", value=guild.name, inline=False)
    embed.add_field(name="Owner", value=guild.owner, inline=False)
    embed.add_field(name="Member Count", value=guild.member_count, inline=False)
    embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d"), inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="banlist", description="View the list of banned users.")
async def ban_list(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    bans = await interaction.guild.bans()
    if not bans:
        await interaction.response.send_message("There are no banned users in this server.")
    else:
        banned_users = "\n".join([f"{ban.user.name}#{ban.user.discriminator}" for ban in bans])
        await interaction.response.send_message(f"🚫 Banned Users:\n{banned_users}")


@bot.tree.command(name="mute", description="Mute a member in the server.")
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not muted_role:
        await interaction.response.send_message("Muted role not found. Please create one.", ephemeral=True)
        return

    await member.add_roles(muted_role, reason=reason)
    await interaction.response.send_message(f"{member} has been muted for {duration} minutes. Reason: {reason}")

    # Remove the role after the duration (in seconds)
    await asyncio.sleep(duration * 60)
    await member.remove_roles(muted_role, reason="Mute duration expired")
    
#fun commeds 
jokes = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why was the math book sad? It had too many problems.",
    "Why can't you give Elsa a balloon? Because she will let it go!"
]

@bot.tree.command(name="joke", description="Get a random joke!")
async def tell_joke(interaction: discord.Interaction):
    await interaction.response.send_message(f"😂 {random.choice(jokes)}")
@bot.tree.command(name="flip", description="Flip a coin!")
async def flip_coin(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🪙 The coin landed on: {result}")
compliments = [
    "You're an amazing person!", 
    "You light up the room!", 
    "You have a great sense of humor!"
]

@bot.tree.command(name="compliment", description="Get a random compliment!")
async def compliment(interaction: discord.Interaction, user: discord.Member = None):
    target = user.mention if user else "You"
    await interaction.response.send_message(f"🌟 {target}, {random.choice(compliments)}")
@bot.tree.command(name="meme", description="Get a random meme!")
async def meme(interaction: discord.Interaction):
    memes = [
        "https://i.imgur.com/j9pZCsK.jpg", 
        "https://i.imgur.com/w3duR07.png",
        "https://i.imgur.com/yhFNOhU.jpg"
    ]
    await interaction.response.send_message(random.choice(memes))
@bot.tree.command(name="random", description="Generate a random number.")
async def random_number(interaction: discord.Interaction, start: int, end: int):
    if start >= end:
        await interaction.response.send_message("Start value must be less than the end value!", ephemeral=True)
        return

    number = random.randint(start, end)
    await interaction.response.send_message(f"🎲 Your random number is: {number}")
gifs = [
    "https://media.giphy.com/media/3o6ZsYm5Gdm9TBH3O0/giphy.gif",
    "https://media.giphy.com/media/l2QE6NSBqFGhJ8kn6/giphy.gif",
    "https://media.giphy.com/media/xUPGcEliCc7bETyfO8/giphy.gif"
]

@bot.tree.command(name="gif", description="Send a random GIF!")
async def random_gif(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(gifs))
roasts = [
    "You're like a cloud. When you disappear, it’s a beautiful day.",
    "You're proof that even garbage can have opinions.",
    "You bring everyone so much joy... when you leave the room."
]

@bot.tree.command(name="roast", description="Roast someone (for fun!).")
async def roast(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"🔥 {user.mention}, {random.choice(roasts)}")
@bot.tree.command(name="hug", description="Send a virtual hug to someone.")
async def hug(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"🤗 {interaction.user.mention} sends a warm hug to {user.mention}!")
@bot.tree.command(name="rps", description="Play Rock, Paper, Scissors with the bot!")
async def rps(interaction: discord.Interaction, choice: str):
    valid_choices = ["rock", "paper", "scissors"]
    if choice.lower() not in valid_choices:
        await interaction.response.send_message("Invalid choice! Choose rock, paper, or scissors.", ephemeral=True)
        return

    bot_choice = random.choice(valid_choices)
    if choice.lower() == bot_choice:
        result = "It's a tie!"
    elif (choice.lower() == "rock" and bot_choice == "scissors") or \
         (choice.lower() == "paper" and bot_choice == "rock") or \
         (choice.lower() == "scissors" and bot_choice == "paper"):
        result = "You win!"
    else:
        result = "I win!"

    await interaction.response.send_message(f"You chose {choice.capitalize()}, I chose {bot_choice.capitalize()}.\n{result}")

bot.run("YOUR_BOT_TOKEN")

