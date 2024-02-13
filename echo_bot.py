import os

import telebot

from dotenv import load_data

load_data()

token = os.getenv('TOKEN')

bot = telebot.TeleBot(token)


@bot.message_handler(content_types=["text"])
def echo(message):
    bot.send_message(message.chat.id, message.text)


bot.polling(none_stop=True)
