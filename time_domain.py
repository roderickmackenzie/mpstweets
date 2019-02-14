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

from words import word_add_array
from words import check_ascii
from words import word_add
from words import word_clean
from words import word_print
from words import words_ret_hist
from words import words_delete_all

from db import db_get_all_users
from db import db_get_tweets_in_last_time

from my_twitter import tweet_image
from random import randint

import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import time
import random

from matplotlib.dates import MONDAY
from matplotlib.finance import quotes_historical_yahoo_ochl
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter

from hashtag_usage_graph import hashtag_get_most_used

days=356

epoch_end=time.time()-days*24*60*60

def user_make_hist(cursor,store,user,words=[]):
	global epoch_end

	for i in range(0,len(words)):
		words[i]=words[i].lower()

	command="SELECT date,tweet from "+user+" WHERE date>"+str(epoch_end)+";"
	cursor.execute(command)
	
	for data in cursor:
		date=data[0]
		tweet=data[1].lower()
		delta=int((epoch_end-date)/(24*60*60))
		if delta<len(store):
			if len(words)==0:
				store[delta]=store[delta]+1
			else:
				for w in words:
					if tweet.count(w)>0:
						store[delta]=store[delta]+1

def movingaverage(interval, window_size):
    window= numpy.ones(int(window_size))/float(window_size)
    return numpy.convolve(interval, window, 'same')

def time_domain(cursor,words=[]):
	print("Time domain",words)
	users=db_get_all_users(cursor)


	store = [0] * days
	store_float = [0.0] * days
	past=[]
	for i in range(0,len(store)):
		past.append(i)

	for user in users:
		user_make_hist(cursor,store,user,words=words)

	#print(store)

	####################



	date1 = epoch_end
	date2 = time.time()

	# every monday
	mondays = WeekdayLocator(MONDAY)

	# every 3rd month
	months = MonthLocator(range(1, 13), bymonthday=1, interval=3)
	monthsFmt = DateFormatter("%b '%y")


	####################
	title=",".join(words)
	plt.figure(figsize=(7.5, 4.0))
	plt.title("Tweets containing:"+title, fontsize=20)
	#plt.gcf().subplots_adjust(bottom=0.15)

	r = float(hash(title+"r") % 256) / 256 
	g = float(hash(title+"g") % 256) / 256
	b = float(hash(title+"b") % 256) / 256
	colors=(r,g,b)

	plt.bar(past,store, color=colors, edgecolor = "none")
	plt.ylabel('Tweets/day', fontsize=20)
	plt.xlabel('Time (days in past)', fontsize=25)

	#ax = plt.axes()

	#ax.xaxis.set_major_locator(months)
	#ax.xaxis.set_major_formatter(monthsFmt)
	#ax.xaxis.set_minor_locator(mondays)
	#ax.autoscale_view()

	#fig = plt.figure(1)
	#fig.autofmt_xdate()
	save_file="/var/www/html/graphs/time_domain.png"
	plt.savefig(save_file,bbox_inches='tight')

	tweet_image(save_file,title="The number of times MPs used the words '"+title+"' during the last year.")

def time_domain_random_stats(cursor):
	number=randint(0, 9)
	if number<2:
		lines = open('search_string.txt').read().splitlines()
		myline =random.choice(lines)
		myline=myline.split(",")
		time_domain(cursor,words=[myline])
	else:
		names,values=hashtag_get_most_used(cursor,delta=172800/2)
		if len(names)>0:
			new_list=[]
			for i in range(0,len(names)):
				if values[i]>3:
					new_list.append(names[i])

			if len(new_list)>1:
				myline =random.choice(new_list)
				time_domain(cursor,words=[myline])

