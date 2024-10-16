import json
import discord
from pytz import all_timezones

from datetime import datetime, timedelta, timezone
import re


def translate_to_datetime(text:str):
    # Regular expression to match the input like "10 days", "10 seconds", or "5 minutes"
    match = re.match(r"(\d+)\s*(seconds?|minutes?|hours?|days?)", text.strip().lower())
    if match:
        value = int(match.group(1))  # Extract the numeric value
        unit = match.group(2)  # Extract the unit (seconds, minutes, hours, days)

        # Determine the appropriate timedelta
        if "second" in unit:
            delta = timedelta(seconds=value)
        elif "minute" in unit:
            delta = timedelta(minutes=value)
        elif "hour" in unit:
            delta = timedelta(hours=value)
        elif "day" in unit:
            delta = timedelta(days=value)
        else:
            raise ValueError("Unsupported time unit")

        # Combine with current datetime
        return datetime.now(timezone.utc) + delta
    else:
        raise ValueError("Invalid input format")


capitals = {}

with open("country-by-capital-city.json", "r", encoding="utf-8") as file:
    for i in json.loads(file.read()):
        if i["city"] is None:
            continue
        capitals[i["country"]] = i["city"]


async def time_zone_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:

    c = current.lower()
    out = []

    for i in all_timezones:
        if c in i.lower():
            out.append(discord.app_commands.Choice(name=i, value=i))
            if len(out) == 25:
                return out

    for country, capital in capitals.items():
        if c in country.lower():
            for k in all_timezones:
                if capital.lower() in k.lower():
                    out.append(discord.app_commands.Choice(name=k, value=k))
                    break
            
    return out
