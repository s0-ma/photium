#!/usr/bin/python
# -*- coding:utf-8 -*-

import makeHtml
import cgi
import sqlite3
import ConfigParser
import cgitb

if __name__ == "__main__":

	cgitb.enable()

	#設定ファイルの読み込み
	inifile = ConfigParser.SafeConfigParser()
	inifile.read(u"./photo.conf")
	Config = inifile.getboolean("config","INPUTTAG")

	#CGI変数の取得(GET)
	f = cgi.FieldStorage()
	if f.has_key('dir') and f['dir'].value != '':
		page = f['dir'].value.decode("utf-8")
	else:
			page = u'top'
	if f.has_key('tag') and f['tag'].value != '':
		tag = f['tag'].value.decode("utf-8")
	else:
		tag = u''

	#タグの設定時
	if Config==True:
		#データベース接続
		con = sqlite3.connect(u"data.db")
		for k in f.keys():
			if (k != "dir") and (k != "tag"):
				con.execute(u"update Picture set tags=? where dir=?",(unicode(f[k].value,"utf-8"),unicode(k,"utf-8"),))
				con.execute(u"update Picture set tags=? where path_orig=?",(unicode(f[k].value,"utf-8"),unicode(k,"utf-8"),))
		con.commit()
		con.close()

	makeHtml.makeHtml(page,tag)

#	for k in f.keys():
#		#print "k=",k,"\nf[k].value=",f[k].value
#		line = u"update Picture set tags=" + unicode(f[k].value,"utf-8") + u" where dir=" + unicode(k,"utf-8")
#		print line
