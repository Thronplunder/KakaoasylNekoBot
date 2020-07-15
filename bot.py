
import datetime
import io
import os
import pathlib
import random

from collections import namedtuple
from urllib.parse import urljoin
from functools import wraps

import pytz
import requests

from flask import Flask, request

SCRIPT_DIR = pathlib.Path(__file__).absolute().parent

TIMEZONE = pytz.timezone('Europe/Berlin')

NEKOS_API = 'https://nekos.life/api/v2/img/neko'

BUTTS_API = 'http://api.obutts.ru/noise/1'
BUTTS_MEDIA_BASE = 'http://media.obutts.ru/'

BOOBS_API = 'http://api.oboobs.ru/noise/1'
BOOBS_MEDIA_BASE = 'http://media.oboobs.ru/'

CATAAS_API_BASE = 'https://cataas.com/'
CATAAS_API_IMG = urljoin(CATAAS_API_BASE, 'cat')
CATAAS_API_GIF = urljoin(CATAAS_API_BASE, 'cat/gif')

RACCOON_DB_PATH = SCRIPT_DIR / 'raccoon.db'
RACCOON_IDS = RACCOON_DB_PATH.open().read().splitlines()

BOOB_LEFT_SIDES = (
        '{', '(', '[', '\\'
        )

BOOB_RIGHT_SIDES = (
        '}', ')', ']', '/',
        )

BOOB_CRACKS = (
        'y', 'Y', '/\\', 'ㅅ', ')(', '][', '}{', ')(.)(',
        )

BOOB_NIPPLES = (
        'o', '.', 'O', '0', '。', '+', 'p', '-', '*', '•', '^', '°', '○',
        )

MAGIC_8_BALL_ANSWERS = (
        'It is certain.',
        'It is decidedly so.',
        'Without a doubt.',
        'Yes - definitely.',
        'You may rely on it.',
        'As I see it, yes.',
        'Most likely.',
        'Outlook good.',
        'Yes.',
        'Signs point to yes.',
        'Reply hazy, try again.',
        'Ask again later.',
        'Better not tell you now.',
        'Cannot predict now.',
        'Concentrate and ask again.',
        'Don\'t count on it.',
        'My reply is no.',
        'My sources say no.',
        'Outlook not so good.',
        'Very doubtful.',
        )

LORENZ_URL = 'www.hfm-karlsruhe.de/inmm/images/01-InMM/team/Lorenz-rainer-120x120.jpg'
LORENZ_MSG = 'Ähm Entschuldigung, was machen sie da?'

SEDUCTIVESEEDORF_URL = "https://www.hmdk-stuttgart.de/typo3temp/_processed_/csm_Portr%C3%A4t-Seedorf-1-f__002__aff54ba6e5.jpg"
SEDUCTIVESEEDORF_MSG = "Ich zeige ihnen eben meinen verkürzten Dominantseptakkord"

WEEKEND_DAYS = (5, 6)


# flask app
APP = Flask(__name__)
APP.debug = 'Debug' in os.environ

# get api key from environment variable
KEY = os.environ['APIKEY']
BASE_URL = 'https://api.telegram.org/bot'+KEY+'/'

COMMANDS = {}

TextMsg = namedtuple('text_msg', ['text'])
PictureMsg = namedtuple('picture_msg', ['url', 'caption'], defaults=('',))
PictureFileMsg = namedtuple('picture_file_msg', ['file'])
AnimationFileMsg = namedtuple('animation_file_msg', ['file'])

BotCommand = namedtuple('bot_command', ['function', 'helptext'])


def bot_command(command):
    '''
    Decorator for bot commands

    Automatically fills the COMMANDS dict

    param command: name of the command
    '''

    def wrapper(func):
        COMMANDS[command] = BotCommand(func, func.__doc__)
        return func

    return wrapper


def nsfw(text=''):
    '''
    Replaces normal function with a somewhat safe for work ascii boobs.

    param text: text to prepend the ascii boobs with
    '''

    def nsfw_decorator(func):
        @wraps(func)
        def wrapper():
            if not is_nsfw_time():
                return TextMsg(f'{text}\n{gen_ascii_boobs()}')
            return func()

        return wrapper
    return nsfw_decorator


def gen_ascii_boobs():
    '''generate ascii boob'''
    left_side = random.choice(BOOB_LEFT_SIDES)
    right_side = random.choice(BOOB_RIGHT_SIDES)
    crack = random.choice(BOOB_CRACKS)
    nipple = random.choice(BOOB_NIPPLES)
    spacing = ' ' * random.randint(0, 2)
    return left_side + spacing + nipple + spacing + crack + spacing + nipple + spacing + right_side


def is_nsfw_time():
    '''Returns true if outside of normal work ours in a specific timezone'''
    current_datetime = datetime.datetime.now(tz=TIMEZONE)
    current_time = current_datetime.time()
    current_date = current_datetime.date()
    return ((current_time.hour >= 18 or current_time.hour < 7)
            or current_date.weekday() in WEEKEND_DAYS)


def get_url_io_buffer(url):
    '''Request given url and return response content as BytesIO buffer and mime type'''
    resp = requests.get(url)

    return io.BytesIO(resp.content)


@bot_command('neko')
def get_neko():
    '''post random neko picture'''
    return PictureMsg(requests.get(NEKOS_API).json()['url'])


