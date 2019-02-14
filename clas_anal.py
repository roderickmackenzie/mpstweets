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

def clas_anal_all(cursor):
	clas_anal(cursor,"brexit")
	clas_anal(cursor,"econ")
	clas_anal(cursor,"health")
	clas_anal(cursor,"international")
	clas_anal(cursor,"party")
	clas_anal(cursor,"sci_env")
	clas_anal(cursor,"terror")
	clas_anal(cursor,"defence")
	clas_anal(cursor,"education")
	clas_anal(cursor,"home_aff")
	clas_anal(cursor,"misc")
	clas_anal(cursor,"science")
	clas_anal(cursor,"sport")
	clas_anal(cursor,"transport")

def clas_anal(cursor,search):
	output_path="/var/www/html/interests"
	output_file=os.path.join(output_path,search+".txt")

	ret=[]
	c=db_get_cols_from_table(cursor,"user_names",["user_id","clas"])
	for i in range(0,len(c)):
		u=c[i][0]
		data=c[i][1].split(";")
		for d in data:
			if d.startswith(search)==True:
				d=d.split("=")[1]	
				ret.append([u,int(d)])
	s = sorted(ret, key=lambda tup: tup[1],reverse=True)

	f=open(output_file, 'w')

	for i in range(0,len(s)):
		f.write(s[i][0]+" "+str(s[i][1])+"\n")

	f.close()

	print(s)
