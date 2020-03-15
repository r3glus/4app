#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import random
import time

import gspread
import schedule
from oauth2client.service_account import ServiceAccountCredentials
from twython import Twython, TwythonError, TwythonStreamer

print("Listening for tweets containing the hashtag")


APP_KEY = "kau0g8qYQtMRK0w41GXoSayx0"
APP_SECRET = "jY6W7tWzJKCwpPJylbC46YS4kKluck9nLMaAmZlHuxYte1ce8n"
OAUTH_TOKEN = "1141000476206481408-G8Buwan7GPbXegsL63TJ8r2MaNFjYZ"
OAUTH_TOKEN_SECRET = "DJzTQWyP6K5pOPg3mNbF5wSNOovmNs9v8gXaBziOjniu6"


def twitter_api():
    """ Authenticate credentials"""

    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    return twitter


def spreadsheet():

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'Reglus-bot.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("Reglus Heroku").sheet1
    return sheet


def get_all_records():

    sheet = spreadsheet()
    return sheet.get_all_records()


def get_fake_news_url():
    sheet = spreadsheet()
    records = sheet.get_all_records()
    urls = [url.get('FAKE NEWS URL') for url in records]

    print(urls)
    return urls


def reply(data):
    api = twitter_api()
    all_records = get_all_records()
    handle = data.get('user').get('screen_name')
    fake_news_url = data.get('entities').get('urls')[0].get('url')

    for record in all_records:
        if fake_news_url in record.values():
            reply_text = "Olá @{handle} O link que você compartilhou não parece ser uma notícia verdadeira! verifique este link {record.get('DEBUNKING')}"
            break
    try:
        tweet_id = data.get('id')
        time.sleep(2)
        api.update_status(status=reply_text, in_reply_to_status_id=tweet_id)
        print("Tweet successfully sent!")
        time.sleep(1)
    except TwythonError as e:
        print(e)


class MyStreamer(TwythonStreamer):
    def on_success(self, data):

        tweetText = data.get('text')
        print(tweetText)
        reply(data)

    def on_error(self, status_code, data):
        print("Twitter Error Status code", status_code)

        # self.disconnect()


stream = MyStreamer(APP_KEY, APP_SECRET,
                    OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

links = get_fake_news_url()
stream.statuses.filter(track=links)
