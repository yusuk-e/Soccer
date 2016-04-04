# -*- coding:utf-8 -*-

import pdb
from time import time
import datetime as dt
import numpy as np
from scipy.special import gammaln
import matplotlib
#matplotlib.use('Agg') #DISPLAYの設定
import matplotlib.pyplot as plt
import resource
import codecs
import random
from collections import defaultdict
from collections import namedtuple
import csv

#------variable------

#--file--
play_file = "play/" + "G_Osaka.csv"

#--dictionary--
team_dic = {}
player_dic = {}
position_dic = {}
action_dic = {}

#--list--
game_ids = []

#--data--
play = defaultdict(int)#プレイデータ play[game_id]
tracking = defaultdict(int)#トラッキングデータ tracking[game_id]


def input():
#--input--

    t0 = time()

    input_play()
    input_trackingdata()

    print "time:%f" % (time()-t0)
    pdb.set_trace()


def input_play():
#--input play data--
    fin = open(play_file)
    reader = csv.reader(fin)
    header = next(reader)#ヘッダとばし
    flag2 = 0

    for row in reader:
        flag = 0

        #--game--
        if len(row[0]) == 0:
            flag = 1
        else:
            game_id = int(row[0])
            if game_id not in game_ids:
                game_ids.append(game_id)
                flag2 = 1

        #--team--
        if len(row[3]) == 0:
            flag = 1
        else:
            team_id = int(row[3])
            if team_id not in team_dic:
                team_dic[team_id] = len(team_dic)
                player_dic[team_id] = {}

        #--player--
        if len(row[7]) == 0:
            flag = 1
        else:
            player_id = int(row[7])
            if player_id not in player_dic[team_id]:
                player_dic[team_id][player_id] = len(player_dic[team_id])

        #--position--
        if len(row[8]) == 0:
            flag = 1
        else:
            position_id = int(row[8])
            if position_id not in position_dic:
                position_dic[position_id] = len(position_dic)

        #--action--
        if len(row[9]) == 0:
            flag = 1
        else:
            action_id = int(row[9])
            if action_id not in action_dic:
                action_dic[action_id] = len(action_dic)

        #--re_time_s--
        re_time_s = int(row[22])

        #--re_time_m--
        re_time_m = int(row[23])

        #--re_time--
        re_time = float(str(re_time_s) + "." + str(re_time_m))

        #
        if flag == 0:
            event = np.array([[team_dic[team_id], \
                                   player_dic[team_id][player_id], \
                                   position_dic[position_id], \
                                   action_dic[action_id], \
                                   re_time]])
            #チーム，プレイヤー，ポジション，行動，ハーフ開始からの相対時刻（秒）

            if flag2 == 1:
                play[game_id] = event
                flag2 = 0
            else:
                play[game_id] = np.vstack([play[game_id], event])
        

def input_trackingdata():
#--input tracking data--
    
    for i in range(len(game_ids)):
        game_id = game_ids[i]

        fin = open(play_file)
    reader = csv.reader(fin)
    header = next(reader)#ヘッダとばし


        pdb.set_trace()

    flag2 = 0

    for row in reader:
        flag = 0

        #--game--
        if len(row[0]) == 0:
            flag = 1
        else:
            game_id = int(row[0])
            if game_id not in game_ids:
                game_ids.append(game_id)
                flag2 = 1

        #--team--
        if len(row[3]) == 0:
            flag = 1
        else:
            team_id = int(row[3])
            if team_id not in team_dic:
                team_dic[team_id] = len(team_dic)
                player_dic[team_id] = {}

    

#--main--
input()#データ読み込み





