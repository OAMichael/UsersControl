#!/usr/bin/python3


from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters


import subprocess
from xdo import Xdo
 


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello, it's UserControl!\nType '/help' for further information")

def helpfunc(update: Update, context: CallbackContext):
    update.message.reply_text("Use '/info [Worker]' for information about worker and graph his active windows. For example, '/info Pasha'")


def info(update: Update, context: CallbackContext):
    worker_name = context.args[0]
    Text = "{:s}".format("Worker name:") + worker_name

    xdo = Xdo()

    # Active window
    try:
        xdo_window_name = xdo.get_window_name(xdo.get_active_window()).decode('UTF-8')
        Text += "\n{:s}".format("Current window name:") + xdo_window_name
    except:
        pass

    update.message.reply_text(Text)

    # Automatically waits
    plot = subprocess.run("./Plot.py")
    context.bot.send_photo(update.message.chat_id, photo=open('./Graphs/Windows.png', 'rb'))


def main():
    updater = Updater("5341440273:AAHw6wLvQcQAINCWW9epFTDPHGK9lr38BP8",
                  use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('info', info))
    updater.dispatcher.add_handler(CommandHandler('help', helpfunc))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
