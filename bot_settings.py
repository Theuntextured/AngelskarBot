import discord
from sql_link import link as sql_link

bot:discord.Client|None = None


# noinspection SqlNoDataSourceInspection
class BotSettings:
    def __init__(self):
        self.log_channel = -1
        self.roster_channel = -1
        self.staff_channel = -1

    def save(self):
        sql_link.cursor.execute(f"UPDATE bot_settings SET value = {self.log_channel} WHERE setting = 'log_channel';")
        sql_link.cursor.execute(f"UPDATE bot_settings SET value = {self.staff_channel} WHERE setting = 'staff_channel';")
        sql_link.cursor.execute(f"UPDATE bot_settings SET value = {self.roster_channel} WHERE setting = 'roster_channel';")
        sql_link.database.commit()

    def get_log_channel(self) -> discord.TextChannel:
        return bot.get_channel(self.log_channel)

    def set_log_channel(self, channel: discord.TextChannel) -> None:
        self.log_channel = channel.id
        self.save()

    def get_roster_channel(self) -> discord.TextChannel:
        return bot.get_channel(self.roster_channel)

    def set_roster_channel(self, channel: discord.TextChannel) -> bool:
        self.roster_channel = channel.id
        self.save()
        return True
    
    def get_staff_channel(self) -> discord.TextChannel:
        return bot.get_channel(self.staff_channel)

    def set_staff_channel(self, channel: discord.TextChannel) -> bool:
        self.staff_channel = channel.id
        self.save()
        return True


def load() -> BotSettings:
    try:
        out = BotSettings()
        sql_link.cursor.execute("SELECT value FROM bot_settings WHERE setting = 'log_channel';")
        out.log_channel = int(sql_link.cursor.fetchone()[0])
        sql_link.cursor.execute("SELECT value FROM bot_settings WHERE setting = 'staff_channel';")
        out.staff_channel = int(sql_link.cursor.fetchone()[0])
        sql_link.cursor.execute("SELECT value FROM bot_settings WHERE setting = 'roster_channel';")
        out.roster_channel = int(sql_link.cursor.fetchone()[0])
        return out
    except Exception as e:
        print(e)
        print("Error in loading settings. Restoring default.")
        return BotSettings()
