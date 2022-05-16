#!/usr/bin/python3


from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

import subprocess

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello, it's UserControl!\nType '/help' for further information")


def helpfunc(update: Update, context: CallbackContext):
    update.message.reply_text("Use '/info [Worker]' for information about worker and graph his active windows. For example, '/info Pasha'")


def info(update: Update, context: CallbackContext):
    worker_name = context.args[0]
    file = open("./Names.dat", "r")
    workers = file.readline()
    file.close()

    if worker_name not in workers:
        update.message.reply_text("There is no such worker")
        return

    Text = f"Worker name:" + worker_name

    update.message.reply_text(Text)

    # Automatically waits
    plot = subprocess.run(["./Plot.py", worker_name])
    context.bot.send_photo(update.message.chat_id, photo=open("./Graphs/Windows" + worker_name + ".png", 'rb'))


def main():
    try:
        updater = Updater("5341440273:AAHw6wLvQcQAINCWW9epFTDPHGK9lr38BP8",
                      use_context=True)
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(CommandHandler('info', info))
        updater.dispatcher.add_handler(CommandHandler('help', helpfunc))

        updater.start_polling()
        updater.idle()
    except KeyboardInterrupt:
        return

if __name__ == '__main__':
    main()
