#! /usr/bin/python
import csv
from datetime import datetime
from datetime import timedelta
from base_sport_event_generator import SportEventGenerator

import http.client
import json
import oauth2
import re
import time

GAME_DURATION = 120

class FootballEventGenerator(SportEventGenerator):
    def __init__(self):
        self.keys = {}
        self.matchDetails = {}

    def oauth_req(self, url, http_method="GET", post_body="", http_headers=None):
        consumer = oauth2.Consumer(key=self.keys["CONSUMER_KEY"], secret=self.keys["CONSUMER_SECRET"])
        token = oauth2.Token(key=self.keys["ACCESS_TOKEN"], secret=self.keys["ACCESS_SECRET"])
        client = oauth2.Client(consumer, token)
        resp, content = client.request(url)
        return content

    def buildEvents(self):
        self.getKeys()
        # premierleague
        # championsleague
        # EuropaLeague
        events = []
        home_timeline = self.oauth_req( 'https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=premierleague&count=200')
        twitter_data = json.loads(home_timeline.decode('utf-8'))
        for i, item in reversed(list(enumerate(twitter_data))):
            if(item["text"].startswith("GOAL")):
                matchInfo = self.parseTweet(item["text"])
                self.matchDetails[matchInfo["homeTeam"] + "-" + matchInfo["awayTeam"]] = matchInfo

                print(item["text"])
                print("*******")
        self.buildProactiveEvent()

    def buildProactiveEvent(self):
        events = []
        for key in self.matchDetails:
            matchInfo = self.matchDetails[key]
            payload = {
                "sportsEvent.eventLeague.name": "boom",
                "update.teamName": matchInfo["whoScored"],
                "sportsEvent.awayTeamStatistic.team.name": matchInfo["homeTeam"],
                "sportsEvent.awayTeamStatistic.score": matchInfo["homeScore"],
                "sportsEvent.homeTeamStatistic.team.name": matchInfo["awayTeam"],
                "sportsEvent.homeTeamStatistic.score": matchInfo["awayScore"]
            }
            print(payload)
            events.append(payload)

    # Parse "GOAL! Liverpool 4-0 Barcelona" text to get away team, home team and score.
    def parseTweet(self, text):
        hyphenIdx = text.index("-")
        homeTeam = ""
        awayTeam = ""
        homeScore = ""
        awayScore = ""
        whoScored = ""

        for i, c in enumerate(text):
            if c == '\n' or c == '(':
                break
            # parse everything after GOAL and before - and score
            if i > 4 and not(ord(c) >= ord('0') and ord(c) <= ord('9')) and i < hyphenIdx:
                homeTeam += c
            # parse everything after GOAL and after - and score
            if i > 4 and not(ord(c) >= ord('0') and ord(c) <= ord('9')) and i > hyphenIdx:
                awayTeam += c
            # parse number before -
            if i > 4 and ord(c) >= ord('0') and ord(c) <= ord('9') and i < hyphenIdx:
                homeScore += c
            # parse number after -
            if i > 4 and ord(c) >= ord('0') and ord(c) <= ord('9') and i > hyphenIdx:
                awayScore += c

        homeTeam = self.getStandardNameForTeam(homeTeam.strip())
        awayTeam = self.getStandardNameForTeam(awayTeam.strip())
        homeScore = homeScore.strip()
        awayScore = awayScore.strip()
        matchInfo = {
            'homeTeam': homeTeam,
            'awayTeam': awayTeam,
            'homeScore': homeScore,
            'awayScore': awayScore
        }

        matchInfo['whoScored'] = self.getWhoScored(matchInfo)
        return matchInfo

    def getWhoScored(self, matchInfo):
        homeScore = matchInfo["homeScore"]
        awayScore = matchInfo["awayScore"]
        # base case (if other team has 0 goals)
        if awayScore == '0':
            whoScored = matchInfo["homeTeam"]
        if homeScore == '0':
            whoScored = matchInfo["awayTeam"]
        # if both teams have scored
        if homeScore != '0' and awayScore != '0':
            # get previous state of this game
            previousScored = self.matchDetails[matchInfo["homeTeam"] + "-" + matchInfo["awayTeam"]]
            if previousScored['homeScore'] == homeScore:
                whoScored = matchInfo["awayTeam"]
            else:
                whoScored = matchInfo["homeTeam"]
        return whoScored


    def getKeys(self):
        # TODO add encryption
        with open('key.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='=')
            for row in csv_reader:
                self.keys[row[0]] = row[1]


    def getUsers():
        # TODO: read from dynamodb in batches and send events for those user-ids
        database =  {
            "xid": "Liverpool",
            "yid": "Real Madrid",
            "zid": "Arsenal"
        }

    def getStandardNameForTeam(self, teamName):
        # TODO: read from dynamodb in batches and send events for those user-ids
        database =  {
            "AFC Bournemouth": "Bournemouth",
            "Bournnemouth": "Bournemouth",
            "Spurs": "Tottenham"
        }
        if teamName in database:
            return database[teamName]
        return teamName
