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

def time_on_twitter(cursor):
	users=db_get_all_users(cursor)

	tweets=[]
	done=0
	v=[]
	rt=0
	origonal=0

	for i in range(0,len(users)):
		u=users[i]
		print(u)	
		cur_time=time.time()
		tweets=db_get_cols_from_table(cursor,u,["date","tweet"])

		for ii in range(0,len(tweets)):
			t=tweets[ii][1]
			delta=(cur_time-int(tweets[ii][0]))/60/60/24
			if delta<365:
				if t.startswith("RT "):
					rt=rt+1
				else:
					origonal=origonal+1

		print(origonal,rt,len(users),(origonal*30.0+rt*10.0)/60/60)
