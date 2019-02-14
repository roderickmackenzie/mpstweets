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

files=[]
words=[]
path="./words/"
def clas_load_words():
	global files
	global words
	global path
	listing=os.listdir(path)
	for file in listing:
		lines = open(os.path.join(path,file)).read().splitlines()
		lines= list(filter(None, lines))

		new_lines=[]
		for l in lines:
			new_lines.append(l.split())
		lines=new_lines
 
		files.append(file)
		words.append(lines)

def class_get_file_number(f):
	global files
	global words
	for i in range(0,len(files)):
		if files[i]==f:
			return i

	return -1

def calss_save_word_file(number):
	global words
	global files
	global path
	out_file=os.path.join(path,files[number])
	f=open(out_file, 'w')

	for w in words[number]:
		f.write(" ".join(w)+"\n")

	f.close()

def class_add_and_save(file_name,new_words):
	global words
	global files
	f_num=class_get_file_number(file_name)
	val=my_match(new_words,words[f_num])
	if val==0:
		words[f_num].append(new_words.lower().split())

	print(words[f_num])
	calss_save_word_file(f_num)
def class_get_files():
	global files
	return files

def my_match(text,words_in):

	stemmer = PorterStemmer()
	text=re.sub(r'[^a-zA-Z0-9 ]', '', text)
	#print(text)
	words=[]
	plurals=text.lower().split()
	for i in range(0,len(words_in)):
		words.append([stemmer.stem(plural) for plural in words_in[i]])

	t = [stemmer.stem(plural) for plural in plurals]
	n=0
	#print(t)
	for i in range(0,len(t)):
		for ii in range(0,len(words)):
			if t[i]==words[ii][0]:
				match=0
				for s in range(0,len(words[ii])):
					if i+s<len(t):
						if words[ii][s]==t[i+s]:
							match=match+1
				if match==len(words[ii]):
					n=n+1

	return n

def clas_clas_text(text):
	global files
	global words
	res=[]
	for i in range(0,len(files)):
		vals=my_match(text,words[i])
		res.append([files[i][0:-4],vals])	

	clas="unknown"
	m=0
	tot=0
	for i in range(0,len(res)):
		if res[i][1]>m:
			m=res[i][1]
			clas=res[i][0]
		tot=tot+res[i][1]

	return clas,tot,res

def clas_stats(cursor):
	users=db_get_all_users(cursor)
	for u in users:
		print(u)
		words_delete_all()
		c=db_get_cols_from_table(cursor,u,["clas"])
		for w in c:
			#print(w)
			word_add(w[0])

		words=words_ret_hist()
		w=""
		for i in range(0,len(words[0])):
			w=w+words[0][i]+"="+str(words[1][i])+";"
		w=w[:-1]
		db_update_record(cursor,"user_names","user_id",u,"clas",w)
		db_commit()
		print(w)
	adas

def clas(cursor,delta=172800/2):
	users=db_get_all_users(cursor)
		
	tweets=[]
	#users=["JoJohnsonUK"]
	done=0
	for i in range(271,562):
		u=users[i]
		print(u,i,len(users))
		#ada
		if db_is_col(cursor,u,"clas")==False:
			db_add_col(cursor,u,"clas")
			print("adding")
	

		tweets=db_get_cols_from_table(cursor,u,["tweet_id","tweet"])

		for t in tweets:
			clas,tot,res=clas_clas_text(t[1])
			db_update_record(cursor,u,"tweet_id",t[0],"clas",clas)
			#print(clas)
			#print(t)

		db_commit()

		#adas			
	types=None
	if tot!=0:
		m=len(tweets)
		if m>500:
			m=500

		for i in range(0,m):

			#print(tweets[i])
			out=clas_clas_text(tweets[i])
			if types==None:
				types=res
			else:
				#print(types)
				for ii in range(0,len(res)):
					types[ii][1]=types[ii][1]+res[ii][1]
			if out!="unknown":
				clas=clas+1

		path="/var/www/html/interests/"+u+".txt"
		#print(types)

		#asadasds

		if clas!=0:
			types=sorted(types,key=itemgetter(1),reverse=True)

			sum_ids=0
			for i in range(0,len(types)):
				sum_ids=sum_ids+types[i][1]

			clas_perent=100.0*(clas/tot)
			print(u,types,clas_perent)
			f=open(path, 'w')
			for i in range(0,len(types)):
				f.write(types[i][0]+" "+str(int((types[i][1]/sum_ids)*100.0))+"\n")

			#f.write("clas "+str(int(clas_perent))+"\n")

			f.close()

		#adas


