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


import re
import os
import sys
sys.path.append('./sen/')
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


from operator import itemgetter
import time
import random

from sentiment_mod import sentiment

def sen_run_over_db(cursor):
	users=db_get_all_users(cursor)
	
	tweets=[]
	cur_time=time.time()
	done=0
	for i in range(0,len(users)):
		u=users[i]
		print(u,i,len(users))

		if db_is_col(cursor,u,"sen")==False:
			db_add_col(cursor,u,"sen")
			print("adding")
	


		tweets=db_get_cols_from_table(cursor,u,["tweet_id","tweet","sen","date"])

		for t in tweets:
			delta=int((cur_time-int(t[3]))/60/60/24)
			#print(delta)
			if delta<365*2:
				if t[2]=="None":
					st=t[1].replace("\\\\","")

					s=sentiment(st)
					print(".", end='', flush=True)
					#print(t[1],s,"new")
					db_update_record(cursor,u,"tweet_id",t[0],"sen",str(s))
					#db_commit()
			#else:
			#	print(t[2])
		print("")
		db_commit()


def sen(cursor):
	users_party=db_get_cols_from_table(cursor,"user_names",["user_id","job_type1"])
	users=[]
	party=[]
	for i in range(0,len(users_party)):
		users.append(users_party[i][0])
		party.append(users_party[i][1])

	tweets=[]
	done=0
	v=[]
	update=True
	days_in_past=365*2
	if update==True:
		all=[0] * days_in_past
		all_tot=[0] * days_in_past

		con=[0] * days_in_past
		con_tot=[0] * days_in_past

		lab=[0] * days_in_past
		lab_tot=[0] * days_in_past

		all_out=[0] * days_in_past
		con_out=[0] * days_in_past
		lab_out=[0] * days_in_past

		for i in range(0,int(len(users))):
			u=users[i]
			p=party[i]
			print(u,p,i,len(users))	
			cur_time=time.time()
			tweets=db_get_cols_from_table(cursor,u,["date","tweet","sen"])

			for ii in range(0,len(tweets)):
				t=tweets[ii][1]
				delta=int((cur_time-int(tweets[ii][0]))/60/60/24)
				if delta<days_in_past:

					string_s=tweets[ii][2]
					if string_s!="None":
						s=float(string_s)
						#s=sentiment(t)
						#print(ii,len(tweets),t,s)
						all[delta]+=s
						all_tot[delta]+=1

						if p.startswith("con")==True:
							con[delta]+=s
							con_tot[delta]+=1

						if p.startswith("lab")==True:
							lab[delta]+=s
							lab_tot[delta]+=1

			for i in range(0,len(all)):
				div=all_tot[i]
				if div!=0:
					all_out[i]=all[i]/div

				div=con_tot[i]
				if div!=0:
					con_out[i]=con[i]/div

				div=lab_tot[i]
				if div!=0:
					lab_out[i]=lab[i]/div


			f=open("sen_"+str(days_in_past)+"_days.txt", 'w')
			for i in range(0,len(all)):
				f.write(str(all_out[i])+" "+str(con_out[i])+" "+str(lab_out[i])+"\n")

			f.close()

if __name__ == '__main__':
	db_set_mariadb_connection()
	cursor = db_get_mariadb_cursor()
	#sen_run_over_db(cursor)
	sen(cursor)
	#sen(cursor)
