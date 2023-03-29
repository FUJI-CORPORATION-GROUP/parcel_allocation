# -*-coding: Shift_JIS -*-
import math
import sys
import re
import os
#文字列の長さを返す
def size(moji):
	return len(moji.encode("SHIFT-JIS"))
#

#コマンドライン引数(temp.txt)の受け取り
file = sys.argv[1]
#読み取り専用で代入
f=open(file,mode="r")
print("hd")
hcw=[];
hcd=[];
for line in f:

	#hq(実行なし)は無視
	if re.match(r"hq",line):
		pass
	#hcw(文字幅)は全て文字幅配列に格納
	elif re.match(r"hcw",line):
		xy=line.split()
		for i in range(len(xy)):
			if i==0:
				hcw.append(xy[i])
			else:
				hcw.append(float(xy[i]))
			#
		#
	#hcd(文字間隔)は文字間隔配列に全て格納
	elif re.match(r"hcd",line):
		xy=line.split()
		for i in range(len(xy)):
			if i==0:
				hcd.append(xy[i])
			else:
				hcd.append(float(xy[i]))
			#
		#
	#cn(文字種)は任意文字種か指定番号かを格納
	elif re.match(r"cn\d",line):
		xy=line.split()
		print(line,end="")
		#指定文字種の場合
		if(len(xy)==1):
			moji_w=hcw[int(line[2:-1])]
			moji_d=hcd[int(line[2:-1])]
		#任意文字種の場合
		else:
			moji_w=float(xy[1])
			moji_d=float(xy[3])
		#
	#ch(字の場所？)は個別にするために文字数分用意
	elif re.match(r"ch",line):
		#改行までの字数を取得
		#最大時数+1の字数を用意
		i=line.find("\"")
		pre_moji=line[0:i]
		moji=line[i+1:len(line)]
		if re.match(r"\^",moji):
			print(line,end="")
		else:
			xy=pre_moji.split()
			x=float(xy[1])
			y=float(xy[2])
			w=float(xy[3])
			h=float(xy[4])
			arg=math.atan2(h,w)
			moji_a=[]
			for i in range(len(moji)):
				moji_a.append(moji[i:i+1])
			#
			for i in range(len(moji_a)):
				print("ch %.11f %.11f %.11f %.11f \"%s" %(x,y,math.cos(arg),math.sin(arg),moji_a[i]))

				if size(moji_a[i])==1:
					pass
					x += (moji_w/2+moji_d/2)*math.cos(arg)
					y += (moji_w/2+moji_d/2)*math.sin(arg)
				else:
					pass
					x += (moji_w+moji_d)*math.cos(arg)
					y += (moji_w+moji_d)*math.sin(arg)
				#
			#
		#
	else:
		print(line,end="")
	#
#
f.close()
