import nekos
import requests
import time
import json
import os
import socketserver
import http.server


# get api key from file
with open('key', 'r') as f:
    key = f.read()
url = "http://api.telegram.org/bot"+key+"/"
hostname = "hoster"
port = os.environ['PORT']


# get url of a neko img
def getNeko():
    return nekos.img('neko')


# get url for a shibe img
def getShibe():
    response = requests.get('http://shibe.online/api/shibes',  params={'count': 1, 'urls': 'true', 'httpsUrls': 'true'})
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


# send an image a telegram chat
def sendImage(chatID, imageUrl):
    newURL = url + 'sendPhoto?chat_id={0}&photo={1}'.format(chatID, imageUrl)
    print(newURL)
    requests.get(newURL)


def main():
    lastUpdate = None
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer((hostname, port), handler) as httpd:
        httpd.serveForever()

    # make it run indefinitely
    while(True):
        print("waiting for updates")
        updates = getUpdates(lastUpdate)
        try:
            updates['result']
        except Exception as e:
            print(updates)
        # test if there are actual updates then do some shit
        if (len(updates['result']) >= 1):
            try:
                lastUpdate = getLastUpdateID(updates) + 1
            except Exception as e:
                for update in updates['result']:
                    print(update)
                print(e)
            for update in updates['result']:
                try:
                    # post some messages for debugging
                    text = update['message']['text']
                    chatID = update['message']['chat']['id']
                    sender = update['message']['from']['first_name']
                    print(sender + ": " + text)

                    # send the pictures if the right command was sent
                    if "/neko" in text:
                        sendImage(chatID, getNeko())
                    if '/shibe' in text:
                        sendImage(chatID, getShibe())
                    if '/inspire' in text:
                        sendImage(chatID, getInspiro())

                except Exception as e:
                    print(e)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