@bot_command('shibe')
def get_shibe():
    '''post random shibe picture'''
    response = requests.get('http://shibe.online/api/shibes',
                            params={'count': 1,
                                    'urls': 'true',
                                    'httpsUrls': 'true'})
    return PictureMsg(response.json()[0])


@bot_command('inspire')
def get_inspiro():
    '''post a random inspirational quote'''
    response = requests.get('http://inspirobot.me/api',
                            params={'generate': 'true'})
    return PictureMsg(response.text)

@bot_command('boobies')
@nsfw()
def get_boobies():
    '''post random boobies'''
    response = requests.get(BOOBS_API)

    if 200 <= response.status_code < 300:
        relative_preview_url = response.json()[0]['preview']
        absolute_preview_url = urljoin(BOOBS_MEDIA_BASE, relative_preview_url)
        return PictureMsg(absolute_preview_url)

    return TextMsg('Boobs are striking :(')

@bot_command('butt')
@nsfw('Sorry, no butts at this time of day, but you can have some boobs.')
def get_butt():
    '''post random butts'''
    response = requests.get(BUTTS_API)

    if 200 <= response.status_code < 300:
        relative_preview_url = response.json()[0]['preview']
        absolute_preview_url = urljoin(BUTTS_MEDIA_BASE, relative_preview_url)
        return PictureMsg(absolute_preview_url)

    return TextMsg('Butts are striking :(')

@bot_command('8ball')
def get_8_ball():
    '''post random magic 8 ball answer'''
    return TextMsg(random.choice(MAGIC_8_BALL_ANSWERS))


@bot_command('lorenz')
def get_lorenz():
    '''post lorenz'''
    return PictureMsg(LORENZ_URL, LORENZ_MSG)

@bot_command('seductiveseedorf')
def get_seedorf():
    '''post seedorf'''
    return PictureMsg(SEDUCTIVESEEDORF_URL, SEDUCTIVESEEDORF_MSG)

@bot_command('cat')
def get_cat():
    '''post random cat from CATAAS'''

    img = get_url_io_buffer(CATAAS_API_IMG)

    return PictureFileMsg(img)


@bot_command('catgif')
def get_catgif():
    '''post random cat gif from CATAAS'''

    img = get_url_io_buffer(CATAAS_API_GIF)

    return AnimationFileMsg(img)


@bot_command('raccoon')
def get_raccon():
    '''post random raccoon pic'''

    return PictureMsg(random.choice(RACCOON_IDS))


@bot_command('help')
def generate_help():
    '''post help'''
    text = 'The bot supports the following commands:\n\n'
    for command, (_, helptext) in COMMANDS.items():
        text += f'- /{command}: {helptext}\n'

    return TextMsg(text)


def get_chat_id(data):
    '''extracts the chat id from a request'''
    _id = data['message']['chat']['id']
    return _id


def get_message(data):
    '''extracts the text message from a request'''
    message = data['message']['text']
    return message


# send an image a telegram chat
def send_image(chat_id, image_url, caption):
    '''
    Send image to a telegram chat

    param chat_id: target chat
    param image_url: url of the image
    param caption: image caption
    '''

    url = BASE_URL + 'sendPhoto'
    requests.get(url, {
            'chat_id': chat_id,
            'photo': image_url,
            'caption': caption})


def send_message(chat_id, message):
    '''
    Send message to a telegram chat

    param chat_id: target chat
    param message: message to send
    '''
    url = BASE_URL + 'sendMessage'
    requests.get(url, {'chat_id': chat_id, 'text': message})


def send_image_file(chat_id, img_file):
    '''
    Send image file to telegram chat

    param chat_id: target chat
    param img_file: img file as file like object
    param mime: image mime type
    '''

    url = BASE_URL + 'sendPhoto'
    requests.post(url, params={'chat_id': chat_id}, files={'photo': img_file})


def send_animation_file(chat_id, animation_file):
    '''
    Send animation file to telegram chat

    param chat_id: target chat
    param img_file: img file as file like object
    param mime: image mime type
    '''

    url = BASE_URL + 'sendAnimation'
    requests.post(
            url,
            params={'chat_id': chat_id},
            files={'animation': ('animaiton.gif', animation_file, 'image/gif')}
            )


def command_dispatch(chat_id, msg):
    '''
    Extracts chat commands from messages and dispatches the function call

    param chatID: target chat
    param msg: (command) message from the chat
    '''
    if not msg.startswith('/'):
        return

    # get first word of message
    command = msg.split(' ', 1)[0]
    # handle targeted commands by removing '@' and everything's that follows
    command = command.split('@', 1)[0]
    # remove command prefix
    command = command.strip('/')

    if command not in COMMANDS:
        return

    msg = COMMANDS[command].function()

    if isinstance(msg, PictureMsg):
        send_image(chat_id, msg.url, msg.caption)

    elif isinstance(msg, TextMsg):
        send_message(chat_id, msg.text)

    elif isinstance(msg, PictureFileMsg):
        send_image_file(chat_id, msg.file)

    elif isinstance(msg, AnimationFileMsg):
        send_animation_file(chat_id, msg.file)

@APP.route('/')
def hello():
    return 'Hello this is Bot'


@APP.route('/'+KEY, methods=['GET', 'POST'])
def handle():
    '''Handles webhook requests from telegram'''
    if request.method == 'POST':
        data = request.get_json()
        if 'text' in data['message']:
            chat_id = get_chat_id(data)
            message = get_message(data)
            if data['message']['from']['is_bot'] is False:
                command_dispatch(chat_id, message)
    return 'ok'
