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



def make_url_hist(cursor,party=""):
	max_days=365
	words_delete_all()
	users=db_get_cols_from_table(cursor,"user_names",["user_id","job_type1"])

	tweets=[]
	done=0
	v=[]

	for i in range(0,10):
		u=users[i][0]
		p=users[i][1]
		print(u,p)
		if p.startswith(party)==True:
			cur_time=time.time()
			tweets=db_get_cols_from_table(cursor,u,["date","url"])
			http=0
			urls=[]
			for ii in range(0,len(tweets)):
				date=int(tweets[ii][0])
				url=tweets[ii][1]

				if url!="None" and url!="error":
					if ((cur_time-date)/60/60/24)<max_days:
						address=url.split("/")[0]
						if address.startswith("www."):
							address=address[4:]
						word_add(address)



	word_clean()
	return words_ret_hist()



def remap(all,in_x,in_y):
	ret=[]
	for i in range(0,len(all)):
		val=0
		for ii in range(0,len(in_x)):
			if all[i]==in_x[ii]:
				val=in_y[ii]
				break
		ret.append(val)
	return ret

if __name__ == '__main__':
	db_set_mariadb_connection()
	cursor = db_get_mariadb_cursor()

	all,all_times=make_url_hist(cursor,party="")

	con,con_times=make_url_hist(cursor,party="con")
	con_times=remap(all,con,con_times)

	lab,lab_times=make_url_hist(cursor,party="lab")
	lab_times=remap(all,lab,lab_times)

	snp,snp_times=make_url_hist(cursor,party="snp")
	snp_times=remap(all,snp,snp_times)

	if len(all)>40:
		all=all[:40]
		con_times=con_times[:40]
		lab_times=lab_times[:40]
		snp_times=snp_times[:40]

	y_pos = np.arange(len(all))

	for_web=False

	plt.figure(figsize=(25.0, 10.0),dpi=300)
	#bars=plt.bar(y_pos, times,color="#36845b")
	bars=plt.bar(y_pos, con_times,color="#00539f")
	bars=plt.bar(y_pos, lab_times,bottom=con_times,color="#d50000")
	bars=plt.bar(y_pos, snp_times,bottom=snp_times,color="#fff685")


	plt.xticks(y_pos, all, fontsize=28)
	plt.legend(loc='best', fontsize=30)
	plt.ylabel('Usage', fontsize=30)
	plt.yscale('log', fontsize=30)
	plt.yticks(fontsize=30)
	plt.xticks(rotation=45, rotation_mode="anchor", ha="right")
	plt.tight_layout()
	plt.savefig('urls.png')
