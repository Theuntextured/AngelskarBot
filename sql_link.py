import mysql.connector
import json
import os

class SQLLink:
    def __init__(self):
        self.is_initialized = False

        print("Initializing SQLLink")
        try:
            self.settings = {}
            with open("database_settings.json", "r") as file:
                for i in json.load(file):
                    self.settings[i["name"]] = i["value"]
                print("Retrieved database settings via file.")
        except FileNotFoundError:
            try:
                self.settings = [
  {
    "name": "MYSQL_ADDON_DB",
    "value": os.environ["MYSQL_ADDON_DB"]
  },
  {
    "name": "MYSQL_ADDON_HOST",
    "value": os.environ["MYSQL_ADDON_HOST"]
  },
  {
    "name": "MYSQL_ADDON_PASSWORD",
    "value": os.environ["MYSQL_ADDON_PASSWORD"]
  },
  {
    "name": "MYSQL_ADDON_PORT",
    "value": os.environ["MYSQL_ADDON_PORT"]
  },
  {
    "name": "MYSQL_ADDON_URI",
    "value": os.environ["MYSQL_ADDON_URI"]
  },
  {
    "name": "MYSQL_ADDON_USER",
    "value": os.environ["MYSQL_ADDON_USER"]
  },
  {
    "name": "MYSQL_ADDON_VERSION",
    "value": os.environ["MYSQL_ADDON_VERSION"]
  }
]
                print("Retreived database settings via environment variables.")
            except Exception as E:
                print(E)
                print("Some environment variables were missing or incorrect. The database could not be linked.")
                return

        try:
            self.database = mysql.connector.connect(
                host=self.settings["MYSQL_ADDON_HOST"],
                user=self.settings["MYSQL_ADDON_USER"],
                password=self.settings["MYSQL_ADDON_PASSWORD"]
            )
            print("Database successfully connected.")
        except Exception as e:
            print(e)
            return

        self.cursor = self.database.cursor()

        self.is_initialized = True

        self.cursor.execute("CREATE DATABASE BotSettings")

        self.cursor.execute("SHOW DATABASE")

        for x in self.cursor:
            print("Database found: ", x)
