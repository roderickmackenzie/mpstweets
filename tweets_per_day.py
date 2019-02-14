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

from operator import itemgetter
import time

from db import db_set_mariadb_connection
from db import db_get_mariadb_cursor

def setup_graph():
	plt.clf()

	plt.gcf().subplots_adjust(bottom=0.15)
	plt.figure(figsize=(5, 2.0),dpi=300)
	ax = plt.subplot(111)


	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.get_yaxis().set_visible(False)
	return ax

def cal_tweets_per_day(cursor):
	users=db_get_all_users(cursor)
		
	tweets=[]
	done=0
	v=[]
	update=False
	if update==True:
		for i in range(0,len(users)):
			u=users[i]
			print(u)	
			cur_time=time.time()
			tweets=db_get_cols_from_table(cursor,u,["date"])
			count=0
			for ii in range(0,len(tweets)):
				delta=(cur_time-int(tweets[ii][0]))/60/60/24
				if delta<100.0:
					count=count+1

			db_update_record(cursor,"user_names","user_id",u,"tweets_per_day",str(count/100.0))

			#v.append(count)

			db_commit()

	tweets_per_day=db_get_cols_from_table(cursor,"user_names",["tweets_per_day","job_type1"])

	con=[]
	lab=[]
	lib=[]
	snp=[]

	for i in range(0,len(tweets_per_day)):
		party=tweets_per_day[i][1]
		if party.startswith("con")==True:
			con.append(int(tweets_per_day[i][0]))

		if party.startswith("lab")==True:
			lab.append(int(tweets_per_day[i][0]))

		if party.startswith("lib")==True:
			lib.append(int(tweets_per_day[i][0]))

		if party.startswith("snp")==True:
			snp.append(int(tweets_per_day[i][0]))


		v.append(int(tweets_per_day[i][0]))

	m=60
	dx=1.0
	x=0.0
	xbins=[]
	while(x<m):
		xbins.append(x)
		x=x+dx

	for_web=False
	if for_web==True:
		plt.figure(figsize=(25.0, 6.0),dpi=300)
		plt.title("Tweets from MPs per day", fontsize=30)
		plt.gcf().subplots_adjust(bottom=0.15)

		plt.hist(v, bins=xbins, alpha=0.5,color='green')
		plt.hist(con, bins=xbins, alpha=0.8,color='blue')
		plt.hist(lab, bins=xbins, alpha=0.8,color='red')
		plt.hist(snp, bins=xbins, alpha=0.8,color='purple')
		plt.hist(lib, bins=xbins, alpha=0.8,color='yellow')

		plt.legend( ('All', 'Con', 'Lab','SNP',"Lib"), fontsize=25)

		plt.ylabel('Number of MPs', fontsize=25)
		plt.xlabel('Number of tweets/day', fontsize=25)

		plt.savefig("/var/www/html/graphs/tweets_per_day.png",bbox_inches='tight')
	else:


		matplotlib.rcParams['font.family'] = 'Open Sans'

		###############All#############
		plt.clf()
		plt.figure(figsize=(6.0, 6.0),dpi=300)
		ax = plt.subplot(111)

		#plt.title("Tweets from MPs per day", fontsize=30)
		plt.gcf().subplots_adjust(bottom=0.15)

		ax.spines['right'].set_visible(False)
		ax.spines['top'].set_visible(False)

		ax.hist(v, bins=xbins, alpha=1.0,color='#36845b')

		plt.ylabel('Number of MPs', fontsize=20)
		plt.xlabel('Number of tweets/day', fontsize=20)

		plt.savefig("./tweets_per_day/tweets_per_day_all.png",bbox_inches='tight')


		###############Con#############

		ax=setup_graph()
		axes = plt.gca()
		axes.set_ylim([0,40])
		plt.hist(con, bins=xbins, alpha=0.8,color="#00539f")


		#plt.legend( ( 'Con', 'Lab','SNP',"Lib"), fontsize=20)

		#plt.ylabel('Number of MPs', fontsize=20)
		#plt.xlabel('Number of tweets/day', fontsize=20)

		plt.savefig("./tweets_per_day/tweets_per_day_all_con.png",bbox_inches='tight')

		###############Lab#############

		ax=setup_graph()
		axes = plt.gca()
		axes.set_ylim([0,40])
		plt.hist(lab, bins=xbins, alpha=0.8,color="#d50000")

		#plt.legend( ( 'Con', 'Lab','SNP',"Lib"), fontsize=20)

		#plt.ylabel('Number of MPs', fontsize=20)
		#plt.xlabel('Number of tweets/day', fontsize=20)

		plt.savefig("./tweets_per_day/tweets_per_day_all_lab.png",bbox_inches='tight')

		###############SNP#############

		ax=setup_graph()
		axes = plt.gca()
		axes.set_ylim([0,40])
		plt.hist(snp, bins=xbins, alpha=0.8,color="#fff685")

		#plt.legend( ( 'Con', 'Lab','SNP',"Lib"), fontsize=20)

		#plt.ylabel('Number of MPs', fontsize=20)
		#plt.xlabel('Number of tweets/day', fontsize=20)

		plt.savefig("./tweets_per_day/tweets_per_day_all_snp.png",bbox_inches='tight')

		###############Lib#############

		ax=setup_graph()

		plt.hist(lib, bins=xbins, alpha=0.8,color='#faa01a')

		#plt.legend( ( 'Con', 'Lab','SNP',"Lib"), fontsize=20)

		#plt.ylabel('Number of MPs', fontsize=20)
		#plt.xlabel('Number of tweets/day', fontsize=20)

		plt.savefig("./tweets_per_day/tweets_per_day_all_lib.png",bbox_inches='tight')

if __name__ == '__main__':
	db_set_mariadb_connection()
	cursor = db_get_mariadb_cursor()
	cal_tweets_per_day(cursor)

