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
# Go through the data base of all tweets and resolve all urls, storing the resolved url back in the db. 
# It will run up 40 or so threads to do this.

from db import db_get_all_users
from db import db_get_tweets_in_last_time
from db import db_get_col
from db import db_is_col
from db import db_add_col
from db import db_get_cols_from_table
from db import db_update_record
from db import db_commit

from db import db_set_mariadb_connection
from db import db_get_mariadb_cursor

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from termcolor import colored
from nltk.stem.porter import *
import re
import os

from operator import itemgetter
import time


from operator import itemgetter
import time

import http.client
import urllib.parse
from urllib.request import urlopen

import threading
import queue



def read_url(url, q):
	try:
		data=urlopen(url[0]).geturl()
		#print('Fetched %s from %s' % (len(data), data))
		q.put([data,url[1]]) 
		print(".", end='', flush=True)

	except KeyboardInterrupt:
		sys.exit()
	except:
		q.put(["error",url[1]]) 
		return



def fetch_parallel(urls):
	q = queue.Queue()
	threads = [threading.Thread(target=read_url, args = (url,q)) for url in urls]
	for t in threads:
		t.start()
		#print(t)

	for t in threads:
		t.join()

	l=[]
	while not q.empty():
		item = q.get()
		l.append(item)

	return l




def short_to_long_over_db(cursor):
	max_days=365

	users=db_get_all_users(cursor)

	tweets=[]
	done=0
	v=[]

	for i in range(0,len(users)):
		u=users[i]
		print(u)
		if db_is_col(cursor,u,"url")==False:
			db_add_col(cursor,u,"url",length="1000")
			print("adding url")

		cur_time=time.time()
		tweets=db_get_cols_from_table(cursor,u,["date","tweet","url","tweet_id"])
		http=0
		urls=[]
		for ii in range(0,len(tweets)):
			date=int(tweets[ii][0])
			t=tweets[ii][1]
			url=tweets[ii][2]
			id=tweets[ii][3]
			if url=="None":
				if ((cur_time-date)/60/60/24)<max_days:
					ret=re.search("(?P<url>https?://[^\s]+)", t)
					if ret!=None:
						ret=ret.group("url")
						if ret.count("\\u2026")==0:
							urls.append([ret,id])

			#print(urls)
			if len(urls)>40 or (len(urls)>0 and ii==len(tweets)-1):
				#print("fetch",urls)
				urls_out=fetch_parallel(urls)
				#print("fetch..")

				for iii in range(0,len(urls_out)):
					if urls_out[iii][0]!="error":
						if urls_out[iii][0].startswith('https://'):
							urls_out[iii][0] = urls_out[iii][0][8:]
						if urls_out[iii][0].startswith('http://'):
							urls_out[iii][0] = urls_out[iii][0][7:]

						if len(urls_out[iii][0])>1000:
							urls_out[iii][0]=urls_out[iii][0][:1000]

						#print(urls[iii][0])
						#print(urls_out[iii][0])
						#print()
					#print(urls_out[iii])
					db_update_record(cursor,u,"tweet_id",urls_out[iii][1],"url",urls_out[iii][0])
					db_commit()

				urls=[]
				ids=[]

if __name__ == '__main__':
	db_set_mariadb_connection()
	cursor = db_get_mariadb_cursor()
	short_to_long_over_db(cursor)

