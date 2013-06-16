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

FILETYPE1 = u".JPG"
FILETYPE2 = u".jpg"
LINK_PATH = u"./dat/link"
THUMB_PATH_L = u"./dat/thumb1"
THUMB_PATH_S = u"./dat/thumb2"
IMGPATH = u""

def initDB():
	#データベースにファイルを作る
	if not os.path.exists(u"data.db"):
		con = sqlite3.connect(u"data.db")
		con.execute(u"""
		create table Picture(
			path_orig varchar(128),
			path_link varchar(128),
			path_thumb1 varchar(128),
			path_thumb2 varchar(128),
			flag integer,
			last_update real,
			tags varchar(128),
			dir varchar(128),
			name varchar(128),
			primary key (path_orig)
		);
		""")
		con.execute(u"""
		create table Dir(
			path_orig varchar(128),
			flag integer,
			last_update varchar(128),
			date varchar(128),
			name varchar(128),
			fileNum integer,
			primary key (path_orig)
		);
		""")
	else:
		con = sqlite3.connect(u"data.db")
	con.close()

#データベースを更新
def updateDB():

	#データベースを開く
	con = sqlite3.connect(u"data.db")

	#データベース既存ファイルの存在確認のためのフラグ
	con.execute(u"update Picture set flag=0")
	con.execute(u"update Dir set flag=0")

	for i in range(2,len(sys.argv)):#カウントを２から初めているのはコマンドとIMGPATHを抜くため
		path_orig = sys.argv[i].decode("utf-8")
		#jpgファイル
		if os.path.isfile(path_orig) and ( (path_orig.find(FILETYPE1) != -1) or (path_orig.find(FILETYPE2) != -1) ):
			path_link = os.path.join(LINK_PATH,path_orig.split(IMGPATH)[1])
			path_thumb1 = os.path.join(THUMB_PATH_L,path_orig.split(IMGPATH)[1])
			path_thumb2 = os.path.join(THUMB_PATH_S,path_orig.split(IMGPATH)[1])
			dirname = os.path.dirname(path_orig)
			filename = os.path.basename(path_orig)
			try:
				#ファイルが存在しない場合データを作ってflag=1
				con.execute(u"insert into Picture values (?,?,?,?,1,?,'',?,?)",\
						(path_orig,\
						path_link,\
						path_thumb1,\
						path_thumb2,\
						0,\
						dirname,\
						filename))
			except:
				#ファイルが既に存在する場合flag=1
				con.execute(u"update Picture set flag=1 where path_orig=?",(path_orig,) )
		#ディレクトリ
		if os.path.isdir(path_orig):
			dirname = path_orig.split(IMGPATH)[1]
			fileNum = len(glob.glob(os.path.join(path_orig,u"*.jpg"))) + len(glob.glob(os.path.join(path_orig,u"*.JPG")))
			try:
				#ディレクトリが存在しない場合データを作ってflag=1
				con.execute(u"insert into Dir values (?,1,?,'',?,?)",\
					(path_orig,\
					0,\
					dirname,
					fileNum))
			except:
				#20111016 既存フォルダに追加時の写真枚数更新
				con.execute(u"update Dir set fileNum=? where path_orig=?",(fileNum,path_orig) )
				#ディレクトリが既に存在する場合flag=1
				con.execute(u"update Dir set flag=1 where path_orig=?",(path_orig,) )
	#存在しないファイル、ディレクトリに対するデータを削除
	con.execute(u"delete from Picture where flag=0")
	con.execute(u"delete from Dir where flag=0")

	#データをコミットしデータベースを閉じる
	con.commit()
	con.close()

#確認のためデータを表示
def printDB():
	#データベースに接続
	con = sqlite3.connect(u"data.db")

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


#サムネイル作成
#TODO存在しないファイル、ディレクトリの削除
def makeThumb():

	#データベースに取得（ファイル）
	con = sqlite3.connect(u"data.db")
	c = con.execute(u"select * from Picture")
	pictureList = c.fetchall()

	#データファイルツリー作成
	for fileInfo in pictureList:

		#親ディレクトリの作成
		upperDir_link = os.path.dirname(fileInfo[1])
		if not os.path.isdir(upperDir_link):
			os.makedirs(upperDir_link)
		upperDir_L = os.path.dirname(fileInfo[2])
		if not os.path.isdir(upperDir_L):
			os.makedirs(upperDir_L)
		upperDir_S = os.path.dirname(fileInfo[3])
		if not os.path.isdir(upperDir_S):
			os.makedirs(upperDir_S)

		#更新があった場合
		updateTime= os.path.getmtime(fileInfo[0])
		if updateTime > fileInfo[5]:

			#リンクの作成
			if not os.path.isfile(fileInfo[1].encode("utf-8")):
				os.symlink(os.path.abspath(fileInfo[0]).encode("utf-8"),fileInfo[1].encode("utf-8"))
			#NEF (raw data) サポート.とりあえずリンクだけ作っとく
			if not os.path.isfile(fileInfo[1].encode("utf-8").split(".JPG")[0] + ".NEF"):
				if os.path.isfile(os.path.abspath(fileInfo[0]).encode("utf-8").split(".JPG")[0] + ".NEF"):
					os.symlink(os.path.abspath(fileInfo[0]).encode("utf-8").split(".JPG")[0] + ".NEF",fileInfo[1].encode("utf-8").split(".JPG")[0] + ".NEF")

			#サムネイルの作成
			if (not os.path.isfile(fileInfo[2].encode("utf-8"))) or (not os.path.isfile(fileInfo[2].encode("utf-8"))) :
				print fileInfo[0]
				data = file(fileInfo[0]).read()
				imgL = imlib2.open_from_memory(data)
				imgS = imlib2.open_from_memory(data)
				newImgL = imgL.scale_preserve_aspect((800,800))
				imgS.thumbnail((150,150))

				try:
					exif = EXIF.process_file(open(fileInfo[1]),details=False,stop_tag=u"Image Orientation")
					if unicode(exif["Image Orientation"]) == u"Rotated 90 CW":
						imgS.orientate(1)
						newImgL.orientate(1)
					elif unicode(exif["Image Orientation"]) == u"Rotated 90 CCW":
						imgS.orientate(3)
						newImgL.orientate(3)
					elif unicode(exif["Image Orientation"]) == u"Rotated 180":
						imgS.orientate(2)
						newImgL.orientate(2)
				except:
					print "exif key error. Key \"Image Orientation\" not found. Exif information may not exist."
				newImgL.save(fileInfo[2].encode("utf-8"),"jpeg")
				imgS.save(fileInfo[3].encode("utf-8"),"jpeg")

			print "更新:", fileInfo[0]

			#更新時間データを更新
			con.execute(u"update Picture set last_update=? where path_orig=?",(updateTime,fileInfo[0]) )

	#データベース終了処理
	con.commit()
	con.close()

if __name__ == "__main__":

	#設定ファイルの読み込み
	inifile = ConfigParser.SafeConfigParser()
	inifile.read("./photo.conf")
	IMGPATH = inifile.get("path","IMGPATH").decode("utf-8")

	#メイン処理
	initDB()
	updateDB()
	#printDB()
	makeThumb()
