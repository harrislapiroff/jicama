#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import twitter
import re
import settings # this is a relative import. Not sure it works in all versions of python, but seems okay in 2.7.x
from ttapi import Bot
from random import choice, shuffle

ADDRESSING_REQUIRED = True
ADDRESSING_PATTERNS = (
	r'@?%s[,:;]?\s+(.*)' % settings.TURNTABLE['name'].lower(),
	r'(.*),?\s+@?%s[\.!\?]?' % settings.TURNTABLE['name'].lower(),
)

# Initialize Turntable bot
tt_bot = Bot(settings.TURNTABLE['auth'], settings.TURNTABLE['user'], settings.TURNTABLE['room'])

# Connect to Twitter account, if settings are in place
if hasattr(settings, 'TWITTER'):
	tw_bot = twitter.Api(**settings.TWITTER)

# These globals serve as a short term database.
RECENT_SONGS = []
BOPPING = False

# Utility function

def add_current_song(data):
	"This function adds the current song to queue. Expects to receive data from tt_bot.roomInfo()"
	current_song = data['room']['metadata']['songlog'][-1]
	tt_bot.playlistAdd(current_song['_id'], 999999) # add to bottom of queue
	tt_bot.snag()
	tt_bot.speak("I added \"%s\" to my queue!" % current_song['metadata']['song'])
	print "- ADDED TO QUEUE %s" % current_song['metadata']['song']

# These functions get directly bound to events

def newsong(data):
	""""
	1. Send a tweet of random artists to @james_joystick every 10 songs.
	2. Reset the BOPPING global.
	
	"""
	
	# 1: Send a tweet of recent songs
	if hasattr(settings, 'TWITTER'): # only tweet if the twitter settings exist
		TWEET_FORMAT = "Recently played: %s http://tt.fm/james_joystick"
		global RECENT_SONGS
		song = data['room']['metadata']['current_song']
		RECENT_SONGS.append(song)
		print "- RECENT SONG: %s" % song['metadata']['song']
		if len(RECENT_SONGS) == 10:
			tweet_artists = []
			shuffle(RECENT_SONGS)
			tweet_artists.append(RECENT_SONGS.pop()['metadata']['artist'])
			tweet = TWEET_FORMAT % ", ".join(tweet_artists)
			while True:
				tweet_artists.append(RECENT_SONGS.pop()['metadata']['artist'])
				new_tweet = TWEET_FORMAT % ", ".join(tweet_artists)
				if len(new_tweet) > 140:
					break
				tweet = new_tweet
			tw_bot.PostUpdate(tweet)
			RECENT_SONGS = []
			print "- TWEETED: %s" % tweet
	
	# 2: Reset the BOPPING global
	global BOPPING
	BOPPING = False


def update_votes(data):
	"If someone else upvotes a song, go ahead and upvote."

	global BOPPING
	if data['room']['metadata']['upvotes'] > 0 and not BOPPING:
		tt_bot.bop()
		BOPPING = True
		print "- STARTED BOPPPING"


def speak(data):
	addressed = False
	command = data['text'].lower()
	
	# check if text is addressed, extract command, if so
	for expression in ADDRESSING_PATTERNS:
		match = re.match(expression, command)
		if match:
			addressed = True
			command = match.groups()[0] # is this right?
			
	# short circuit if addressing is required, but text is not addressed
	if ADDRESSING_REQUIRED and not addressed:
		return
	
	if re.match(r"add( this)?( song)? to( your)? queue", command):
		tt_bot.roomInfo(add_current_song)

	if re.match(r"(remove|delete)( this)?( song)? from( your)? queue", command):
		tt_bot.playlistRemove(0)
		print "- REMOVED TOP TRACK FROM QUEUE"

	if re.match(r"(hop|step) up", command):
		tt_bot.addDj()
		print "- HOPPED UP"
	
	if re.match(r"(hop|step) down", command):
		tt_bot.remDj()
		print "- STEPPED DOWN"
	
	if re.match(r"skip", command):
		tt_bot.skip()
	
	if re.match(r"(bop|dance)", command):
		if not BOPPING:
			tt_bot.bop()
		else:
			tt_bot.speak("I already am!")


def add_dj(data):
	VERBS = ("play", "spin", "DJ")
	ADJECTIVES = ("hot", "sweet", "rocking", "bumping")
	NOUNS = ("tracks", "songs", "tunes", "beats")
	new_dj = data['user']
	if hasattr(settings, 'TWITTER'):
		tweet = "%s just stepped up to %s some %s %s in http://tt.fm/james_joystick." % (data['user'][0]['name'], choice(VERBS), choice(ADJECTIVES), choice(NOUNS))
		tw_bot.PostUpdate(tweet)
	print "- TWEETED: %s" % tweet


# Bind listeners
tt_bot.on("newsong", newsong)
tt_bot.on("speak", speak)
tt_bot.on("update_votes", update_votes)
tt_bot.on("add_dj", add_dj)


# Kick this party off!
tt_bot.start()
