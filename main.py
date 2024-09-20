import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # Required to manage channels and roles
intents.members = True  # Required to manage members

# Initialize the bot
bot = commands.Bot(command_prefix="/", intents=intents)

# List to store users waiting to be paired
waiting_list = []

class JoinQueueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Matchmaking beitreten", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        # Check if the user is already in the waiting list
        if user in waiting_list:
            await interaction.response.send_message("Du bist bereits in der Warteschlange!", ephemeral=True)
            return

        # Add user to the waiting list
        waiting_list.append(user)
        await interaction.response.send_message(f"{user.mention}, du wurdest zur Warteschlange hinzugefügt!", ephemeral=True)

        # If there are 12 users in the waiting list, create a group
        if len(waiting_list) >= 12:
            # Select 12 players from the queue
            group = random.sample(waiting_list, 12)

            # Remove the selected players from the waiting list
            for player in group:
                waiting_list.remove(player)

            # Create a temporary role and channel for the group
            guild = interaction.guild
            role = await guild.create_role(name="Deadlock Gruppe", mentionable=True)
            channel = await guild.create_text_channel(f"deadlock-gruppe-{random.randint(1000, 9999)}")

            # Add the role to each player and move them to the channel
            for player in group:
                await player.add_roles(role)
                await channel.set_permissions(player, read_messages=True, send_messages=True)
            
            # Notify the group
            await channel.send(f"{role.mention}, ihr wurdet in einer Gruppe für Deadlock platziert!")

class LeaveQueueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Matchmaking verlassen", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        # Check if the user is in the waiting list
        if user not in waiting_list:
            await interaction.response.send_message("Du bist nicht in der Warteschlange!", ephemeral=True)
            return

        # Remove user from the waiting list
        waiting_list.remove(user)
        await interaction.response.send_message(f"{user.mention}, du wurdest aus der Warteschlange entfernt!", ephemeral=True)

class MatchmakingView(View):
    def __init__(self):
        super().__init__()
        # Add both join and leave buttons
        self.add_item(JoinQueueButton())
        self.add_item(LeaveQueueButton())

# Command to initiate the matchmaking process
@bot.command(name="matchmake")
async def matchmake(ctx):
    await ctx.send("Klicke auf den Button, um der Matchmaking-Warteschlange beizutreten oder sie zu verlassen!", view=MatchmakingView())

# Bot event when the bot is ready
@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user}")

# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))
