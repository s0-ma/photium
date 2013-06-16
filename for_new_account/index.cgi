#!/usr/bin/python
# -*- coding:utf-8 -*-

import makeHtml
import cgi
import sqlite3
import ConfigParser
import cgitb

if __name__ == "__main__":

	cgitb.enable()

	#CGI変数の取得(GET)
	f = cgi.FieldStorage()
	if f.has_key('dir') and f['dir'].value != '':
		page = f['dir'].value.decode("utf-8")
	else:
			page = u'top'

	makeHtml.makeHtml(page)

#	for k in f.keys():
#		#print "k=",k,"\nf[k].value=",f[k].value
#		line = u"update Picture set tags=" + unicode(f[k].value,"utf-8") + u" where dir=" + unicode(k,"utf-8")
#		print line
