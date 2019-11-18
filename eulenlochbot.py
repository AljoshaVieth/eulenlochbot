#!/usr/bin/env python3.6
import logging
from urllib.request import urlopen

from bs4 import BeautifulSoup
from telegram import ChatAction, ReplyKeyboardMarkup
from telegram.ext import MessageHandler, Filters, Updater, CommandHandler
from functools import wraps
import time
import json

bot_token = ''
weather_token = ''

updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

custom_keyboard = [['/status'],
                       ['/wetter', '/foto']]
reply_markup = ReplyKeyboardMarkup(custom_keyboard)

url = 'http://eulenloch.de'


def send_typing_action(func):
    """Sends typing action while processing func command."""
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)
    return command_func


@send_typing_action
def start(update, context):
    start_message = "Willkommen beim inoffiziellen Telegrambot fürs Eulenloch\nDieser Bot kann dir sagen, ob der Lift " \
                    "geöffnet hat und wie das Wetter dort ungefähr ist \nAußerdem kann er dir ein aktuelles Foto aus " \
                    "Schömberg senden \nDer Bot bekommt die Öffnungsaten von der Webseite eulenloch.de \nDie " \
                    "Wetterdaten kommen von openweathermap.org \nDie LiveBilder kommen von einer Webcam aus Schömberg " \
                    "(https://goo.gl/H6QSnw Danke Jens D.)\nDieser Bot ist nicht unfehlbar! \nbei Fragen einfach eine " \
                    "Mail an hallo@aljosha.eu senden."
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_message, reply_markup=reply_markup)

@send_typing_action
def status(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=get_lift_status(), reply_markup=reply_markup)

def send_photo(update, context):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
    photo_url = 'http://webcam-schoemberg.selfhost.me/webcam/image.jpg?' + str(time.time())
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, reply_markup=reply_markup)

@send_typing_action
def weather(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=get_weather(), reply_markup=reply_markup)

@send_typing_action
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, diesen Befehl verstehe ich nicht.", reply_markup=reply_markup)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

status_handler = CommandHandler('status', status)
dispatcher.add_handler(status_handler)

send_photo_handler = CommandHandler('foto', send_photo)
dispatcher.add_handler(send_photo_handler)

weather_handler = CommandHandler('wetter', weather)
dispatcher.add_handler(weather_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

def get_lift_status():
    page = urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    status = soup.find("div", {"id": "links"})

    return status.text.replace('\n', ' ').replace('\r', '')

def get_weather():
    page = urlopen("http://api.openweathermap.org/data/2.5/weather?zip=75328,de&appid=" + weather_token + "&units=metric&lang=de")
    data = json.loads(page.read().decode())
    description = data['weather'][0]['description']
    temperature = data['main']['temp']
    return "Ungefähres Wetter am Lift: " + description + " bei " + str(temperature) + "°C"

updater.start_polling()
