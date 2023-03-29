# -*-coding: Shift_JIS -*-
import importlib
import math
import sys
import re
import os
import math

#�������m�̌�_�̌v�Z
def line_cross_point(P0, P1, Q0, Q1):
    x0, y0 = P0; x1, y1 = P1
    x2, y2 = Q0; x3, y3 = Q1
    a0 = x1 - x0; b0 = y1 - y0
    a2 = x3 - x2; b2 = y3 - y2

    d = a0*b2 - a2*b0
    if d == 0:
        # ���s�̏ꍇ
        return None

    # ��_�v�Z
    sn = b2 * (x2-x0) - a2 * (y2-y0)
    x = x0 + a0*sn/d
    y = y0 + b0*sn/d

    #��_������ɑ��݂���ꍇ�̂ݕ`��
    if (x0 <= x <= x1 and y0 <= y <= y1) or (x0 >= x >= x1 and y0 >= y >= y1) or (x0 <= x <= x1 and y0 >= y >= y1) or (x0 >= x >= x1 and y0 <= y <= y1):
      return [x, y]
    else:
      return None

#������̒�����Ԃ�
def size(moji):
	return len(moji.encode("SHIFT-JIS"))
#

#�R�}���h���C������(temp.txt)�̎󂯎��
file = sys.argv[1]

#�ǂݎ���p�ő��
f=open(file,mode="r")
print("hd")
datas = []
hp = []
xy = []
hp_coor = []
fin_line = []
fin_coor = []
hp_cnt = 0
pt_flag = False

#temp�̒��g���擾
for line in f:
	#hq(���s�Ȃ�)�͖���
  if re.match(r"hq",line):
    pass
  #hp�̏ꍇ�͍��W�擾
  elif re.match(r"hp",line):
    xy=line.split()
    for i in range(len(xy)):
      if i==0:
        hp_cnt += 1
      else:
        hp.append(xy[i])
  #�󔒂̏ꍇ�����W�擾
  elif re.match(r" ",line):
    xy=line.split()
    xy = [float(item) for item in xy]
    datas.append([xy[0],xy[1]])
    datas.append([xy[2],xy[3]])
    #print(line,end="")
#�t�@�C�������
f.close()

#�d�����Ă���Ō�̗v�f���폜
del hp[-2:]
print("hp:" + str(hp))
print("datas" + str(datas))

#���X�g�̒��g��S��float�^��
hp = [float(item) for item in hp]

#hp�����W���X�g�ɕϊ�
for i in range(0, len(hp), 2):
  hp_coor.append([hp[i], hp[i + 1]])

print(len(hp_coor))
print(hp_coor)

for i in range(len(hp_coor)):
  if i + 1 == len(hp_coor):
    print(" %.11f %.11f %.11f %.11f\n" %(hp_coor[i][0],hp_coor[i][1],hp_coor[0][0], hp_coor[0][1]))
  else:
    print(" %.11f %.11f %.11f %.11f\n" %(hp_coor[i][0],hp_coor[i][1],hp_coor[i + 1][0], hp_coor[i + 1][1]))



#���������܂ŐL�k
for i in range(0, len(datas), 2):
  for j in range(len(hp_coor)):
    if j + 1 == len(hp_coor):
      pt_flag = True
      #�Z�o�����_���g��ɑ��݂���ꍇ���X�g�ɒǉ�
      fin_coor = line_cross_point(hp_coor[j], hp_coor[0], datas[i], datas[i + 1])
      print("fin_coor:" + str(fin_coor))
      #�Ԃ��ꂽ���̂�None�łȂ���Α��s
      if fin_coor is not None:
        for k in range(len(hp_coor)):

          print(hp_coor[k], fin_coor)

          #���_�̏ꍇ�͏���
          if math.floor(hp_coor[k][0] * 10 ** 7) / (10 ** 7) == math.floor(fin_coor[0] * 10 ** 7) / (10 ** 7) and math.floor(hp_coor[k][1] * 10 ** 7) / (10 ** 7) == math.floor(fin_coor[1] * 10 ** 7) / (10 ** 7):
            print("�ǉ����Ȃ�")
            pt_flag = False
        #�����𖞂����Ă���ΐL�k
        if pt_flag:
          print("�ǉ�����" + str(fin_coor))
          fin_line.append(fin_coor)
          pt_flag = False
    else:
      pt_flag = True
      fin_coor = line_cross_point(hp_coor[j], hp_coor[j + 1], datas[i], datas[i + 1])
      print("fin_coor:" + str(fin_coor))
      #�Ԃ��ꂽ���̂�None�łȂ���Α��s
      if fin_coor is not None:
        for k in range(len(hp_coor)):

          print(hp_coor[k], fin_coor)

          #���_�̏ꍇ�͏���
          if math.floor(hp_coor[k][0] * 10 ** 7) / (10 ** 7) == math.floor(fin_coor[0] * 10 ** 7) / (10 ** 7) and math.floor(hp_coor[k][1] * 10 ** 7) / (10 ** 7) == math.floor(fin_coor[1] * 10 ** 7) / (10 ** 7):
            print("�ǉ����Ȃ�")
            pt_flag = False
        #�����𖞂����Ă���ΐL�k
        if pt_flag:
          print("�ǉ�����" + str(fin_coor))
          fin_line.append(fin_coor)
          pt_flag = False

print(" ")
print(fin_line)
print(" ")

#�쐬����������`��
for i in range(0, len(fin_line), 2):
  print(i)
  print(" %.11f %.11f %.11f %.11f\n" %(fin_line[i][0],fin_line[i][1],fin_line[i + 1][0], fin_line[i + 1][1]))
