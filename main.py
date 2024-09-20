import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import os

intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix="!", intents=intents)

# List to store users waiting to be paired
waiting_list = []

class MatchmakingButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Join Matchmaking Queue", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        # Check if the user is already in the waiting list
        if user in waiting_list:
            await interaction.response.send_message("You are already in the queue!", ephemeral=True)
            return

        # Add user to the waiting list
        waiting_list.append(user)
        await interaction.response.send_message(f"{user.mention}, you have joined the matchmaking queue!", ephemeral=True)

        # If two or more users are in the queue, pair them
        if len(waiting_list) >= 2:
            # Randomly pair two users
            pair = random.sample(waiting_list, 2)
            waiting_list.remove(pair[0])
            waiting_list.remove(pair[1])

            # Notify the users they've been paired
            await interaction.followup.send(f"{pair[0].mention} and {pair[1].mention} have been paired!")

class MatchmakingView(View):
    def __init__(self):
        super().__init__()
        self.add_item(MatchmakingButton())

# Command to initiate the matchmaking process
@bot.command(name="matchmake")
async def matchmake(ctx):
    await ctx.send("Click the button to join the matchmaking queue!", view=MatchmakingView())

# Bot event when the bot is ready
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))
