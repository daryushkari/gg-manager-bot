import logging
import os
import random
import datetime
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
from telegram import Message, User, Chat, MessageEntity, Document
from random import randint
import duel

games = ['R6','R6','R6', 'RL', 'RL', 'RL', 'Apex']
stickerCount = {}
englishCount = {}
baseClock = time.time()
msgCount = {}
floodStat = {}
floodClock = time.time()


def start(bot, update):
    update.message.reply_text("GG ?")

def randomgame(bot, update):
    update.message.reply_text("GG "+ random.choice(games))
    
def roll(bot, update):
    update.message.reply_text("GG "+ str(randint(0,100)))

def isEnglish(text):
    countEnglishLetters = 0
    for c in text:
        if ord(c) < 128 and c.isalpha():
            countEnglishLetters += 1
    return countEnglishLetters/len(text) >0.5

def processText(bot, update):
    global englishCount
    global baseClock
    print("new Text Upate : "+str(update))
    
    user = update.effective_user
    username = user['username']
    print('user name'+ str(username)) 
    print('update.message.text '+ update.message.text + 'isenglish: '+str(isEnglish(update.message.text)))     
    if isEnglish(update.message.text):
        englishCount[username] = englishCount.setdefault(username, 0) + 1
    
    
    
    timenow = time.time()
    temp = timenow-baseClock
    hours = temp//3600
    if(hours>5):
        baseClock = timenow
        englishCount = {}
    
    if(englishCount.setdefault(username, 0)>10) and isEnglish(update.message.text):
        bot.delete_message(update.message.chat.id, update.message.message_id)
    
    

def processSticker(bot, update):
    global stickerCount
    global baseClock
    print("sticker update"+str(update))
    
    user = update.effective_user
    username = user['username']
    
    stickerCount[username] = stickerCount.setdefault(username, 0) + 1
    
    
    timenow = time.time()
    temp = timenow-baseClock
    hours = temp//3600
    if(hours>5):
        baseClock = timenow
        stickerCount = {}
        
    if(englishCount.setdefault(username, 0)>5):
        bot.delete_message(update.message.chat.id, update.message.message_id)

def antiFlood(bot, update):
    global msgCount
    global floodClock

    print("All Filter update"+str(update))

    user = update.effective_user
    username = user['username']
    msgCount[username] = msgCount.setdefault(username, 0) + 1

    timenow = time.time()

    temp = timenow - floodClock
    if(temp < 10 and msgCount.setdefault(username, 0) > 10 ):
        bot.delete_message(update.message.chat.id, update.message.message_id)
        floodStat[username] = True

    if(temp > 10):
        floodClock = time.time()
        floodStat[username] = False
        msgCount[username] = 0








    

    
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


if __name__ == "__main__":
    # Set these variable to the appropriate values
    TOKEN = os.environ.get('TOKEN')
    NAME = "gg-manager-bot"


    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # Add handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('roll', roll))
    dp.add_handler(CommandHandler('randomgame', randomgame))
    dp.add_handler(CommandHandler('start_duel', duel.start_duel))
    dp.add_handler(CommandHandler('shot!', duel.shot))
    dp.add_handler(MessageHandler((Filters.text & (~ Filters.entity(MessageEntity.MENTION))), processText))
    dp.add_handler(MessageHandler((Filters.sticker | Filters.animation), processSticker))
    dp.add_handler(MessageHandler(Filters.all, antiFlood))
    
    dp.add_error_handler(error)

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",port=int(PORT),url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    
    updater.idle()
