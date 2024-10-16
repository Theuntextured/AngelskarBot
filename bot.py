import discord
from discord.ext import commands
import bot_settings
import os
import pytz
from datetime import datetime
import json
import capitals

IS_ADMIN_COMMAND = "admin_command"
months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
with open("country-by-capital-city.json") as json_file:
    json_data = json.load(json_file)

class Practice:
    def __init__(self, date_time:datetime, ping_stand_ins:bool):
        self.datetime = date_time
        self.ping_stand_ins = ping_stand_ins

class Team:
    def __init__(self, name:str, symbol:str = "", category:discord.CategoryChannel = None) -> None:
        self.members = []
        self.tryouts = []
        self.standins = []
        self.captain = None
        self.vice_captain = None
        self.coach = None
        self.guest_count = 0

        self.name = name.title()
        self.symbol = symbol

        self.stand_in_role = discord.utils.get(bot.angelskar_guild.roles, name=f"{self.name} Stand-in")
        self.tryout_role = discord.utils.get(bot.angelskar_guild.roles, name=f"{self.name} Tryout")
        self.captain_role = discord.utils.get(bot.angelskar_guild.roles, name=f"{self.name} Captain")
        self.vice_captain_role = discord.utils.get(bot.angelskar_guild.roles, name=f"{self.name} Vice-Captain")
        self.guest_role = discord.utils.get(bot.angelskar_guild.roles, name=f"{self.name} Guest")
        self.coach_role = discord.utils.get(bot.angelskar_guild.roles, name=f"{self.name} Coach")
        self.player_role = discord.utils.get(bot.angelskar_guild.roles, name=f"AngelSkar {self.name}")

        self.roles = {
            "player" : self.player_role,
            "captain" : self.captain_role,
            "vice-captain" : self.vice_captain_role,
            "stand-in" : self.vice_captain_role,
            "tryout" : self.tryout_role,
            "coach" : self.coach_role,
            "guest" : self.guest_role
            }

        self.channel_category = category

        for self.schedule_channel in category.text_channels:
            if "schedule" in self.schedule_channel.name:
                break

        self.practices = []

    def is_valid_team(self):
        return len(self.members) > 0 and self.captain != None

    def __str__(self):
        return self.name 

    def get_info_string(self) -> str:
        out = f"# {self.symbol} | {self.name}"

        if not self.is_valid_team():
            return out

        out = f"{out}\n* {self.captain.display_name} **(Captain)**"
        if self.vice_captain != None:
            out = f"{out}\n* {self.vice_captain.display_name} **(Vice-Captain)**"

        for m in self.members:
            if m == self.captain or m == self.vice_captain:
                continue
            out = f"{out}\n* {m.display_name}"

        out = out + "\n"

        if len (self.tryouts) > 0:
            out = f"{out}\n **Tryouts:**"
            for m in self.tryouts:
                out = f"{out}\n* {m.display_name}"
            out = out + "\n"

        if len(self.standins) > 0:
            out = f"{out}\n **Stand-ins:**"
            for m in self.standins:
                out = f"{out}\n* {m.display_name}"
            out = out + "\n"

        if self.guest_count > 0:
            if self.guest_count > 1:
                g = "Guests"
            else:
                g = "Guest"
            out = f"{out}\n{self.guest_count} {g}\n"

        return out

    def update_members(self) -> None:
        self.captain = None
        self.vice_captain = None
        self.coach = None

        try:
            m = self.captain_role.members
            self.captain = m[0]
        except:
            pass
        try:
            m = self.vice_captain_role.members
            self.vice_captain = m[0]
        except:
            pass
        try:
            m = self.coach_role.members
            self.coach = m[0]
        except:
            pass
        try:
            self.members = sorted(self.player_role.members, key = lambda item : item.display_name)
        except:
            self.members = []
        try:
            self.standins = sorted(self.stand_in_role.members.copy(), key = lambda item : item.display_name)
        except:
            self.standins = []
        try:
            self.tryouts = sorted(self.tryout_role.members.copy(), key = lambda item : item.display_name)
        except:
            self.tryouts = []

        try:
            self.guest_count = len(self.guest_role.members)
        except:
            self.guest_count = 0

    def get_mention(self, include_stand_ins = False) -> str:
        out = ""
        out = out + self.player_role.mention
        if len(self.tryout_role.members) > 0:
            out = out + " " + self.tryout_role.mention

        if include_stand_ins:
            if len(self.stand_in_role.members) > 0:
                out = out + " " + self.tryout_role.mention

        return out

