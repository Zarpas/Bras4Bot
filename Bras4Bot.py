#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from signal import signal, SIGINT, SIGTERM, SIGABRT

from telegram.ext import Updater, CommandHandler
import pygame


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

cola_archivos = []

SONG_END = pygame.USEREVENT + 1

pygame.mixer.init()

ruta = os.path.join(os.path.dirname(__file__), 'files')


def ls(ruta=None):
    if ruta is None:
        ruta = os.getcwd()

    return [archivo.name for archivo in os.scandir(ruta) if archivo.is_file()]


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hola!, teclea /help para aprender que opciones existen.')


def help(bot, update):
    update.message.reply_text(
        'Este bot reproduce musica en el ordenador anfitrion. Hay varias opciones: /list para listado de canciones'
        'disponible, /play [numero] para reproducir la cancion deseada y /stop para parar la reproduccion.'
    )


def list(bot, update):
    update.message.reply_text('Listado')
    archivos = ls(ruta)
    index = 1
    for archivo in archivos:
        update.message.reply_text('{}- {}'.format(index, archivo))
        index += 1


def play(bot, update, args):
    archivos = ls(ruta)
    archivo = os.path.join(ruta, archivos[int(args[0])-1])
    update.message.reply_text('Reproduciendo: {}'.format(archivos[int(args[0])-1]))
    pygame.mixer.music.set_endevent( SONG_END)
    pygame.mixer.music.load(archivo)
    pygame.mixer.music.play()


def stop(bot, update):
    pygame.mixer.music.stop()
    update.message.reply_text('Parado')


def queue(bot, update, args):
    archivos = ls(ruta)
    update.message.reply_text('En cola: {}'.format(archivos[int(args[0])-1]))
    cola_archivos.append(int(args[0])-1)


def cola(bot, update):
    archivos = ls(ruta)
    update.message.reply_text('Cola de reproducción:')
    try:
        for num in cola:
            update.message.reply_text(archivos[num])
    except Exception:
        update.message.reply_text('Cola vacia.')


def error(bot, update, error):
    logger.warn('Update "{}" caused error "{}"'.format(update, error))


def lanzar_bot(updater):
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("list", list))
    dispatcher.add_handler(CommandHandler("play", play, pass_args = True))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("queue", queue, pass_args = True))
    # algun problema con la libreria pygame hace que no funcione correctamente
    # bypasseada la libreria pygame, utiliza una simple lista de python
    dispatcher.add_handler(CommandHandler("cola", cola))
    dispatcher.add_error_handler(error)
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    #updater.idle()
    stop_signals = (SIGINT, SIGTERM, SIGABRT)
    for sig in stop_signals:
        signal(sig, updater.signal_handler)

    pygame.init()


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("bot-token")  # Bras4Bot
    lanzar_bot(updater)

    updater.is_idle = True
    while updater.is_idle:
        for event in pygame.event.get():
            if event.type == SONG_END:
                print("The song ended!")
                if len(cola_archivos) > 0:
                    archivos = ls(ruta)
                    archivo = os.path.join(ruta, archivos[cola_archivos.pop(0)])
                    pygame.mixer.music.load(archivo)
                    pygame.mixer.music.play()
            if event.type == pygame.K_LCTRL:
                updater.is_idle = False
    pygame.quit()


if __name__ == '__main__':
    main()
