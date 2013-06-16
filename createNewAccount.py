#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import glob
import sqlite3
from kaa import imlib2
import ConfigParser
sys.path.append("./exif-py")
import EXIF

FILETYPE = u".JPG"
LINK_PATH = u"./dat/link"
THUMB_PATH_L = u"./dat/thumb1"
THUMB_PATH_S = u"./dat/thumb2"
IMGPATH = u""

def makeNewDB():
	#データベースにファイルを作る
	DBpath = os.path.join(sys.argv[1],"data.db")
	if not os.path.exists(DBpath):
		con = sqlite3.connect(DBpath)
		con.execute(u"""
		create table Picture(
			path_link varchar(128),
			path_thumb1 varchar(128),
			path_thumb2 varchar(128),
			dir varchar(128),
			name varchar(128),
			primary key (path_link)
		);
		""")
		con.execute(u"""
		create table Dir(
			name varchar(128),
			fileNum integer,
			primary key (name)
		);
		""")
	else:
		con = sqlite3.connect(DBpath)
	con.close()

#データベースを更新
#TODO 更新の有無にかかわらず全データをアップデートしているので、オリジナル更新を確認してのDB更新
def updateDB():

	userName = sys.argv[1].decode("utf-8")

	#オリジナルデータベースを取得（ファイル）
	conOrig = sqlite3.connect(u"data.db")
	cOrig = conOrig.execute(u"select * from Picture where tags glob ?",(u"*_"+userName+u"*",))
	pictureListOrig = cOrig.fetchall()
	conOrig.close()

	#新しいアカウント用のデータベースのパス
	DBpath = os.path.join(sys.argv[1],"data.db")

	#データベースを開き、初期化
	con = sqlite3.connect(DBpath)
	con.execute(u"delete from Picture")
	con.execute(u"delete from Dir")

	for fileInfoOrig in pictureListOrig: 
	#jpgファイル
		path_link = fileInfoOrig[1]
		path_thumb1 = fileInfoOrig[2]
		path_thumb2 = fileInfoOrig[3]
		dirname = os.path.basename(fileInfoOrig[7])
		filename = fileInfoOrig[8]
		con.execute(u"insert into Picture values (?,?,?,?,?)",\
				(path_link,\
				path_thumb1,\
				path_thumb2,\
				dirname,\
				filename))

	for root,dirs,files in os.walk(os.path.join(userName,u"dat/link")):
		for dir in dirs:
			#ディレクトリ
			dirname = dir
			fileNum = len(glob.glob(os.path.join(os.path.join(root,dir),u"*.JPG"))) + len(glob.glob(os.path.join(os.path.join(root,dir),u"*.jpg")))
			con.execute(u"insert into Dir values (?,?)",\
				(dirname,\
				fileNum))
	#データをコミットしデータベースを閉じる
	con.commit()
	con.close()

#確認のためデータを表示
def printDB():
	userName = sys.argv[1].decode("utf-8")
	#データベースに接続
	con = sqlite3.connect(os.path.join(userName,u"data.db"))

	#ディレクトリデータ取得
	dirDB = con.execute(u"select * from Dir")
	dirList = dirDB.fetchall()
	for hoge in dirList:
		print hoge
	#ファイルデータ取得
	pictureDB = con.execute(u"select * from Picture")
	pictureList = pictureDB.fetchall()
	for hoge in pictureList:
		print hoge

	#データベースを閉じる
	con.close()


def makeNewAccount():
	
	#引数
	if(len(sys.argv)==1 or len(sys.argv)>2):
		print "アカウント名を正しく引数として渡してください。\n"
		sys.exit()
	else:
		userName = sys.argv[1].decode("utf-8")

	#ユーザーのディレクトリ作成
	if not os.path.isdir(userName):
		os.makedirs(userName)

	if not os.path.isfile(os.path.join(userName,"base.html")):
		os.symlink(os.path.abspath("./base.html"),os.path.join(userName,"base.html"))
	if not os.path.isdir(os.path.join(userName,"csstemplate")):
		os.symlink(os.path.abspath("./csstemplate"),os.path.join(userName,"csstemplate"))
	if not os.path.isfile(os.path.join(userName,"favicon.ico")):
		os.symlink(os.path.abspath("./favicon.ico"),os.path.join(userName,"favicon.ico"))
	if not os.path.isdir(os.path.join(userName,"highslide")):
		os.symlink(os.path.abspath("./highslide"),os.path.join(userName,"highslide"))
	if not os.path.isfile(os.path.join(userName,"index.cgi")):
		os.symlink(os.path.abspath("./for_new_account/index.cgi"),os.path.join(userName,"index.cgi"))
	if not os.path.isfile(os.path.join(userName,"makeHtml.py")):
		os.symlink(os.path.abspath("./for_new_account/makeHtml.py"),os.path.join(userName,"makeHtml.py"))
	if not os.path.isfile(os.path.join(userName,"makeHtml.pyc")):
		os.symlink(os.path.abspath("./for_new_account/makeHtml.pyc"),os.path.join(userName,"makeHtml.pyc"))

	#データベースを取得（ファイル）
	con = sqlite3.connect(u"data.db")
	c = con.execute(u"select * from Picture where tags glob ?",(u"*_"+userName+u"*",))
	pictureList = c.fetchall()

	#ファイルのリンクツリーを全削除
	for root,dirs,files in os.walk(os.path.join(userName,"dat"),topdown=False):
		for file in files:
			os.remove(os.path.join(root,file))
		for dir in dirs:
			os.rmdir(os.path.join(root,dir))

	#リンクツリーを作成
	for fileInfo in pictureList:
		
		#親ディレクトリの作成
		upperDir_link = os.path.dirname(os.path.join(userName,fileInfo[1]))
		if not os.path.isdir(upperDir_link):
			os.makedirs(upperDir_link)
		upperDir_L = os.path.dirname(os.path.join(userName,fileInfo[2]))
		if not os.path.isdir(upperDir_L):
			os.makedirs(upperDir_L)
		upperDir_S = os.path.dirname(os.path.join(userName,fileInfo[3]))
		if not os.path.isdir(upperDir_S):
			os.makedirs(upperDir_S)

		#リンクの作成
		if not os.path.isfile(os.path.join(userName,fileInfo[1])):
			os.symlink(os.path.abspath(fileInfo[1]),os.path.join(userName,fileInfo[1]))
		if not os.path.isfile(os.path.join(userName,fileInfo[2])):
			os.symlink(os.path.abspath(fileInfo[2]),os.path.join(userName,fileInfo[2]))
		if not os.path.isfile(os.path.join(userName,fileInfo[3])):
			os.symlink(os.path.abspath(fileInfo[3]),os.path.join(userName,fileInfo[3]))



	

if __name__ == "__main__":

	userName = sys.argv[1].decode("utf-8")

	#メイン処理
	makeNewAccount()
	makeNewDB()
	updateDB()
	#printDB()
	if not os.path.isfile(os.path.join(userName,".htaccess")):
		print """出来上がったユーザーに対するディレクトリに関しての.htaccessファイルを作成してください。
例）
AuthType Digest
AuthName "hoge"
Require valid-user

その後、sudo /usr/bin/htdigest /etc/apache2/.digest_passwd hoge "追加ユーザー名"
を実行。"""


