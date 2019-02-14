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
from words import word_add_array
from words import word_add_array_at

from db import db_get_all_users
from db import db_get_tweets_in_last_time
from db import db_user_get_job1

import numpy as np
from termcolor import colored
from nltk.stem.porter import *
import re

def re_tweet(cursor,delta=172800/2):
	words_delete_all()
	
	users=db_get_all_users(cursor)
	tweets=[]
	for u in users:
		#print(u)

		tweets=db_get_tweets_in_last_time(cursor,u,delta=1e10)
		tot=len(tweets)
		for i in range(0,len(tweets)):
			if tweets[i].startswith("RT @"):
				user=tweets[i].split(":")[0][3:]
				word_add_array_at(user)

		#word_clean()

		print(u)

	names,values=words_ret_hist(max_len=400)
	f=open('/var/www/html/stats/retweets.txt', 'w')
	print(names)
	for i in range(0,len(names)):
		ismp=users.count(names[i][1:])
		party=db_user_get_job1(cursor,names[i][1:])
		if party==None:
			party="notmp"
		#print (names[i][1:],party)
		out=names[i]+" "+str(values[i])+" "+str(ismp)+" "+party
		f.write(out+"\n")

	#print(names,values)

	f.close()

	aasdsad