class Bot(commands.Bot):
    angelskar_guild:discord.Guild = None
    teams:dict[str, Team] = dict()
    #used to return value from get_last_message since the function returns coro
    target_message = None

    async def get_last_message(self, channel:discord.TextChannel):
        l = [message async for message in channel.history(limit=5)]
        for i in l:
            if i.author == self.user:
                self.target_message = i
        self.target_message = None

    def start_bot(self):
        bot_settings.bot = self
        self.bot_settings = bot_settings.load()
        try:
            with open("token.txt") as file:
                token = file.read()
        except:
            try:
                token = os.environ["TOKEN"]
            except:
                return
        self.run(token)

    async def update_roster_channel(self):
        channel: discord.TextChannel = self.bot_settings.get_roster_channel()

        if channel == None:
            return

        await self.get_last_message(channel)
        last_message = self.target_message

        to_send = "# **__ROSTERS__**\n\n"

        for t in sorted(self.teams.values(), key = lambda e : e.name):
            if t.is_valid_team():
                to_send = to_send + t.get_info_string() + "\n"

        if last_message and last_message.author == self.user:
            await last_message.edit(to_send)
        else:
            await channel.purge(limit=10, check=lambda m: m.author == bot.user)
            await channel.send(to_send)

    async def update_staff_channel(self):
        channel: discord.TextChannel = self.bot_settings.get_staff_channel()

        if channel == None:
            return

        to_send = "# **__STAFF__**"

        roles_to_display = ["Owner", "Co-owner", "Head Admin", "Admin", "Head Moderator", "Moderator", "Twitch Moderator", "Caster", "Developer", "Editor"]

        staff = {}
        roles:dict[str, list[discord.Member]] = {}

        for r in roles_to_display:
            role_obj = discord.utils.get(self.angelskar_guild.roles, name = r)
            for u in role_obj.members:
                if u not in staff:
                    staff[u] = [r]
                    if r in roles:
                        roles[r].append(u)
                    else:
                        roles[r] = [u]
                else:
                    staff[u].append(r)

        for r in roles_to_display:
            if r not in roles:
                continue
            if len(roles[r]) == 0:
                continue
            to_send = f"{to_send}\n# {r}"
            for u in roles[r]:
                to_send = f"{to_send}\n* {u.display_name}"

                if len(staff[u]) > 1:
                    to_send = to_send + " _(Also "
                    for i in range(1, len(staff[u])):
                        to_send = to_send + staff[u][i] + ", "
                    to_send = to_send[:-2] + ")_"

        await self.get_last_message(channel)
        last_message = self.target_message

        if last_message and last_message.author == self.user:
            last_message.edit(to_send)
        else:
            await channel.purge(limit=10, check=lambda m: m.author == bot.user)
            await channel.send(to_send)

    async def log_message(self, message:str) -> bool:
        if len(message) == 0:
            return False
        print(message)
        channel:discord.TextChannel = self.bot_settings.get_log_channel()
        if channel == None:
            return False
        await channel.send(message)
        return True

    async def update_teams(self) -> None:
        # old_team_names = set(self.teams.keys())
        team_names = set()

        for r in self.angelskar_guild.roles:
            if r.name.lower().endswith(" captain"):
                team_names.add(r.name.lower()[:-8])

        # if old_team_names == set(self.teams.keys()):
        #    return

        self.teams.clear()

        for i in team_names:
            i = i.lower()
            for c in self.angelskar_guild.voice_channels:
                if i in c.name.lower():
                    emote = c.name[0]
                    new_team = Team(i, emote, c.category)
                    self.teams[i] = new_team
                    new_team.update_members()
                    break

        await self.update_roster_channel()

bot = Bot(intents=discord.Intents.all(), command_prefix="/")

def get_team_from_user(user:discord.Member) -> Team:

    for i in ["player", "coach", "stand-in", "tryout"]:
        for t in bot.teams.values():
            if t.roles[i] in user.roles:
                return t
            
    return None

@bot.tree.command(name="help",description="Prints some information about the bot and available commands.")
async def help(interaction:discord.Interaction):
    out = "# AngelSkar Bot Help\n[Source Code](<https://github.com/Theuntextured/AngelskarBot>)\n"
    out = out + "## Available Commands:\n"
    for c in bot.tree.get_commands():
        if (interaction.permissions.manage_guild) or (IS_ADMIN_COMMAND not in c.extras):
            out = out + f"* `/{c.name}`: {c.description}\n"
    await interaction.response.send_message(out)

@bot.tree.command(name="logchannel", description="Displays or sets the log channel to use", extras={IS_ADMIN_COMMAND: True})
async def log_channel(interaction:discord.Interaction, channel:discord.TextChannel = None):
    if channel == None:
        c = bot.bot_settings.get_log_channel()
        if c == None:
            await interaction.response.send_message("The log channel is currently not linked.")
        else:
            await interaction.response.send_message(f"The log channel is currently linked to {c.mention}")
    else:
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message("Insufficient permissions to run the command.")
            return
        bot.bot_settings.set_log_channel(channel)

        message = f"Linked the log to channel {channel.mention}"
        await interaction.response.send_message(message)
        await channel.send(message)

