import nekos
import time
import requests
import json
import os
from bottle import run, route, request as bottle_request


# get api key from file
"""
with open('key', 'r') as f:
    key = f.read()
    """

# get api key from environment variable
key = os.environ['APIKEY']
url = "http://api.telegram.org/bot"+key+"/"
hostname = "hoster"
port = os.environ['PORT']


# get url of a neko img
def getNeko():
    return nekos.img('neko')


# get url for a shibe img
def getShibe():
    response = bottle_request.get('http://shibe.online/api/shibes',  params={'count': 1, 'urls': 'true', 'httpsUrls': 'true'})
    return response.json()[0]


# get inspirobot image
def getInspiro():
    response = requests.get('http://inspirobot.me/api', params={'generate': 'true'})
    return response.text


# get data from telegram server
def getData(url):
    response = requests.get(url)
    localData = response.content.decode('utf8')
    return localData


# extract jason from telegram server answer
def getJSON(url):
    localdata = getData(url)
    jsonData = json.loads(localdata)
    return jsonData


# get only new telegram server answers as json
def getUpdates(offset=None):
    localUrl = url+'getUpdates?timeout=25&allowed_updates=["message"]'
    if offset:
        localUrl += '&offset={}'.format(offset)
    js = getJSON(localUrl)
    return js


# get the newest update id from the array of messages
def getLastUpdateID(updates):
    if len(updates) > 0:
        updateIDS = []
        for update in updates['result']:
            updateIDS.append(int(update['update_id']))
        return max(updateIDS)


def getChatID(data):
    id = data['message']['chat']['id']
    return id


def getMessage(data):
    message = data['message']['text']
    return message


def getSender(data):
    sender = data['message']['from']['first_name']


# send an image a telegram chat
def sendImage(chatID, imageUrl):
    newURL = url + 'sendPhoto'.format(chatID, imageUrl)
    print(newURL)
    requests.get(newURL, {'chat_id': chatID, 'photo': imageUrl})


@post('/'+key)
def main():
    data = bottle_request.json
    chatID = getChatID(data)
    sender = getSender(data)
    message = getMessage(data)

    if message contains '/neko':
        sendImage(chatID, getNeko())
    if message contains '/shibe':
        sendImage(chatID, getShibe())
    if message contains 'inspire':
        sendImage(chatID, getInspiro())
    return response

if __name__ == '__main__':
    run(name = hostname, port=int(port), debug=True)
