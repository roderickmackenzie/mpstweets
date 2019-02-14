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

from words import word_add_array_hashtag
from words import check_ascii
from words import word_add
from words import word_clean
from words import word_print
from words import words_ret_hist
from words import words_delete_all

from db import db_get_all_users
from db import db_get_tweets_in_last_time
from db import db_get_col
from db import db_is_col
from db import db_add_col
from db import db_get_cols_from_table
from db import db_update_record
from db import db_commit

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from termcolor import colored
from nltk.stem.porter import *
import re
import os

from db import db_set_mariadb_connection
from db import db_get_mariadb_cursor


from operator import itemgetter
import time

db_set_mariadb_connection()

def get_tweet_time(cursor,u,st):
	tweets=db_get_cols_from_table(cursor,u,["date","tweet"])

	for ii in range(0,len(tweets)):
		t=tweets[ii][1]
		d=int(tweets[ii][0])
		if t.startswith(st)==True:
			return d

	return -1

def retweet_anal_to_flat_files(cursor):
	users=db_get_all_users(cursor)

	tweets=[]
	done=0
	v=[]

	if os.path.isdir("retweet_anal")==False:
		os.mkdir("retweet_anal")

	for i in range(0,len(users)):
		f=open(os.path.join("retweet_anal",users[i]), 'w')
		f.close()

	for i in range(0,len(users)):
		u=users[i]
		print(u)	
		cur_time=time.time()
		tweets=db_get_cols_from_table(cursor,u,["date","tweet"])
		rt=0
		origonal=0
		for ii in range(0,len(tweets)):
			t=tweets[ii][1]
			d=int(tweets[ii][0])

			if t.startswith("RT @"):
				user=t.split(":")[0][4:]
				if user in users:
					short=t
					if len(short)>100:
						short=short[:100]
					f=open(os.path.join("retweet_anal",user), 'a')
					f.write(str(d)+":"+short+"\n")
					f.close()
					#print(str(d),t)

def do_retweet_anal():
	cursor = db_get_mariadb_cursor()
	hist=[0] * 24
	users=db_get_all_users(cursor)
	data=[]
	for u in users:
		print(u)
		lines = open(os.path.join("retweet_anal",u)).read().splitlines()
		date=[]
		tweets=[]
		for l in lines:
			s=l.split(":")
			date.append(int(s[0]))
			tweets.append(s[2][1:])

		if len(tweets)>0:
			tweets, date = (list(t) for t in zip(*sorted(zip(tweets, date))))
			cur_t=""
			for i in range(0,len(tweets)):
				if cur_t!=tweets[i]:
					cur_t=tweets[i]
					start_time=get_tweet_time(cursor,u,tweets[i])
					#print(tweets[i],start_time)

				delta=int((date[i]-start_time)/60/60)
				data.append(delta)
		print(data)

	f=open("retweets.txt", 'w')
	for i in range(0,len(data)):
		f.write(str(data[i])+"\n")
	f.close()


lines = open("retweets.txt").read().splitlines()
data=[]
for l in lines:
	data.append(int(l))

x=0
dx=1
xbins=[]
while(x<500):
	xbins.append(x)
	x=x+dx


plt.figure(figsize=(6.0, 6.0),dpi=300)
plt.gcf().subplots_adjust(bottom=0.15)
plt.yscale('log', fontsize=30)
plt.xscale('log', fontsize=30)
#plt.hist(v, bins=xbins, alpha=0.5,color='green')
plt.hist(data, bins=xbins, alpha=0.8,color='green')

plt.ylabel('Retweets', fontsize=25)
plt.xlabel('Retweet delay (hours)', fontsize=25)

plt.savefig("anal.png",bbox_inches='tight')


#retweet_anal_to_flat_files(cursor)

