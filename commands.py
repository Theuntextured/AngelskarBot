import util
from bot import *
from PIL import Image, UnidentifiedImageError
import requests
from io import BytesIO
import pytz
from command_decorators import *
from datetime import datetime, UTC
from practice import Practice


@bot.tree.command(
    name="help",
    description="Prints some information about the bot and available commands.",
)
@discord.app_commands.describe(command="The command to get help with.")
@discord.app_commands.autocomplete(command=command_list_autocomplete)
async def help(interaction: discord.Interaction, command: str = None):
    if command is None:
        out = "# AngelSkar Bot Help\n[Source Code](<https://github.com/Theuntextured/AngelskarBot>)\n"
        out = out + "## Available Commands:\n"
        for c in bot.tree.get_commands():
            can_run = True
            for check in c.checks:
                try:
                    check(interaction)
                except:
                    can_run = False
                    break
            if can_run:
                out = out + f"* `/{c.name}`: {c.description}\n"
        await interaction.response.send_message(out)
        return

    command = command.lower().strip()
    desired_command = bot.tree.get_command(command)
    if desired_command is None:
        await interaction.response.send_message(f"`{command}` is not a valid command.")
        return

    out = f"## `/{desired_command.name}`\n**{desired_command.description}**\n"

    can_run = True
    for check in desired_command.checks:
        try:
            check(interaction)
        except:
            can_run = False
            break

    if not can_run:
        out = f"{out}(You cannot run this command.)\n"

    out = f"{out}## Parameters:"
    for p in desired_command.parameters:
        out = f"{out}\n* {p.name}: {p.description} {'' if p.required else '(optional)'}"

    await interaction.response.send_message(out)


@bot.tree.command(
    name="logchannel", description="Displays or sets the log channel to use."
)
@discord.app_commands.describe(channel="The channel that should be set to be the staff display channel.")
@discord.app_commands.checks.has_permissions(manage_guild=True)
@discord.app_commands.describe(channel="The channel that should be set to be the log display channel.")
async def log_channel(
    interaction: discord.Interaction, channel: discord.TextChannel = None
):
    if channel == None:
        c = bot.bot_settings.get_log_channel()
        if c == None:
            await interaction.response.send_message(
                "The log channel is currently not linked."
            )
        else:
            await interaction.response.send_message(
                f"The log channel is currently linked to {c.mention}"
            )
    else:
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message(
                "Insufficient permissions to run the command."
            )
            return
        bot.bot_settings.set_log_channel(channel)

        message = f"Linked the log to channel {channel.mention}"
        await interaction.response.send_message(message)
        await channel.send(message)


@bot.tree.command(
    name="rosterchannel",
    description="Displays the roster channel to use. If you have the required permissions, you can set it.",
)
@discord.app_commands.describe(channel="The channel that should be set to be the roster display channel.")
async def roster_channel(
    interaction: discord.Interaction, channel: discord.TextChannel = None
):
    if channel == None:
        c = bot.bot_settings.get_roster_channel()
        if c == None:
            await interaction.response.send_message(
                "The roster channel is currently not linked."
            )
        else:
            await interaction.response.send_message(
                f"The roster channel is currently linked to {c.mention}"
            )
    else:
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message(
                "Insufficient permissions to run the command."
            )
            return

        bot.bot_settings.set_roster_channel(channel)
        await bot.update_roster_channel()

        message = f"Linked the roster to channel {channel.mention}"
        await interaction.response.send_message(message)


@bot.tree.command(
    name="staffchannel",
    description="Displays the staff channel to use. If you have the required permissions, you can set it.",
)
@discord.app_commands.describe(channel="The channel that should be set to be the staff display channel.")
async def staff_channel(
    interaction: discord.Interaction, channel: discord.TextChannel = None
):
    if channel == None:
        c = bot.bot_settings.get_staff_channel()
        if c == None:
            await interaction.response.send_message(
                "The staff channel is currently not linked."
            )
        else:
            await interaction.response.send_message(
                f"The staff channel is currently linked to {c.mention}"
            )
    else:
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message(
                "Insufficient permissions to run the command."
            )
            return

        bot.bot_settings.set_staff_channel(channel)
        await bot.update_staff_channel()

        message = f"Linked the staff to channel {channel.mention}"
        await interaction.response.send_message(message)


