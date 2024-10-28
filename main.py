from bot import bot
import webserver
#the two modules are "unused" according to VS, but they need to be loaded. DO NOT REMOVE THEM!
import commands
import events

import sql_link
x = sql_link.SQLLink()
print("EXITING")
exit()

if __name__ == "__main__":
    print("Starting...")
    webserver.keep_alive()
    bot.start_bot()
