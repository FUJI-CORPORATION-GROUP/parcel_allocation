# -*-coding: Shift_JIS -*-
import math
import sys
import re
import os
#������̒�����Ԃ�
def size(moji):
	return len(moji.encode("SHIFT-JIS"))
#

#�R�}���h���C������(temp.txt)�̎󂯎��
file = sys.argv[1]
#�ǂݎ���p�ő��
f=open(file,mode="r")
print("hd")
hcw=[];
hcd=[];
for line in f:

	#hq(���s�Ȃ�)�͖���
	if re.match(r"hq",line):
		pass
	#hcw(������)�͑S�ĕ������z��Ɋi�[
	elif re.match(r"hcw",line):
		xy=line.split()
		for i in range(len(xy)):
			if i==0:
				hcw.append(xy[i])
			else:
				hcw.append(float(xy[i]))
			#
		#
	#hcd(�����Ԋu)�͕����Ԋu�z��ɑS�Ċi�[
	elif re.match(r"hcd",line):
		xy=line.split()
		for i in range(len(xy)):
			if i==0:
				hcd.append(xy[i])
			else:
				hcd.append(float(xy[i]))
			#
		#
	#cn(������)�͔C�ӕ����킩�w��ԍ������i�[
	elif re.match(r"cn\d",line):
		xy=line.split()
		print(line,end="")
		#�w�蕶����̏ꍇ
		if(len(xy)==1):
			moji_w=hcw[int(line[2:-1])]
			moji_d=hcd[int(line[2:-1])]
		#�C�ӕ�����̏ꍇ
		else:
			moji_w=float(xy[1])
			moji_d=float(xy[3])
		#
	#ch(���̏ꏊ�H)�͌ʂɂ��邽�߂ɕ��������p��
	elif re.match(r"ch",line):
		#���s�܂ł̎������擾
		#�ő厞��+1�̎�����p��
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