'''

    input_time()#前半開始・終了，後半開始・終了時刻の読み込み

elem_player = namedtuple("elem_player", "f, t, re_t, team, x, y, v")
#フレーム番号，x座標，y座標，速度，x軸方向のメッシュid，y軸方向のメッシュid，通し番号のメッシュid（左上はじまり）
frame_id_min = 10 ** 14
frame_id_max = -10 ** 14
Foo_p = namedtuple("Foo_p", "x, y, v, mx, my, m")
#x座標，y座標，速度，x軸方向のメッシュid，y軸方向のメッシュid，通し番号のメッシュid（左上はじまり）
Foo_b = namedtuple("Foo_b", "x,y,z,v,Team,Status,info")
#x座標，y座標，z座標，速度，保持しているチームid，ボールが生きてるかどうか，追加情報


#xmax = 0
#xmin = 0
#ymax = 0
#ymin = 0
xmax = float(5550)
xmin = float(-5550)
ymax = float(4400)
ymin = float(-4400)
new_xmax = float(2 * xmax) + 1 #x=xmaxのときint()が30を超えてしまうので+1しておく
new_ymax = float(2 * ymax) + 1
Dx = 30 #x方向のメッシュ分割数
Dy = 20 #y方向のメッシュ分割数
M_Team0 = np.zeros([Dy, Dx])
M_Team1 = np.zeros([Dy, Dx])
#-----------------------------------------------------------------------------------------


#Input------------------------------------------------------------------------------------
counter = 0
t0 = time()
#filename = "udp.out"
filename = "udp_small.out"
D = defaultdict(lambda: defaultdict(lambda: defaultdict(int))) 
#選手の位置情報 D[frame_id][Team_id][Player_id]
B = defaultdict(int) #ボールの位置情報 B[frame_id]

fin = open(filename)
counter = 0
for row in fin:
    temp0 = row.rstrip("\r\n").split(":")
    frame_id = int(temp0[0])
    #frame_id_dic.append(frame_id)
    if frame_id_min > frame_id:
        frame_id_min = frame_id
    if frame_id_max < frame_id:
        frame_id_max = frame_id

    temp1 = temp0[1].rstrip("\r\n").split(";")

    for i in range(len(temp1) - 1):
        temp2 = temp1[i].rstrip("\r\n").split(",")
        Team_id = int(temp2[0])
        sys_id = int(temp2[1])
        Player_id = int(temp2[2])
        for j in range(len(temp2)):
            if j == 1:
                if sys_id not in sys_id_dic:
                    sys_id_dic.append(sys_id)
            elif j == 2 and Team_id == 0:
                if Player_id not in Player_Team0_dic:
                    Player_Team0_dic.append(Player_id)
            elif j == 2 and Team_id == 1:
                if Player_id not in Player_Team1_dic:
                    Player_Team1_dic.append(Player_id)

        new_x = float(temp2[3])-xmin #原点をコートの左下に
        new_y = float(temp2[4])-ymin

        Mx_id = int( Dx * new_x / new_xmax ) #メッシュidを計算
        #if Mx_id > 29 or Mx_id < 0:
        #    pdb.set_trace()
        My_id = Dy - 1 - int( Dy * new_y / new_ymax ) #左上がメッシュid=0になるように反転
        #if My_id < 0 or My_id > 20:
        #    pdb.set_trace()
        M_id = My_id * Dx + Mx_id

        f = Foo_p(new_x, new_y, float(temp2[5]), Mx_id, My_id, M_id)
        D[frame_id][Team_id][Player_id] = f

        if f.x < 0 or f.y < 0:
            print err
        #if f.x > xmax:
        #    xmax = f.x
        #if f.x < xmin:
        #    xmin = f.x
        #if f.y > ymax:
        #    ymax = f.y
        #if f.y < ymin:
        #    ymin = f.y

    temp3 = temp0[2].rstrip("\r\n").split(";")
    temp3 = temp3[0].rstrip("\r\n").split(",")

    for j in range(len(temp3) - 1):
        
        if j == 4:
            if temp3[j] == "A":
                frag = 0
            elif temp3[j] == "H":
                frag = 1
            else:
                print "err"
            temp3[j] = frag

    if len(temp3) == 6:
        f = Foo_b(float(temp3[0]), float(temp3[1]), float(temp3[2]), float(temp3[3]), int(temp3[4]), temp3[5], "")
    elif len(temp3) == 7:
        f = Foo_b(float(temp3[0]), float(temp3[1]), float(temp3[2]), float(temp3[3]), int(temp3[4]), temp3[5], temp3[6])
        info = temp3[6]
        if info not in info_dic:
            info_dic.append(info)
    else:
        print "err"

    B[frame_id] = f

    #if f.x > xmax:
    #    xmax = f.x
    #if f.x < xmin:
    #    xmin = f.x
    #if f.y > ymax:
    #    ymax = f.y
    #if f.y < ymin:
    #    ymin = f.y

fin.close()

print "time:%f" % (time()-t0)
#-----------------------------------------------------------------------------------------

X = []
Y = []
min_event_x = 1000000
min_event_x_ind = 0
min_event_y = 1000000
min_event_y_ind = 0
for i in range(1000):
    event = B[frame_id_min + i]
    X.append(event.x)
    Y.append(event.y)
    if abs(event.x) < min_event_x:
        min_event_x_ind = i
        min_event_x = event.x

    if abs(event.y) < min_event_y:
        min_event_y_ind = i
        min_event_y = event.y

X = np.array(X)
Y = np.array(Y)
fig = plt.figure()
plt.quiver(X[:-1], Y[:-1], X[1:]-X[:-1], Y[1:]-Y[:-1], width=0.003, scale_units='xy', angles='xy', scale=1, color='darkcyan')
plt.savefig('temp.png')

pdb.set_trace()
#今だけ--------------
frame_id_max = int(frame_id_max - (frame_id_max - frame_id_min + 1) / 2) - 2000 #適当に前半だけ分析
#--------------


#全体のようす（いまはいらないかな）---------------
'''
if Team_id == 0:
    M_Team0[My_id, Mx_id] += 1
