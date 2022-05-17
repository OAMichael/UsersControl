#!/usr/bin/python3

from telegram.ext.updater import Updater
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.replykeyboardremove import ReplyKeyboardRemove

import subprocess

workers_list = []
Buttons = [['Workers info', 'Help'], ['Remove keyboard'], ['List of workers']]
List_to_filter = ['Workers info', 'Help', 'Remove keyboard', 'List of workers']


def start(update: Update, context: CallbackContext):
    kbd = ReplyKeyboardMarkup(Buttons)
    update.message.reply_text(text="Hello, it's UserControl!\nType '/help' for further information", reply_markup=kbd)


def helpfunc(update: Update, context: CallbackContext):
    update.message.reply_text("/info [Worker name] to get information about worker and graph his active windows\n" +
                              "/workers to get list of workers\n" + 
                              "/keyboard to enable keyboard mode\n" +
                              "/normal to disable keyboard mode")


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    query.delete_message()
    worker_info(query.data, query, context)


def ReadNames():
    global workers_list
    file = open("./Names.dat", "r")
    workers_list = file.read().split("\n")
    file.close()
    del workers_list[-1]


def worker_info(worker, update: Update, context: CallbackContext):
    ReadNames()

    if worker not in workers_list:
        update.message.reply_text("There is no such worker")
        return

    Text = f"Worker name:" + worker

    update.message.reply_text(Text)

    # Automatically waits
    plot = subprocess.run(["./Plot.py", worker])
    context.bot.send_photo(update.message.chat_id, photo=open("./Graphs/Windows" + worker + ".png", 'rb'))    


def info(update: Update, context: CallbackContext):
    worker_info(context.args[0], update, context)


def workers(update: Update, context: CallbackContext):
    ReadNames()
    keyboard = []

    for worker in workers_list:
        keyboard.append( [InlineKeyboardButton(worker, callback_data=worker)] )

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"--------- List of workers ({len(workers_list)}) ---------", reply_markup=reply_markup)


def RaiseKeyboard(update: Update, context: CallbackContext):
    kbd = ReplyKeyboardMarkup(Buttons)
    update.message.reply_text(text="Back to keyboard", reply_markup=kbd)


def RemoveKeyboard(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardRemove()
    update.message.reply_text(text="Back to normal mode", reply_markup=reply_markup)


def ProceedKeyboard(update: Update, context: CallbackContext):
    message = update.message.text

    if message == 'Help':
        helpfunc(update, context)
    if message == 'Remove keyboard':
        RemoveKeyboard(update, context)
    if message == 'List of workers':
        workers(update, context)
    if message == 'Workers info':
        global List_to_filter
        ReadNames()

        List_to_filter += workers_list
        if 'Back to menu' not in List_to_filter:
            List_to_filter.append('Back to menu')
        
        Keys = [['Back to menu']]
        for name in workers_list:
            Keys.append([name])

        kbd = ReplyKeyboardMarkup(Keys)
        update.message.reply_text(text="Choose a worker from the list:", reply_markup=kbd)

    if message in workers_list:
        worker_info(message, update, context)
    if message == 'Back to menu':
        RaiseKeyboard(update, context)


def main():
    List_to_filter
    try:
        updater = Updater("5341440273:AAHw6wLvQcQAINCWW9epFTDPHGK9lr38BP8", use_context=True)
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(CommandHandler('info', info))
        updater.dispatcher.add_handler(CommandHandler('help', helpfunc))
        updater.dispatcher.add_handler(CommandHandler('workers', workers))
        updater.dispatcher.add_handler(CommandHandler('keyboard', RaiseKeyboard))
        updater.dispatcher.add_handler(CommandHandler('normal', RemoveKeyboard))
        updater.dispatcher.add_handler(MessageHandler(Filters.text(List_to_filter), ProceedKeyboard))
        updater.dispatcher.add_handler(CallbackQueryHandler(button))

        updater.start_polling()
        updater.idle()
    except KeyboardInterrupt:
        return

if __name__ == '__main__':
    main()
