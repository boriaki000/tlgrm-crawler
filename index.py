import sys

import json
import os
import requests
import asyncio
import configparser
from pytz import timezone, utc
from datetime import datetime
from time import sleep
from googletrans import Translator
from telethon import TelegramClient

# Telegram
config = configparser.ConfigParser()
config.read("config.ini")
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
api_hash = str(api_hash)
phone = config['Telegram']['phone']
username = config['Telegram']['username']
# Translator
translator = Translator()
# Discord
discord_webhook = config['Discord']['webhook']
# Other
test_mode = config['Other']['test_mode'] == '1'
retry_count = 2
text_prefix = '```'


async def get_posts(chat_url, basetime, time_distance, pytz_timezone):
    try:
        channel = await client.get_entity(chat_url)
        result = []
        async for message in client.iter_messages(chat_url,limit=100):
            created_at = datetime.strptime(str(message.date), '%Y-%m-%d %H:%M:%S+00:00')
            distance = basetime - created_at
            if distance.days == 0 and distance.seconds < time_distance:
                text = translator.translate('translated:' + message.text, src='en', dest='ja').text
                result.append({'created_at':str(pytz_timezone.localize(created_at))
                            ,'text':text_prefix + text + text_prefix
                            ,'url':chat_url + '/' + str(message.id)})
    except Exception as e:
        print('Error occurs in get_posts\n')
        print(str(e) + '\n')
        raise Exception('Inner Error')
    else:
        return result

async def get_title(chat_url):
    channel = await client.get_entity(chat_url)
    return channel.title

def post_to_discord(result, user_name):
    if result:
        result.reverse()
        for item in result:
            call_discord_api(item, user_name)

def call_discord_api(item, user_name):
    content = user_name + ' ' + item['created_at'] + '\n' + item['text'] + '\n' + item['url']
    for i in range(0, retry_count):
        try:
            response = requests.post(
                discord_webhook
                ,json.dumps({'content': content})
                ,headers={'Content-Type': 'application/json'}
            )
            if response.status_code != requests.codes['no_content']:
                raise Exception('Webhook returned not expected code >>' + str(response))
        except Exception as e:
            logger.warn('Error occurs in post_to_discord.\n')
            logger.warn(str(e) + '\n')
            sleep(i * 5)
        else:
            print('post discord success!')
            return response

    print('Could not post below content.\n')
    print('user_name >> ' + item['user_name'] + '\n') 
    print('created_at >> ' + item['created_at'] + '\n') 
    raise Exception('Inner Error')

def show_test_result(result):
    print('test mode')
    if result:
        print(len(result))
        for res in result:
            print(res['created_at'])
            print(res['text'])
            print(res['url'])
    else:
        print('no posts')


# Create the client and connect
client = TelegramClient(username, api_id, api_hash)
client.start()

loop = asyncio.get_event_loop()
args = sys.argv
chat_url = args[1]
title = loop.run_until_complete(get_title(chat_url))
time_distance = int(args[2])
basetime = datetime.now()
pytz_timezone = timezone(utc.zone)

print('channle title:' + title)
result = loop.run_until_complete(get_posts(chat_url, basetime, time_distance, pytz_timezone))

if test_mode:
    show_test_result(result)
else:
    post_to_discord(result, title)
