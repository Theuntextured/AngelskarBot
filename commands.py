from bot import *
from typing import Callable
from PIL import Image, UnidentifiedImageError
import requests
from io import BytesIO
from discord.app_commands.errors import CheckFailure
import pytz


async def command_list_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    current = current.lower().strip()
    out = []
    for c in bot.tree.get_commands():
        if current not in c.name:
            continue
        can_run = True
        for check in c.checks:
            try:
                check(interaction)
            except:
                can_run = False
                break
        if can_run:
            out.append(discord.app_commands.Choice(name=c.name, value=c.name))
    return out


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


class NotCaptain(CheckFailure):
    def __init__(self) -> None:
        message = (
            f"You are not a captain of any team, which is required to run this command."
        )
        super().__init__(message)


def is_captain(
    include_vice_captain: bool = False,
) -> Callable[[discord.app_commands.checks.T], discord.app_commands.checks.T]:

    def predicate(interaction: discord.Interaction) -> bool:
        team = get_team_from_user(interaction.user)
        if team is None:
            raise NotCaptain()
            return False
        if team.captain == interaction.user:
            return True
        if team.vice_captaincaptain == interaction.user and include_vice_captain:
            return True

        raise NotCaptain
        return False

    return discord.app_commands.commands.check(predicate)


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


# command is removed in stable, since it does not do anything.
"""
@bot.tree.command(name="createprac", description="Schedule a practice session.")
@discord.app_commands.autocomplete(timezone=util.time_zone_autocomplete)
@discord.app_commands.rename(pingstandins="ping-stand-ins", timezone="time-zone")
@discord.app_commands.choices(timezone=[discord.Choice(name=tz, value=id) for id, tz in enumerate(pytz.all_timezones)])
@discord.app_commands.describe(
    date="In format DD-MM-YYYY",
    time="In format HH::MM (24 hour clock)",
    timezone="What timezone is the specified time in? Default is CET/CEST",
    pingstandins="Whether or not to ping the stand-ins of the team.",
    )"""


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

    channel = team.schedule_channel

    datestr = (
        date.replace("/", "-")
        .replace(".", "-")
        .replace(":", "-")
        .replace(" ", "-")
        .split("-")
    )
    day = datestr[0]
    timed = time.replace(".", ":").split(":")
    hours = int(timed[0])
    minutes = int(timed[1])

    # month = months[int(datestr[1])-1]

    try:
        try:
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

        team.practices.append(Practice(utc_datetime, pingstandins))

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
