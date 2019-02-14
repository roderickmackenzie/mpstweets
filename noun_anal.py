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
import sys

from operator import itemgetter
import time

import http.client
import urllib.parse
from urllib.request import urlopen

from words import word_add_array

from db import db_set_mariadb_connection
from db import db_get_mariadb_cursor

def noun_anal(cursor):
	words_delete_all()

	users=db_get_all_users(cursor)

	tweets=[]
	v=[]
	update=False

	if update==True:
		print(len(users))
		for i in range(0,len(users)):
			u=users[i]
			print(i,u)	
			cur_time=time.time()
			tweets=db_get_cols_from_table(cursor,u,["tweet","date"])

			for ii in range(0,len(tweets)):
				t=tweets[ii][0]
				date=int(tweets[ii][1])
				if ((cur_time-date)/60/60/24)<100.0:
					#print(t)
					word_add_array(t)

		names,values=words_ret_hist()
		f = open('noun_hist.dat', 'w')
		for i in range(0,len(names)):
			f.write(names[i]+" "+str(values[i])+"\n")
		f.close()

	lines = open('noun_hist.dat').read().splitlines()
	http=[]
	times=[]
	for i in range(0,len(lines)):
		a=lines[i].split()
		http.append(a[0])
		times.append(int(a[1]))
		if i>15:
			break

	http.reverse()
	times.reverse()

	y_pos = np.arange(len(http))

	for_web=False
	if for_web==True:
		plt.figure(figsize=(25.0, 16.0),dpi=300)
		bars=plt.bar(y_pos, times,color="blue")

		plt.xticks(y_pos, http, fontsize=35)
		plt.legend(loc='best', fontsize=30)
		plt.ylabel('Usage (Tweets)', fontsize=30)
		#plt.yscale('log', fontsize=30)
		plt.yticks(fontsize=30)
		plt.xticks(rotation=45, rotation_mode="anchor", ha="right")
		plt.tight_layout()
		plt.savefig('/var/www/html/graphs/nouns.png')
	else:
		plt.figure(figsize=(10.0, 10.0),dpi=300)

		ax = plt.subplot(111)
		ax.spines['right'].set_visible(False)
		ax.spines['top'].set_visible(False)

		bars=plt.barh(y_pos, times,color="#36845b")
		for tick in ax.xaxis.get_major_ticks():
			tick.label.set_fontsize(25) 

		plt.yticks(y_pos, http, fontsize=25)
		plt.xticks(rotation=45, rotation_mode="anchor", ha="right")
		plt.legend(loc='best', fontsize=25)
		plt.xlabel('Usage (Tweets)', fontsize=25)
		#plt.yscale('log', fontsize=30)
		plt.tight_layout()
		plt.savefig('nouns.png')

if __name__ == '__main__':
	db_set_mariadb_connection()
	cursor = db_get_mariadb_cursor()
	noun_anal(cursor)
