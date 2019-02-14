#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    Code to download tweets from a set of twitter accounts and analyze them.
#    The code was used to write this blog post about UK MPs use of twitter.
#    The artical which came out of this work can be downloaded here:
#
#	 https://commonslibrary.parliament.uk/tag/roderick-mackenzie/
#
#    Copyright (C) 2018 Roderick C. I. MacKenzie r.c.i.mackenzie at googlemail.com
#	 Room B86 Coates, University Park, Nottingham, NG7 2RD, UK
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License v2.0, as published by
#    the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

##
# @file
# Harvest all MPs tweets and store them in the db.

import time
import tweepy #https://github.com/tweepy/tweepy
import csv
import os

import random
import mysql.connector as mariadb
import time
import sys

from db import db_get_all_users
from db import db_visit_user
from db import db_add_user
from db import db_get_oldest_visited
from db import db_set_mariadb_connection
from db import db_get_mariadb_cursor
from db import db_user_update_job1
from db import db_user_get_job1
from db import to_stats
from word_usage_graph import word_usage_graph
from hashtag_usage_graph import hashtag_usage_graph
from at_usage_graph import at_usage_graph

from time_domain import time_domain

from hashtag_flow import hashtag_flow
from time_domain import time_domain_random_stats

db_set_mariadb_connection()
cursor = db_get_mariadb_cursor()


from my_twitter import my_twitter_connect
from my_twitter import my_twitter_get_api
from my_twitter import get_all_tweets
from my_twitter import twitter_update_user_followers
from my_twitter import guess_party_from_web

import urllib.request

from export import to_csv

from clas import clas
from clas import clas_load_words
from clas import clas_stats

from clas_anal import clas_anal_all

from re_tweet import re_tweet

from tweets_per_day import cal_tweets_per_day

from internal_external_tweets import internal_external_tweets

from topics import topics

from noun_anal import noun_anal

from time_on_twitter import time_on_twitter

if __name__ == '__main__':
	clas_load_words()
	my_twitter_connect()
	api = my_twitter_get_api()

	print("Start")

	last_batch_time=time.time()
	last_batch_time_hour=time.time()
	wait_time=0
	#last_batch_time=0

	while(1):
		delta=time.time()-last_batch_time
		delta_hour=time.time()-last_batch_time_hour
		print("delta=",delta)
		print("delta=",delta_hour)

		if abs(delta_hour)>60*60*4:
			last_batch_time_hour=time.time()
			hashtag_flow(cursor)

		if abs(delta)>6*60*60:
			last_batch_time=time.time()
			#time_domain_random_stats(cursor)
			#word_usage_graph(cursor)
			#hashtag_usage_graph(cursor)
			#at_usage_graph(cursor)

			#for friend in tweepy.Cursor(api.friends).items():
			#	# Process the friend here
			#	#print(friend.screen_name,friend.name)
			#	db_add_user(cursor,friend.screen_name,real_name=friend.name)

	#for ii in range(0, len(lines)):
		#all_users=db_get_all_users(cursor)
		#m=len(all_users)
		#ii=random.randint(0,m-1)
		#user=all_users[ii].rstrip()
		user=db_get_oldest_visited(cursor)
		db_visit_user(cursor,user)

		ret=0
		#try:
		ret=get_all_tweets(cursor,api,user)
		#except:
		#	pass

		#party=guess_party_from_text(api,user)
		#print("guessed party=",party)

		if ret!=0:
			twitter_update_user_followers(cursor,api,user)
			party=db_user_get_job1(cursor,user)
			if party=="" or party=="unknown":
				party=guess_party_from_web(user)
				print("guessed party=",party)
				db_user_update_job1(cursor,user,party)
			to_csv(cursor,user)
			to_stats(cursor,user)
		
		print("Waiting")
		time.sleep(wait_time)
		

	mariadb_connection.close()
	#sys.exit(0)
