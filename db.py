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

import time
import tweepy
import csv
import os

import random
import mysql.connector as mariadb
import time
import sys

mariadb_connection=""

def db_added_in_24_hours(cursor,user):
	t=str(time.time()-24*60*60)
	cursor.execute("SELECT COUNT(1) FROM "+user+" WHERE date>"+t+";")
	count=0
	for table_name in cursor:
		value=str(table_name[0])

	command="update user_names set tweets_added=\'"+value+"\' where user_id=\'"+user+"\';"
	cursor.execute(command)

	
def db_get_deleted(cursor,user,id):
	cursor.execute("SELECT deleted from "+user+" WHERE tweet_id="+id+";")
	count=0
	for table_name in cursor:
		return str(table_name[0])

def db_set_tweets_deleted(cursor,user,ids,api):
	updated=0
	for id in ids:
		if db_get_deleted(cursor,user,id)=="0":
			cursor.execute("update "+user+" set deleted='1' where tweet_id="+id+";")
			text="DT from "+"#"+user+": "+db_get_tweet_text(cursor,user,id)
			updated=updated+1
			if len(text)>179:
				text=text[:179]
			#do_tweet(api,text)

	return updated

def db_show_mps():
	cursor.execute("SHOW TABLES;")
	for (table_name,) in cursor:
		print(table_name)

def db_add_mp(cursor,name):
	global mariadb_connection

	found=db_is_table(cursor,name)

	if found==False:
		cursor.execute("CREATE TABLE "+name+"( tweet_id BIGINT, date BIGINT, tweet VARCHAR(320), deleted INT, added_time INT, deleted_time INT, clas VARCHAR(100), PRIMARY KEY ( tweet_id ) );")
		#cursor.fetchall()
	mariadb_connection.commit()

def db_set_mariadb_connection():
	global mariadb_connection
	mariadb_connection = mariadb.connect(user='rod', password='5alignalign5', database='par')

def db_get_mariadb_connection():
	global mariadb_connection
	return

def db_get_mariadb_cursor():
	global mariadb_connection
	return mariadb_connection.cursor()

def db_get_all_users(cursor):
	ret=[]
	cursor.execute("SELECT user_id from user_names;")
	for table_name in cursor:
		ret.append(str(table_name[0]))

	return ret

def db_get_oldest_visited(cursor):
	ret=[]
	cursor.execute("SELECT user_id,date_visited from user_names;")
	min_user=""
	min_time=time.time()
	tot=0.0
	n=0
	for data in cursor:
		user=str(data[0])
		when=float(data[1])
		if when<min_time:
			min_time=when
			min_user=user
		tot=(tot-min_time)+when
		n=n+1.0
	print("avg update time",tot/n/60.0)
	return min_user

def db_visit_user(cursor,user):
	global mariadb_connection
	cursor.execute("update user_names set date_visited=\'"+str(time.time())+"\' where user_id=\'"+user+"\';")
	mariadb_connection.commit()

def db_update_record(cursor,tab,key_name,key,col,value):
	global mariadb_connection
	command="update "+tab+" set "+col+"=\'%s\' where "+key_name+"=\'"+key+"\';"

	cursor.execute(command, (value))

def db_commit():
	global mariadb_connection
	mariadb_connection.commit()

def db_count_deleted(cursor,user):
	value=""
	cursor.execute("SELECT COUNT(1) FROM "+user+" WHERE deleted = 1;")
	for table_name in cursor:
		value=str(table_name[0])

	command="update user_names set tweets_deleted=\'"+value+"\' where user_id=\'"+user+"\';"
	cursor.execute(command)

def db_is_date(cursor,tabel,date):
	cursor.execute("SELECT COUNT(1) FROM "+tabel+" WHERE date = "+str(date)+";")
	for table_name in cursor:
		return str(table_name[0])

def db_is_user(cursor,user):
	cursor.execute("SELECT COUNT(1) FROM user_names WHERE user_id = \""+user+"\";")
	for table_name in cursor:
		return str(table_name[0])

def db_get_col(cursor,table):
	command="SHOW COLUMNS FROM "+table+";"
	cursor.execute(command)
	ret=[]
	for data in cursor:
		ret.append(data[0])

	return ret

def db_is_col(cursor,table,col):
	cols=db_get_col(cursor,table)
	return col in cols