@bot.tree.command(name="rosterchannel", description="Displays the roster channel to use. If you have the required permissions, you can set it.")
async def roster_channel(interaction:discord.Interaction, channel:discord.TextChannel = None):
    if channel == None:
        c = bot.bot_settings.get_roster_channel()
        if c == None:
            await interaction.response.send_message("The roster channel is currently not linked.")
        else:
            await interaction.response.send_message(f"The roster channel is currently linked to {c.mention}")
    else:
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message("Insufficient permissions to run the command.")
            return

        bot.bot_settings.set_roster_channel(channel)
        await bot.update_roster_channel()

        message = f"Linked the roster to channel {channel.mention}"
        await interaction.response.send_message(message)

@bot.tree.command(name="staffchannel", description="Displays the staff channel to use. If you have the required permissions, you can set it.")
async def staff_channel(interaction:discord.Interaction, channel:discord.TextChannel = None):
    if channel == None:
        c = bot.bot_settings.get_staff_channel()
        if c == None:
            await interaction.response.send_message("The staff channel is currently not linked.")
        else:
            await interaction.response.send_message(f"The staff channel is currently linked to {c.mention}")
    else:
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message("Insufficient permissions to run the command.")
            return

        bot.bot_settings.set_staff_channel(channel)
        await bot.update_staff_channel()

        message = f"Linked the staff to channel {channel.mention}"
        await interaction.response.send_message(message)

@bot.tree.command(name="createprac", description="Schedule a practice session.")
@discord.app_commands.autocomplete(timezone=capitals.time_zone_autocomplete)
#@discord.app_commands.choices(timezone=[discord.Choice(name=tz, value=id) for id, tz in enumerate(pytz.all_timezones)])
@discord.app_commands.describe(
    date="In format DD-MM-YYYY", 
    time="In format HH::MM (24 hour clock)", 
    timezone="What timezone is the specified time in? Default is CET/CEST",
    pingstandins="Whether or not to ping the stand-ins of the team.")
async def create_prac(interaction:discord.Interaction, date: str, time: str, timezone: str = "Europe/Amsterdam", pingstandins:bool = False):
    # Split the date and time strings for parsing
    team = get_team_from_user(interaction.user)
    if team is None:
        interaction.response.send_message("You cannot create practice because you are not part of a team.")

    channel = team.schedule_channel

    datestr = date.replace("/", "-").replace(".", "-").replace(":", "-").replace(" ", "-").split("-")
    day = datestr[0]
    timed = time.replace(".", ":").split(":")
    hours = int(timed[0])
    minutes = int(timed[1])
    

    # month = months[int(datestr[1])-1]


    try:
        try:
            naive_datetime = datetime(int(datestr[2]), int(datestr[1]), int(day), hours, minutes)
        except:
            await interaction.response.send_message("Invalid Date Format, please use DD-MM-YYYY")
            return


        try:
            user_timezone = pytz.timezone(timezone)
        except:
            await interaction.response.send_message("Invalid timezone!")
            return
        localized_datetime = user_timezone.localize(naive_datetime)
        
        utc_datetime = localized_datetime.astimezone(pytz.utc)

        team.practices.append(Practice(utc_datetime, pingstandins))
        
        # Generate the timestamp for Discord formatting
        timestamp = int(utc_datetime.timestamp())
        
        # Send the message to the chosen channel with the converted timestamp
        await channel.send(f"{team.get_mention(pingstandins)} Practice Scheduled for: <t:{timestamp}:F>")
        
        # Send confirmation message to the user who ran the command
        await interaction.response.send_message(f" Practice successfully scheduled for {team.name} at <t:{timestamp}:F> ({timezone} time).")
    
    except ValueError:
        # Handle invalid date, time, or timezone input
        await interaction.response.send_message("Invalid date, time, or timezone format! Please use the format `DD-MM-YYYY HH:MM` and a valid timezone.")
        return

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.log_message("Bot started!")
    bot.angelskar_guild = discord.utils.get(bot.guilds, id=1049126797465362523)

    await bot.update_teams()
    await bot.update_staff_channel()

@bot.event
async def on_member_update(before:discord.Member, after:discord.Member):
    # inefficient but fuck you
    if before.roles == after.roles:
        return
    for t in bot.teams.values():
        t.update_members()
    await bot.update_roster_channel()
    await bot.update_staff_channel()

@bot.event
async def on_member_remove(member:discord.Member):
    for t in bot.teams.values():
        t.update_members()
    await bot.update_roster_channel()
    await bot.update_staff_channel()

@bot.event
async def on_guild_update(before:discord.Guild, after:discord.Guild):
    #inefficient but fuck you
    #voice channels are used to determine the symbol of the team
    if before.roles == after.roles and before.voice_channels == after.voice_channels:
        return
    await bot.update_teams()
    await bot.update_staff_channel()
