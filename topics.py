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

def topics(cursor):
	users=db_get_all_users(cursor)

	tweets=[]
	done=0
	v=[]
	update=True
	days_in_past=200
	cur_time=time.time()-7*24*60*60
	if update==True:
		brexit=[0] * days_in_past
		defence=[0] * days_in_past
		econ=[0] * days_in_past
		education=[0] * days_in_past
		health=[0] * days_in_past
		home_aff=[0] * days_in_past
		international=[0] * days_in_past
		misc=[0] * days_in_past
		party=[0] * days_in_past
		sci_env=[0] * days_in_past
		sport=[0] * days_in_past
		terror=[0] * days_in_past
		transport=[0] * days_in_past

		for i in range(0,int(len(users)/1)):	#
			u=users[i]
			print(u)	

			tweets=db_get_cols_from_table(cursor,u,["date","clas"])
			#internal=0
			#external=0


			for ii in range(0,len(tweets)):
				c=tweets[ii][1]
				delta=int((cur_time-int(tweets[ii][0]))/60/60/24)
				if delta<days_in_past:
					if c=="health":
						health[delta]+= 1
					elif c=="transport":
						transport[delta]+= 1
					elif c=="education":
						education[delta]+= 1
					elif c=="sci_env" or c=="science":
						sci_env[delta]+= 1	
					elif c=="party":
						party[delta]+= 1
					elif c=="brexit":
						brexit[delta]+= 1

	m=days_in_past
	dx=1.0
	x=0.0
	xbins=[]
	while(x<m):
		xbins.append(x)
		x=x+dx

	matplotlib.rcParams['font.family'] = 'Open Sans'

	plt.figure(figsize=(25.0, 6.0),dpi=300)


	ax = plt.subplot(111)
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)

	plt.gcf().subplots_adjust(bottom=0.15)

	plt.semilogy(xbins, health, alpha=1.0,color="#36845b")
	plt.semilogy(xbins, transport, alpha=1.0,color="#a3d9bc")
	plt.semilogy(xbins, education, alpha=1.0,color="#808080")
	plt.semilogy(xbins, sci_env, alpha=1.0,color="#305496")
	plt.semilogy(xbins, party, alpha=1.0,color="#ffc000")
	plt.tick_params(axis='y', labelsize=25)
	plt.tick_params(axis='x', labelsize=25)

	plt.legend( ('Health',"Transport","Education","Science/Env","Political"), fontsize=25)
	plt.xlim((0, 225)) 
	plt.ylabel('Number of tweets', fontsize=25)
	plt.xlabel('Days in past', fontsize=25)

	plt.savefig("topics.png",bbox_inches='tight')

if __name__ == '__main__':
	db_set_mariadb_connection()
	cursor = db_get_mariadb_cursor()
	topics(cursor)


