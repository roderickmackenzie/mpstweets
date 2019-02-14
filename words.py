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

from collections import Counter
import numpy as np
#import matplotlib.pyplot as plt
from operator import itemgetter, attrgetter

import glob
import nltk
from collections import defaultdict
from collections import OrderedDict
from operator import itemgetter


    
words=defaultdict(int)
class word:
	word=""
	n=""

def word_add_array(text):

		text = nltk.word_tokenize(text)
		result = nltk.pos_tag(text)
		for i in range(0,len(result)):
			t=result[i][0].lower()
			if t=="amp" or t.count("\\\\")!=0 or t.count("\\u")!=0:
				return
			if result[i][1][0]=="N":
				word_add(t)

def word_add_array_at(text):
		text=text.split()
		for w in text:
			if w.startswith("@"):
				word_add(w)

def word_add_array_hashtag(text):
		text=text.split()
		for w in text:
			if w.startswith("#"):
				if w.startswith("#\\")==False:
					word_add(w)

def check_ascii(mystring):
	#print(mystring)
	try:
		mystring.encode('ascii')
	except:
		return False
	else:
		return True

def word_add(word_in):
	if word_in=="https" or word_in=="http" or word_in=="@" or word_in=="rt" or word_in=="%":
		return
	#print(words)
	#print()
	words[word_in] += 1
#	i=word_search(word_in)
#	if i!=-1:
#		words[i].n=words[i].n+1
#	else:
#		b=word()
#		b.word=word_in
#		b.n=1
#		words.append(b)

def word_clean():
	global words
	#words = {x for x in words if check_ascii(x[0])==True }
	words={i:words[i] for i in words if check_ascii(i)==True}

def words_delete_all():
	global words
	words=defaultdict(int)

def word_print():
	print(words)


def words_ret_hist(max_len=150):
	global words
	names=[]
	values=[]
	#words.sort(key=attrgetter('n'),reverse=True)
	#print("words",words)
	ordered_words = OrderedDict(sorted(words.items(), key=itemgetter(1),reverse=True))

	m=len(ordered_words)
	if m>max_len:
		m=max_len

	k=list(ordered_words.keys())
	v=list(ordered_words.values())

	for i in range(0, m):
		if v[i]>0:
			names.append(k[i])
			values.append(v[i])

	return [names,values]
