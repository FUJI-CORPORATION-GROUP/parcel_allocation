# -*-coding: Shift_JIS -*-
import importlib
import math
import sys
import re
import os
import Calc

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
    if (x0 <= x <= x1 and y0 <= y <= y1) or (x0 >= x >= x1 and y0 >= y >= y1):
      return x, y
    else:
      return None

#�Ԍ�����ɍő�ː��̑�n���`��
def maguchi(data, coor):
  lines_h = []
  lines_l = []
  fin_line = []

  #���̒������v�Z
  edge = abs(coor[0][0] - coor[1][0])
  #�Ԍ���7.1m�Ōv�Z
  num = (int)(edge / 7100)
  #��n���Ɏg�����s���̒����̌v�Z
  depth = abs(coor[1][1] - coor[2][1]) / 1000

  print("edge:" + str(edge) + " num:" + str(num))

#�Ƃ��쐬����ː�������
  flont_x = edge / num
  flont_y = abs(coor[0][1] - coor[1][1]) / num

  #�������Ԍ��̊��o�ō쐬
  for i in range(1,num):
    lines_l.append([coor[2][0] + flont_x * i - 1000000, coor[2][1] + flont_y * i - 1000000])
    lines_h.append([coor[1][0] + flont_x * i - 1000000, coor[1][1] + flont_y * i - 1000000])

    for j in range(len(data)):
      if j + 1 == len(data):
        #�Z�o�����_���g��ɑ��݂���ꍇ���X�g�ɒǉ�
        fin_coor = line_cross_point(data[j], data[1], lines_h[i - 1], lines_l[i - 1])
        if fin_coor is not None:
          fin_line.append(fin_coor)
      else:
        fin_coor = line_cross_point(data[j], data[j + 1], lines_h[i - 1], lines_l[i - 1])
        if fin_coor is not None:
          fin_line.append(fin_coor)

  print("fin_line" + str(fin_line))
  print(len(fin_line))

  #�쐬����������`��
  for i in range(0, len(fin_line), 2):
    print(i)
    print(" %.11f %.11f %.11f %.11f\n" %(fin_line[i][0],fin_line[i][1],fin_line[i + 1][0], fin_line[i + 1][1]))


  #������̕~�n�������
  if flont_x * depth > 200:
    print("������̖ʐς���")
    mid_line = []
    mid_line.append([(coor[1][0] + coor[2][0]) / 2 - 1000000, (coor[1][1] + coor[2][1]) / 2 - 1000000])
    mid_line.append([mid_line[0][0] + flont_x * num, mid_line[0][1] + flont_y * num])
    print(" %.11f %.11f %.11f %.11f\n" %(mid_line[0][0],mid_line[0][1],mid_line[1][0], mid_line[1][1]))


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
xy = []
hp = []
hp_coor = []
hp_coor_plus = []
start = 0
hp_cnt = 0

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
        #hp.append(xy[i])
        hp_cnt += 1
      else:
        hp.append(xy[i])
  #�󔒂̏ꍇ�����W�擾
  elif re.match(r" ",line):
    xy=line.split()
    datas.append([xy[0],xy[1]])
    datas.append([xy[2],xy[3]])
    print(line,end="")

f.close()

#�d���폜
datas = list(map(list,set(map(tuple,datas))))

#���X�g�̒��g��S��float�^��
hp = [float(item) for item in hp]
cnt = (len(hp) / 2 + 2)

print(hp)

#hp�����W���X�g�ɕϊ�
for i in range(0, len(hp), 2):
  hp_coor_plus.append([hp[i] + 1000000, hp[i + 1] + 1000000])
  hp_coor.append([hp[i], hp[i + 1]])

print(hp_coor_plus)

#�ʐ�/�ː��̌v�Z
area = Calc.main_calc(hp_coor_plus)
units = area / 100000000

print("�ʐς�" + str(area) + "�ː���" + str(int(units)))

if len(datas) > 3:
  #�ʍ��W�̓���
  x=float(datas[0][0])
  y=float(datas[0][1])

  m1 = (float(datas[0][0]) + float(datas[1][0])) / 2
  m2 = (float(datas[0][1]) + float(datas[1][1])) / 2
  m3 = (float(datas[2][0]) + float(datas[3][0])) / 2
  m4 = (float(datas[2][1]) + float(datas[3][1])) / 2

  #���_�̕`��
  print("")
  print(" " + str(int(m1)) + " " + str(int(m2)) + " " + str(int(m3)) + " " + str(int(m4)))

maguchi(hp_coor, hp_coor_plus)