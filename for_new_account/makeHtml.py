#!/usr/bin/python
# -*- coding:utf-8 -*-

import sqlite3
import os
import ConfigParser
import sys

def makeHtml(page):

	#データベースに接続
	con = sqlite3.connect("data.db")
	#ディレクトリのデータを取得
	dirDB = con.execute(u"select * from Dir order by name desc")
	dirList = dirDB.fetchall()

	#データベースから必要な情報を取得
	if page == "top":
		pictureDB = con.execute(u"select * from Picture order by name")
		pictureList = pictureDB.fetchall()
	else:
		try:
			pictureDB = con.execute(u"select * from Picture where dir=? order by name",(page,))
			pictureList = pictureDB.fetchall()
			#ファイルの存在しないディレクトリへのアクセスの場合
			if len(pictureList)==0:
				print
				print "error occured"
				sys.exit()
		except:
			sys.exit()

	#htmlの初期表示
	print "Content-Type: text/html"
	print 

	#htmlの表示
	#ベースとなるhtmlを読み込む
	f = open("base.html")
	lines = f.readlines()
	#前後ページ名を格納する変数
	backpage = ""
	nextpage = ""

	for line in lines:

		#メニューの表示
		if line == "<!--MENULOOP-->\n":
			print '<li id="MENU01" class="menu-on"><a href="./">index</a></li>'
			for i in range(0,len(dirList)):
				print '<li id="MENU01"><a href="./index.cgi?dir='+ dirList[i][0].encode("utf-8")+'">',
				if (page == dirList[i][0]):
					print "<span style='font-weight:bold;'>" + dirList[i][0].encode("utf-8") + '...(' + unicode(dirList[i][1]).encode("utf-8") + ')</span>',

					#ついでにここで前後のページ先へのリンクも変数に格納
					if (len(dirList) == 1):
						break
					elif(i==0):
						nextpage = dirList[1][0]
					elif(i==len(dirList)-1):
						backpage = dirList[i-1][0]
					else:
						nextpage = dirList[i+1][0]
						backpage = dirList[i-1][0]

				else:
					print dirList[i][0].encode("utf-8") + '...(' + unicode(dirList[i][1]).encode("utf-8") + ')',
				print '</a></li>'

		#サムネイルの表示
		elif line == "<!--KIZILOOP-->\n":
			#トップページでない場合のみ写真を表示
			if page != "top":
				print '<div class="highslide-gallery" style="margin: auto">'

				for row in pictureList:

					print '	<a class="highslide" href="'+ row[1].encode("utf-8") + '" onclick="return hs.expand(this)">'
					print '		<img src="'+ row[2].encode("utf-8") + '" alt="' + row[4].encode("utf-8") +'" />'
					print '	</a>'
					print '		<div class="highslide-caption">'
					print '			<div align="right">original jpg data is <a href="'+row[0].encode("utf-8")+'">'+'here</a></div>'
					print '			<div align="right">raw data is <a href="'+row[0].encode("utf-8").split(".JPG")[0]+".NEF"+'">'+'here</a></div>'
					print '		</div>'

				print '</div>'
			#トップページでの表示内容
			else:
				print '<p>ようこそ</p>'

		#フッターの表示
		elif line == "<!--FOOTERLOOP-->\n" and False:
			print '<ul>'
			print '<li id="FOOTER01"><a href="#PAGETOP">PAGETOP</a></li>'
			print '</ul>'
			print 
		#その他変数の表示
		else:
			line = line.replace("%SITETITLE%","my photo")
			line = line.replace ("%PAGETITLE1%",page.encode("utf-8"))
			line = line.replace("%PAGETITLE2%",page.encode("utf-8"))
			if (nextpage!=""):
				line = line.replace("%BACKPAGE%",'<a href="./index.cgi?dir='+ nextpage.encode("utf-8") +'">前へ</a>' )
			else:
				line = line.replace("%BACKPAGE%",'前へ' )
			if (backpage!=""):
				line = line.replace("%NEXTPAGE%",'<a href="./index.cgi?dir='+ backpage.encode("utf-8") +'">次へ</a>' )
			else:
				line = line.replace("%NEXTPAGE%",'次へ' )
			print line,
	f.close()
	con.close()


if __name__ == "__main__":

	makeHtml()