if Team_id == 1:
    M_Team1[My_id, Mx_id] += 1

fig = plt.figure()
plt.imshow(M_Team0)
plt.savefig('Mesh/M_Team0.png')
plt.close()

fig = plt.figure()
plt.imshow(M_Team1)
plt.savefig('Mesh/M_Team1.png')
plt.close()
'''
#-----------------------------------------------


#プレイヤー毎のヒートマップ作成-----------------------------------------------
t0 = time()

D_Team0 = defaultdict(int) #選手の位置情報 D[Player_id]
D_Team1 = defaultdict(int) #選手の位置情報 D[Player_id]
N = frame_id_max - frame_id_min + 1
for i in range(N):
    n = i + frame_id_min
    x_Team0 = D[n][0]
    N_Player_Team0 = len(Player_Team0_dic)

    for j in range(N_Player_Team0):
    #for j in range(2):
        Player_Team0_id = Player_Team0_dic[j]
        x = x_Team0[Player_Team0_id]

        if np.size(D_Team0[Player_Team0_id]) == 1: #D_Team0にまだデータがない選手の場合
            if np.size(x) == 6: #xが構造体を持つ場合
                f = np.array([n, x.x, x.y, x.v, x.mx, x.my, x.m])
                D_Team0[Player_Team0_id] = f

        else:
            if np.size(x) == 6:#xが構造体を持つ場合
                f = np.array([n, x.x, x.y, x.v, x.mx, x.my, x.m])
                D_Team0[Player_Team0_id] = np.vstack([D_Team0[Player_Team0_id],f])


for j in range(N_Player_Team0):
#for j in range(2):
    Player_Team0_id = Player_Team0_dic[j]
    if np.size(D_Team0[Player_Team0_id]) != 1:
        X = D_Team0[Player_Team0_id][:,1]
        Y = D_Team0[Player_Team0_id][:,2]
        fig = plt.figure()
        plt.plot(X,Y)
        plt.axis([0.0,new_xmax,0.0,new_ymax])
        plt.savefig('Tracking/Tracking_Team'+str(0)+'_Player'+str(Player_Team0_id)+'.png')
        plt.close()

        Mx = D_Team0[Player_Team0_id][:,4]
        My = D_Team0[Player_Team0_id][:,5]
        M = np.zeros([Dy, Dx])
        for k in range(len(Mx)):
            M[My[k],Mx[k]] += 1

        fig = plt.figure()
        plt.imshow(M)
        plt.savefig('Mesh/M_Team0'+'_Player'+str(Player_Team0_id)+'.png')
        plt.close()


print "time:%f" % (time()-t0)
#-----------------------------------------------------------------------------

    
#{ユーザ，場所}*時間の行列作成-----------------------------------------------
t0 = time()

print "time:%f" % (time()-t0)
#-----------------------------------------------------------------------------

'''


pdb.set_trace()
