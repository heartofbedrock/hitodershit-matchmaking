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
groups = []  # List to store ongoing groups that are waiting to fill up

class JoinQueueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Matchmaking beitreten", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        # Check if the user is already in the waiting list
        if user in waiting_list:
            await interaction.response.send_message("Du bist bereits in der Warteschlange!", ephemeral=True)
            return

        # Defer the interaction response (gives bot time to process the matchmaking)
        await interaction.response.defer(ephemeral=True)

        # Add user to the waiting list
        waiting_list.append(user)

        # Send immediate response
        await interaction.followup.send(f"{user.mention}, du wurdest zur Warteschlange hinzugefügt!", ephemeral=True)

        # Check if we need to create a new group
        await manage_groups(interaction)

async def manage_groups(interaction):
    guild = interaction.guild

    # If there are enough users (at least 2), either fill existing groups or start a new one
    for group in groups:
        if len(group['members']) < 12:  # Check if this group is not full yet
            group_size_needed = 12 - len(group['members'])
            new_members = waiting_list[:group_size_needed]
            group['members'].extend(new_members)
            for member in new_members:
                waiting_list.remove(member)
                await member.add_roles(group['role'])
                await group['channel'].set_permissions(member, read_messages=True, send_messages=True)
            await group['channel'].send(f"{' '.join([member.mention for member in new_members])}, ihr wurdet der Gruppe hinzugefügt! ({len(group['members'])}/12)")
            # If group is now full, stop filling it
            if len(group['members']) == 12:
                await group['channel'].send(f"Die Gruppe ist jetzt voll! ({len(group['members'])}/12)")
            return

    # If no existing group needs members, start a new group with the first 2 players
    if len(waiting_list) >= 2:
        # Create a temporary role and channel for the group
        role = await guild.create_role(name="Deadlock Gruppe", mentionable=True)
        channel = await guild.create_text_channel(f"deadlock-gruppe-{random.randint(1000, 9999)}")

        # Add the first 2 users to the new group
        new_group = {
            'members': waiting_list[:2],
            'role': role,
            'channel': channel
        }

        groups.append(new_group)

        # Remove these 2 users from the waiting list
        for member in new_group['members']:
            waiting_list.remove(member)
            await member.add_roles(role)
            await channel.set_permissions(member, read_messages=True, send_messages=True)

        # Notify the group
        await channel.send(f"{role.mention}, ihr wurdet in einer neuen Gruppe für Deadlock platziert! ({len(new_group['members'])}/12)")
    return

class LeaveQueueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Matchmaking verlassen", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        # Check if the user is in the waiting list
        if user not in waiting_list:
            await interaction.response.send_message("Du bist nicht in der Warteschlange!", ephemeral=True)
            return

        # Defer the interaction response
        await interaction.response.defer(ephemeral=True)

        # Remove user from the waiting list
        waiting_list.remove(user)

        # Send immediate response
        await interaction.followup.send(f"{user.mention}, du wurdest aus der Warteschlange entfernt!", ephemeral=True)

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