@bot.tree.command(
    name="team",
    description="Displays information about a specific team.",
)
@discord.app_commands.describe(team="The desired team.")
async def get_team_info(interaction: discord.Interaction, team: str):
    team = team.lower()

    if team not in bot.teams:
        await interaction.response.send_message(f"{team.title()} is not a valid team.")
        return

    await interaction.response.send_message(bot.teams[team].get_info_string())


@bot.tree.command(
    name="registerteamlogo",
    description="Register a new team logo. Make sure to embed an image to this command.",
)
@discord.app_commands.describe(image_link="The url containing the image. The image will be resized to 128x128 when uploading it to Discord.")
@is_captain(True)
async def register_team_logo(interaction: discord.Interaction, image_link: str):
    team = get_team_from_user(interaction.user)

    if team is None or (
        team.captain != interaction.user and team.vice_captain != interaction.user
    ):
        interaction.response.send_message(
            "Only captains and vice-captains are allowed to set the team logo."
        )

    try:
        logo = Image.open(requests.get(image_link, stream=True).raw)
    except UnidentifiedImageError:
        interaction.response.send_message("The embed did not contain a valid image.")
        return
    logo = logo.resize((128, 128))

    to_delete = util.get_emoji_id_from_name(bot, team.name)
    if to_delete is not None:
        await bot.angelskar_guild.delete_emoji(
            discord.Object(to_delete), reason="Updating to new logo. (Deleting old)"
        )

    b = BytesIO()
    logo.save(b, format="PNG")

    new_emoji: discord.Emoji = await bot.angelskar_guild.create_custom_emoji(
        name=team.name,
        image=b.getvalue(),
        reason="Updating to new logo. (Creating new)",
    )
    await interaction.response.send_message(
        f"Successfully updated the team logo for Team {team.name} to <:{new_emoji.name}:{new_emoji.id}>."
    )
    await bot.update_teams()


@bot.tree.command(name="createprac", description="Schedule a practice session.")
@discord.app_commands.autocomplete(timezone=time_zone_autocomplete)
@discord.app_commands.rename(pingstandins="ping-stand-ins", timezone="time-zone")
@discord.app_commands.describe(
    date="In format DD-MM-YYYY",
    time="In format HH::MM (24 hour clock)",
    timezone="What timezone is the specified time in? Default is CET/CEST",
    pingstandins="Whether or not to ping the stand-ins of the team. Default is False.",
    )
@is_captain(True)
async def create_prac(
    interaction: discord.Interaction,
    date: str,
    time: str,
    timezone: str = "Europe/Amsterdam",
    pingstandins: bool = False,
):
    # Split the date and time strings for parsing
    team = get_team_from_user(interaction.user)
    if team is None:
        interaction.response.send_message(
            "You cannot create practice because you are not part of a team."
        )
    try:    
        channel = team.schedule_channel

        datestr = (
            date.replace("/", "-")
            .replace(".", "-")
            .replace(":", "-")
            .replace(" ", "-")
            .split("-")
        )
        timed = time.replace(".", ":").split(":")
        hours = int(timed[0])
        minutes = int(timed[1])
        try:
            day = datestr[0]
            naive_datetime = datetime(
                int(datestr[2]), int(datestr[1]), int(day), hours, minutes
            )
        except:
            await interaction.response.send_message(
                "Invalid Date Format, please use DD-MM-YYYY"
            )
            return

        try:
            user_timezone = pytz.timezone(timezone)
        except:
            await interaction.response.send_message("Invalid timezone!")
            return
        localized_datetime = user_timezone.localize(naive_datetime)

        utc_datetime = localized_datetime.astimezone(pytz.utc)

        if utc_datetime <= util.get_utc_now():
            await interaction.response.send_message("You cannot create a practice session in the past.")
            return

        for p in team.practices:
            if utc_datetime == p.datetime:
                await interaction.response.send_message("A practice session for this time already exists.")
                return

        team.practices.append(Practice(utc_datetime, pingstandins, team))

        # Generate the timestamp for Discord formatting
        timestamp = int(utc_datetime.timestamp())

        # Send the message to the chosen channel with the converted timestamp
        await channel.send(
            f"{team.get_mention(pingstandins)} Practice Scheduled for: <t:{timestamp}:F>"
        )

        # Send confirmation message to the user who ran the command
        await interaction.response.send_message(
            f" Practice successfully scheduled for {team.name} at <t:{timestamp}:F> ({timezone} time)."
        )

    except ValueError:
        # Handle invalid date, time, or timezone input
        await interaction.response.send_message(
            "Invalid date, time, or timezone format! Please use the format `DD-MM-YYYY HH:MM` and a valid timezone."
        )
        return


