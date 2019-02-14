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
import tweepy
import csv
import os

import random
import mysql.connector as mariadb
import time
import sys

from db import db_get_all_users
from db import db_visit_user
from db import db_add_user
from db import db_get_oldest_visited
from db import db_set_mariadb_connection
from db import db_user_update_job1
from db import db_user_get_job1
from db import to_stats
from word_usage_graph import word_usage_graph
from hashtag_usage_graph import hashtag_usage_graph
from at_usage_graph import at_usage_graph

from time_domain import time_domain

from hashtag_flow import hashtag_flow
from time_domain import time_domain_random_stats

mariadb_connection = mariadb.connect(user='rod', password='5alignalign5', database='par')
cursor = mariadb_connection.cursor()

db_set_mariadb_connection(mariadb_connection)

from my_twitter import my_twitter_connect
from my_twitter import my_twitter_get_api
from my_twitter import get_all_tweets
from my_twitter import twitter_update_user_followers
from my_twitter import guess_party_from_web
from db import db_get_tweets_in_last_time

import urllib.request

from export import to_csv

from clas import clas_load_words
from clas import clas_clas_text
from clas import class_get_files
from clas import class_add_and_save

from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5.QtWidgets import QTextEdit,QProgressBar, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt,QFile,QIODevice
from PyQt5.QtWidgets import QWidget,QSizePolicy,QVBoxLayout, QLabel, QHBoxLayout,QComboBox, QPushButton,QDialog, QFileDialog,QToolBar,QMessageBox, QLineEdit, QToolButton


class main(QMainWindow):
	def __init__(self):
		super(main,self).__init__()
		self.setMinimumSize(800,400)
		self.show()
		self.tweet_pos=0

		self.all_user_tweets=[]

		self.users=db_get_all_users(cursor)

		vbox=QVBoxLayout()

		self.status=QLabel("hello")

		hbox=QHBoxLayout()
		self.back=QPushButton("Back")
		self.back.clicked.connect(self.callback_back)
		self.next=QPushButton("Next")
		self.next.clicked.connect(self.callback_next)
		self.save=QPushButton("Save")
		self.save.clicked.connect(self.callback_save)

		self.prog=QProgressBar()

		hbox.addWidget(self.back)
		hbox.addWidget(self.next)
		hbox.addWidget(self.save)

		self.cb = QComboBox()
		self.cb.setStyleSheet("font: 24pt ;");

		self.cb_users = QComboBox()

		for file in class_get_files():
			self.cb.addItem(file)

		for u in self.users:
			self.cb_users.addItem(u)

		self.cb_users.currentIndexChanged.connect(self.callback_user_changed)

		h_button_widget=QWidget()
		h_button_widget.setLayout(hbox)

		self.display=QTextEdit()
		self.display.setStyleSheet("font: 24pt ;");
		self.display.cursorPositionChanged.connect(self.callback_cursor_move)

		vbox.addWidget(self.cb_users)
		vbox.addWidget(self.cb)
		vbox.addWidget(self.display)
		vbox.addWidget(h_button_widget)
		vbox.addWidget(self.status)
		vbox.addWidget(self.prog)

		wvbox=QWidget()
		wvbox.setLayout(vbox)

		self.setCentralWidget(wvbox)
		#self.get_next()

	def callback_cursor_move(self):
		self.selected=self.display.textCursor().selectedText().strip()

	def callback_save(self):
		file=self.cb.currentText()
		class_add_and_save(file,self.selected)
		print(file,"<",self.selected)
		self.callback_next()

	def callback_next(self):
		self.get_next_unkown_tweet()
		if self.tweet_pos>=len(self.all_user_tweets):
			self.tweet_pos=0

		self.status_update()

	def callback_back(self):
		self.get_last_unkown_tweet()
		if self.tweet_pos<0:
			self.tweet_pos=0
		self.status_update()

	def status_update(self):
		self.display.setText(self.all_user_tweets[self.tweet_pos])
		self.status.setText("pos="+str(self.tweet_pos)+"/"+str(len(self.all_user_tweets))+" known="+str(self.known)+"/"+str(len(self.all_user_tweets)))

	def callback_user_changed(self):
		u=self.cb_users.currentText()
		print(u)
		self.all_user_tweets=db_get_tweets_in_last_time(cursor,u,delta=1e10)
		self.tweet_pos=0
		self.known=0
		i=0
		for t in self.all_user_tweets:
			progress=float(i/len(self.all_user_tweets))*100.0		
			clas,tot,res=clas_clas_text(t)
			if tot!=0:
				self.known=self.known+1
			self.prog.setValue(progress)
			QApplication.processEvents()
			i=i+1

		self.get_next_unkown_tweet()
		self.status_update()


	def get_next_unkown_tweet(self):
		for i in range(self.tweet_pos+1,len(self.all_user_tweets)):
			t=self.all_user_tweets[i]
			clas,tot,res=clas_clas_text(t)
			if tot==0:
				print(i)
				self.tweet_pos=i
				self.status_update()
				return

	def get_last_unkown_tweet(self):
		for i in reversed(range(0,self.tweet_pos)):
			t=self.all_user_tweets[i]
			clas,tot,res=clas_clas_text(t)
			if tot==0:
				print(i)
				self.tweet_pos=i
				self.status_update()
				return

	def get_next(self,u):

		for t in self.all_user_tweets:
			clas,tot,res=clas_clas_text(t)
			if tot==0:
				self.display.setText(t)
				return
#					print(t,clas,tot,"res=",res)
#					input("hello")

if __name__ == '__main__':
	clas_load_words()
	app = QApplication(sys.argv)
	ex = main()
	sys.exit(app.exec_())




	mariadb_connection.close()