def db_add_col(cursor,table,col,length="1000"):
	global mariadb_connection
	cursor.execute("ALTER TABLE "+table+" \n ADD COLUMN "+col+" VARCHAR("+length+");")
	mariadb_connection.commit()
	 
 
def db_user_update_job1(cursor,user,job):
	global mariadb_connection
	if db_is_user(cursor,user)=="1":
		command="update user_names set job_type1=\'"+job+"\' where user_id=\'"+user+"\';"
		cursor.execute(command,(str(job)))
		mariadb_connection.commit()

def db_user_get_job1(cursor,user):
	global mariadb_connection
	if db_is_user(cursor,user)=="1":
		command="select job_type1 from user_names where user_id=\'"+user+"\';"
		cursor.execute(command)

	for table_name in cursor:
		return str(table_name[0])

def db_add_user_followers(cursor,name,followers):
	global mariadb_connection
	print("Add user followers")
	tab_name=name+"_fol"
	found=db_is_table(cursor,tab_name)
	if found==False:
		cursor.execute("CREATE TABLE "+tab_name+"( date BIGINT, followers BIGINT, PRIMARY KEY ( date ) );")

	t=time.time()
	day=24*60*60
	rounded_day = int(t - (t % day));

	if db_is_date(cursor,tab_name,rounded_day)=="0":
		print("here")
		command="INSERT INTO "+tab_name+" (date,followers ) VALUES (%s,%s);"
		cursor.execute(command,(str(rounded_day),str(followers)))
		mariadb_connection.commit()

def db_add_user(cursor,name,real_name=""):
	global mariadb_connection
	found=db_is_table(cursor,"user_names")
	if found==False:
		cursor.execute("CREATE TABLE user_names( user_id VARCHAR(100), real_name VARCHAR(100),job_type0 VARCHAR(100), job_type1 VARCHAR(100),  date_added BIGINT, date_visited BIGINT,  tweets_added BIGINT, tweets_deleted BIGINT, tweets_per_day INT, PRIMARY KEY ( user_id ) );")

	#print("exists",is_user(name))
	if db_is_user(cursor,name)=="0":
		command="INSERT INTO user_names (user_id,date_added,real_name ) VALUES (%s,%s,%s);"
		cursor.execute(command,(name,str(time.time()),str(real_name)))
		mariadb_connection.commit()

def db_get_tweet_text(cursor,user,id):
	cursor.execute("SELECT tweet from "+user+" WHERE tweet_id="+id+";")
	count=0
	for table_name in cursor:
		return str(table_name[0].strip())

def db_get_tweets_in_last_time(cursor,user,delta=172800/2):
	cursor.execute("select tweet from "+user+" where date>"+str(time.time()-delta)+";")
	count=0
	ret=[]
	for tweet in cursor:
		ret.append(tweet[0].strip())
	return ret

def db_get_cols_from_table(cursor,tab,cols):
	text=""
	for c in cols:
		text=text+c+","
	text=text[:-1]

	cursor.execute("select "+text+" from "+tab+";")
	count=0
	ret=[]
	for row in cursor:
		build=[]
		for r in row:
			build.append(str(r).strip())
		ret.append(build)
	return ret

def db_get_tweets_in_time_frame(cursor,user,width=1,time_ago=1):
	start=time.time()-(time_ago+width/2.0)*60*60
	stop=start+width*60.0*60.0
	cursor.execute("select tweet from "+user+" where date>"+str(start)+" AND date<"+str(stop)+";")
	count=0
	ret=[]
	for tweet in cursor:
		ret.append(tweet[0].strip())
	return ret

def db_is_table(cursor,name):
	found=False
	cursor.execute("SHOW TABLES")
	for (table_name,) in cursor:
		if table_name==name:
			found=True
	return found

def db_add_tweet(cursor,name,id,date,tweet,clas):
	global mariadb_connection
	try:
		tweet=tweet.replace('\'','\\\'')
		tweet=tweet.encode("unicode_escape")

		command="INSERT INTO "+name+" (tweet_id, date, tweet, deleted, added_time,deleted_time,clas) VALUES (%s, %s, %s, %s,%s, %s, %s);"
		cursor.execute(command,(id,date,tweet,"0",str(time.time()),"0",clas))
		mariadb_connection.commit()
		return True
	except:
		return False

def to_stats(cursor,name):
	deleted=db_count_deleted(cursor,name)
	print("deleted=",deleted)
	db_added_in_24_hours(cursor,name)