@bot.tree.command(name="pracs", description="Displays the list of practice sessions.")
@discord.app_commands.autocomplete(team=teams_autocomplete)
@discord.app_commands.describe(team="What team's practice sessions to list. The default is your own, if you have one.")
async def prac_list(interaction:discord.Interaction, team: str = None):
    try:
        if team is None:
            team_object = get_team_from_user(interaction.user)
        else:
            team_object = bot.teams[team.strip().lower()]
    except:
        await interaction.response.send_message("Invalid team name!")
        return
    if team_object is None:
        await interaction.response.send_message("You are not part of any team. Please specify what team's practices you want to list.")
        return

    if len(team_object.practices) == 0:
        await interaction.response.send_message(f"Team {team_object.name.title()} has no scheduled practices.")

    out_str = f"Team {team_object.name.title()} has the following practice sessions:\n"

    for i, p in enumerate(team_object.practices):
        out_str += f"* {i}: <t:{int(p.datetime.timestamp())}:F> (<t:{int(p.datetime.timestamp())}:R>)\n"

    await interaction.response.send_message(out_str)


@bot.tree.command(name="deleteprac", description="Deletes a practice session.")
@discord.app_commands.describe(index = "What practice session to delete. Do /pracs to view the indices of the practice sessions.")
@is_captain(True)
async def delete_prac(interaction:discord.Interaction, index: int):
    team = get_team_from_user(interaction.user)
    if team is None:
        await interaction.response.send_message("You cannot delete practice because you are not part of a team.")
        return
    try:
        team.practices[index].safe_delete()
    except:
        await interaction.response.send_message("The index you inserted is not valid.")
        return

    await interaction.response.send_message("Successfully deleted the practice session.")




@bot.tree.command(name="timeout", description="Timeouts a user.")
@discord.app_commands.describe(user="The member to time out.", 
                               duration="How long to time out the user for.", 
                               reason="The reason for the timeout. This will be communicated to the user.")
@discord.app_commands.checks.has_permissions(moderate_members=True)
async def timeout(
    interaction: discord.Interaction,
    user: discord.Member,
    duration: str,
    reason: str = "Unspecified reason.",
):
    if not interaction.permissions.moderate_members:
        interaction.response.send_message("Insufficient permissions.")
        return
    try:
        until = util.translate_to_datetime(duration)
    except:
        interaction.response.send_message("The duration was invalid.")
        return

    try:
        await user.timeout(until, reason=reason)
    except:
        await interaction.response.send_message("Bot has insufficient permissions.")
        return

    await interaction.response.send_message(
        f"Successfully timed out {user.display_name} for {duration.lower()} with the reason:\n> {reason}"
    )

    try:
        await user.send(
            f"You have been timed out for {duration} with the following reason:\n> {reason}"
        )
    except:
        await interaction.response.send_message(
            f"{user.mention} You have been timed out for {duration} with the following reason:\n> {reason}"
        )
