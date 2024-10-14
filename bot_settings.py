import pickle
import discord

bot:discord.Client = None

DATA_FILE = "bot_data.pickle"

class BotSettings:
    def __init__(self):
        self.log_channel = -1
        self.roster_channel = -1
        self.staff_channel = -1

    def save(self):
        global DATA_FILE
        with open(DATA_FILE, "wb") as file:
            pickle.dump(self, file)

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


def load():
    try:
        global DATA_FILE
        with open(DATA_FILE, "rb") as infile:
            return pickle.load(infile)
    except Exception as e:
        print(e)
        print("Error in loading settings. Restoring default.")
        return BotSettings()
