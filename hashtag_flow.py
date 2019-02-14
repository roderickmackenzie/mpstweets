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
from db import db_get_tweets_in_time_frame

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import glob, os
from matplotlib import cm

import time
import os
import hashlib
import shutil

from my_twitter import my_twitter_tweet

def hashtag_flow(cursor):
	print("making hashtag flow graph")
	path="/var/www/html/graphs/"
	thumbs="/var/www/html/thumbs"
	if os.path.isdir(thumbs)==False:
		os.mkdir(thumbs)

	os.chdir("/var/www/html/graphs/")
	for f in glob.glob("hashtag_flow*.png"):
		os.remove(f)

	file_number=0
	ago=0.0
	pngs=""
	plt.figure(figsize=(8.0, 4.0))
	#color = cm.inferno_r(np.linspace(.4,.8, 20))
	loop=0
	pop_hash_tags=""

	while(ago<48):
		print("ago=",ago)
		words_delete_all()
		users=db_get_all_users(cursor)
		tweets=[]
		for u in users:
			tweets=db_get_tweets_in_time_frame(cursor,u,width=4,time_ago=ago)
			for i in range(0,len(tweets)):
				word_add_array_hashtag(tweets[i])

		word_clean()
		names,values=words_ret_hist()
		if len(names)>=10:
			names=names[:10]
			values=values[:10]
			names.reverse()
			values.reverse()

			if loop==0:
				pop_hash_tags=" ".join(names)

			color=[]
			#names[5]="#brexit"
			for i in range(0,len(names)):
				names[i]=names[i].strip().lower()
				r = float(hash(names[i]+"r") % 256) / 256 
				g = float(hash(names[i]+"g") % 256) / 256
				b = float(hash(names[i]+"b") % 256) / 256
				color.append([r,g,b,1.0])
				#print(names[i],(r,g,b,1.0))
			#print(color)

			#word_print()

			y_pos = np.arange(len(names))
			 #,dpi=300 figsize=(25.0, 16.0)
			plt.cla()
			bars=plt.barh(y_pos, values, align='center',color=color)
			plt.yticks(y_pos, names)
			t=time.time()
			t=t-ago*60*60
			ago_to_2dp="%.2f" %  ago
			plt.title("Number of tweets "+str(ago_to_2dp)+" hours ago from MPs")
			plt.xlabel('Tweets')
			plt.xlim([0,40])
			plt.xticks(rotation='vertical')
			plt.subplots_adjust(left=0.35, right=0.95, top=0.9, bottom=0.2)
			plt.savefig('/var/www/html/graphs/hashtag_flow'+str(file_number)+'.png')
			pngs=pngs+" hashtag_flow"+str(file_number)+'.png'
			file_number=file_number+1
		ago=ago+0.25
		loop=loop+1


	os.system("convert -delay 30 -loop 0 -quality 50% "+pngs+" hashtag_flow.gif")
	m = hashlib.md5()
	m.update(str(time.time()).encode('utf-8'))
	random_file=m.hexdigest()+".gif"
	shutil.copyfile(os.path.join(path,"hashtag_flow.gif"), os.path.join(thumbs,random_file))
	my_twitter_tweet("Top hashtags used by MPs in last 48 hours: http://mpstweets.com/flow.php?fname="+random_file+" "+pop_hash_tags)

	#os.system("ffmpeg -y -f image2 -r 6 -i 'hashtag_flow%d.png' output.mp4")
	#os.system("ffmpeg -y -i output.mp4 -c:v libvpx -qmin 0 -qmax 25 -crf 4 -b:v 1M -vf scale=1280:-2 -an -threads 0 output.webm")


