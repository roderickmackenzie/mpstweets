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


import time
import tweepy #https://github.com/tweepy/tweepy
import csv
import os

import random

import time
import sys
import hashlib
import shutil

from db import db_add_mp
from db import db_add_user
from db import db_add_tweet
from db import db_set_tweets_deleted
from db import db_add_user_followers
from db import db_update_record

from clas import clas_clas_text
api=None

class tweet():
	def __init__(self):
		self.time=""
		self.id=""
		self.changed=0
		self.deleted="0"

	def import_from_db(self,obj):
		#print(obj)
		self.id=str(obj[0])
		self.time=str(obj[1])
		self.deleted=str(obj[3])
		self.changed=0

def tweet_dump(data):
	for a in data:
		print(a.id,a.time,a.changed)

def tweet_check_off(data,id):
	for i in range(0,len(data)):
		#print(data[i].id,id)
		if data[i].id==id:
			data[i].changed=1
			#print("Founnd!!!!")
			break

def tweet_find_deleted(data):
	deleted=[]
	for i in range(0,len(data)):
		if data[i].changed==0:
			deleted.append(data[i].id)

	return deleted

def my_twitter_connect():
	global api
	#addasdas put in secrets here

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)


def my_twitter_get_api():
	global api
	return api

def my_twitter_tweet(text):
	global api
	status = api.update_status(status=text)

def guess_party_from_web(user):
	global api
	party="unknown"
	try:
		data=api.get_user(user)
	except:
		return "usernotfound"

	text=data.description.lower()
	print(data.description)

	if text.count("liberal Democrat")>0 or text.count("Lib Dem")>0 or text.count("@LibDems")>0:
		party="lib"

	elif text.count("labour")>0:
		party="lab"

	elif text.count("conservative")>0:
		party="con"

	elif text.count("@thesnp")>0 or text.count("snp")>0:
		party="snp"

	elif text.count("sinn féin")>0:
		party="sf"
	elif text.count("minister")>0 and text.count("shadow")==0:
		party="con"	
	elif text.count("democratic unionist party")>0 or text.count("dup")>0:
		party="dup"
	else:
		#ok so we have no clue.
		url=""
		text=""
		try:
			url=data.entities['url']['urls'][0]['expanded_url']
			print(url)
		except:
			pass
		if url!="":
			try:
				f = urllib.request.urlopen(url)
				text=f.read().lower()
			except:
				return party
			text=str(text, 'utf-8')
			print(type(text))
			#text=text.encode('utf-8')
			#except:
			#	pass
			con=text.count("conservative")
			lab=text.count("labour")
			print("con",con)
			print("lab",lab)
			if con+lab>0:
				if con>lab:
					party="con*"
				else:
					party="lab*"
				

			
		#if url!="":
		#	response = urllib2.urlopen('http://python.org/')
		#	html = response.read()
		#	print(html)

	return party

def last_200(cursor,name):
	command="SELECT * from "+name+";"
	cursor.execute(command)

	ids=[]	
	for table_name in cursor:
		a=tweet()
		a.import_from_db(table_name)
		ids.append(a)

	ids.reverse()
	if len(ids)>50:
		ids=ids[0:50]
	return ids

def get_all_tweets(cursor,api,user):
	db_add_user(cursor,user)
	db_add_mp(cursor,user)
	#db_visit_user(cursor,user)
	#Twitter only allows access to a users most recent 3240 tweets with this method
	
	#authorize twitter, initialize tweepy

	count=0
	added=0
	last=last_200(cursor,user)

	new_tweets=0
	while (1):
		print("getting tweets ",count,user)
		try:
			if count==0:
				tweets = api.user_timeline(screen_name = user,count=200)
			else:
				tweets = api.user_timeline(screen_name = user,count=200,max_id=oldest)
		except:
			print("Error getting tweets from user",user)
			return -1

		if count>0 and len(tweets)>0:
			tweets=tweets[1:]

		if len(tweets)==0:
			break

		count=count+1

		#del tweets[24]

		#for tweet in tweets:
		#	print(tweet.created_at)

		num_tweets=len(tweets)
		in_database=0
		for tweet in tweets:
			#print(type(tweet.created_at))	#time.mktime(d.timetuple())
			unix_time=time.mktime(tweet.created_at.timetuple())
			#print(tweet.created_at,time.ctime(unix_time))

			ret=db_add_tweet(cursor,user,tweet.id_str, str(unix_time), str(tweet.text),"unknown")
			tweet_check_off(last,tweet.id_str)
			#print(tweet.id_str,ret)
			if ret==False:
				in_database=in_database+1
			else:
				clas,tot,res=clas_clas_text(str(tweet.text))
				print(clas)
				db_update_record(cursor,user,"tweet_id",tweet.id_str,"clas",clas)
				new_tweets=new_tweets+1
			#	done_all=True
			#	break

		
			oldest = tweet.id

		print("new=",new_tweets,"downloaded=",num_tweets)
		if in_database==num_tweets:
			break
		#if done_all==True:
		#	print("Upto date for user ",user,"added",added)
		#	break


	#tweet_dump(last)
	deleted_tweets=tweet_find_deleted(last)
	print(deleted_tweets)
	n_deleted_tweets=db_set_tweets_deleted(cursor,user,deleted_tweets,api)

	return new_tweets+n_deleted_tweets

def twitter_update_user_followers(cursor,api,user):
	try:
		data=api.get_user(user)
	except:
		return
	followers=data.followers_count
	#print(data.followers_count)
	db_add_user_followers(cursor,user,followers)

def tweet_image(local_file_name,title):
	m = hashlib.md5()
	thumbs="/var/www/html/thumbs"
	filename, file_extension = os.path.splitext(local_file_name)
	m.update(str(time.time()).encode('utf-8'))
	random_file=m.hexdigest()+file_extension
	shutil.copyfile(local_file_name, os.path.join(thumbs,random_file))
	my_twitter_tweet(title+" http://mpstweets.com/usage.php?fname="+random_file)

	f = open(os.path.join(thumbs,random_file)+".txt", "w")
	f.write(title)
	f.close()


