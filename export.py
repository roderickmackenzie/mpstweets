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
import mysql.connector as mariadb
import time
import sys

def to_csv(cursor,name):
	path="/var/www/html/data/"
	command="SELECT * from "+name+";"
	cursor.execute(command)
	f=open(path+name+'.txt', 'w')

	all=[]
	for table_name in cursor:
		line=str(table_name[0])+","+time.ctime(int(table_name[1]))+","+str(table_name[3])+","+table_name[2]
		all.append(line)

	#all.reverse()
	for i in range(0,len(all)):
		ii=len(all)-1-i
		f.write(all[ii]+"\n")

	f.close()

	os.chdir(path)
	os.system("zip "+name+".zip "+name+".txt")
	os.remove(path+name+".txt")


