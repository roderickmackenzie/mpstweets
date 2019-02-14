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

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from termcolor import colored
from nltk.stem.porter import *

from operator import itemgetter
import time
import random

days_in_past=365*2
lines = open('sen_'+str(days_in_past)+'_days.txt').read().splitlines()
all=[]
con=[]
lab=[]
delta=0.0
for i in range(0,len(lines)):
	s=lines[i].split()
	if float(s[0])!=0.0:
		all.append(float(s[0])+delta)
		con.append(float(s[1])+delta)
		lab.append(float(s[2])+delta)


m=len(all)
dx=1.0
x=0.0
xbins=[]
while(x<m):
	xbins.append(x)
	x=x+dx

matplotlib.rcParams['font.family'] = 'Open Sans'

plt.figure(figsize=(25.0, 6.0),dpi=300)
plt.gcf().subplots_adjust(bottom=0.15)

ax = plt.subplot(111)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

#plt.hist(health, bins=xbins, alpha=0.5,color='green')
#plt.hist(transport, bins=xbins, alpha=0.8,color='blue')
#plt.hist(education, bins=xbins, alpha=0.8,color='red')
#plt.hist(sci_env, bins=xbins, alpha=0.8,color='purple')

plt.plot(xbins, con, alpha=1.0,color="#00539f")
plt.plot(xbins, lab, alpha=1.0,color="#d50000")

plt.tick_params(axis='y', labelsize=25)
plt.tick_params(axis='x', labelsize=25)

plt.legend( ("Con","Lab"), fontsize=25)
plt.xlim((0, days_in_past+25)) 
plt.ylabel('Sentiment', fontsize=25)
plt.xlabel('Days in past', fontsize=25)

plt.savefig("sen_"+str(days_in_past)+".png",bbox_inches='tight')	#/var/www/html/graphs/



