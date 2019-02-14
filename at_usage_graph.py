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


from words import word_add_array_at
from words import check_ascii
from words import word_add
from words import word_clean
from words import word_print
from words import words_ret_hist
from words import words_delete_all

from db import db_get_all_users
from db import db_get_tweets_in_last_time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def at_usage_graph(cursor):
	print("making @ graph")
	words_delete_all()
	users=db_get_all_users(cursor)
	tweets=[]
	for u in users:
		tweets=db_get_tweets_in_last_time(cursor,u)
		for i in range(0,len(tweets)):
			word_add_array_at(tweets[i])

	word_clean()
	names,values=words_ret_hist()
	names=names[:20]
	values=values[:20]
	names.reverse()
	values.reverse()
	#word_print()

	y_pos = np.arange(len(names))

	plt.figure() #,dpi=300 figsize=(25.0, 16.0)
	bars=plt.barh(y_pos, values, align='center')

	plt.yticks(y_pos, names)
	plt.xlabel('Usage')
	plt.xticks(rotation='vertical')
	plt.savefig('/var/www/html/graphs/at_usage.png', bbox_inches='tight')

