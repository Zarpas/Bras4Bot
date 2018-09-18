#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from signal import signal, SIGINT, SIGTERM, SIGABRT
import logging
from os import scandir, getcwd, path
import pygame
from time import sleep

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

cola_archivos = []

SONG_END = pygame.USEREVENT + 1

pygame.mixer.init()

ruta = path.join(
    path.dirname(__file__),
    'files')

def ls(ruta = getcwd()):
    return [arch.name for arch in scandir(ruta) if arch.is_file()]

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hola!, teclea /help para aprender que opciones existen.')

def help(bot, update):
    update.message.reply_text('Este bot reproduce musica en el ordenador anfitrion. Hay varias opciones: /list para listado de canciones disponible, /play [numero] para reproducir la cancion deseada y /stop para parar la reproduccion.')

def list(bot, update):
    update.message.reply_text('Listado')
    archivos = ls(ruta)
    index = 1
    for archivo in archivos:
        update.message.reply_text(str(index) + '- ' + archivo)
        index+=1
    
def play(bot, update, args):
    archivos = ls(ruta)
    archivo = path.join(ruta, archivos[int(args[0])-1])
    update.message.reply_text('Reproduciendo: ' + archivos[int(args[0])-1])
    pygame.mixer.music.set_endevent( SONG_END)
    pygame.mixer.music.load(archivo)
    pygame.mixer.music.play()

def stop(bot, update):
    pygame.mixer.music.stop()
    update.message.reply_text('Parado')

def queue(bot, update, args):
    archivos = ls(ruta)
    update.message.reply_text('En cola: ' + archivos[int(args[0])-1])
    cola_archivos.append(int(args[0])-1)

def cola(bot, update):
    archivos = ls(ruta)
    update.message.reply_text('Cola de reproducción:')
    try:
        for num in cola:
            update.message.reply_text(archivos[num])
    except:
        update.message.reply_text('Cola vacia.')

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("bot-token") # Bras4Bot

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("list", list))
    dp.add_handler(CommandHandler("play", play, pass_args = True))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("queue", queue, pass_args = True))  # algun problema con la libreria pygame hace que no funcione correctamente
                                                                      # bypasseada la libreria pygame, utiliza una simple lista de python
    dp.add_handler(CommandHandler("cola", cola))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.

    #updater.idle()

    # Sustituyo el codigo original por otro que revise y chequee

    pygame.init()

    stop_signals = (SIGINT, SIGTERM, SIGABRT)

    for sig in stop_signals:
        signal( sig, updater.signal_handler)
    updater.is_idle = True
    while updater.is_idle:
        # sleep(1)
        for event in pygame.event.get():
            if event.type == SONG_END:
                print("The song ended!")
                if len(cola_archivos) > 0:
                    archivos = ls(ruta)
                    archivo = path.join(ruta, archivos[cola_archivos.pop(0)])
                    pygame.mixer.music.load( archivo)
                    pygame.mixer.music.play()
            if event.type == pygame.K_LCTRL:
                updater.is_idle = False
    pygame.quit()


if __name__ == '__main__':
    main()
