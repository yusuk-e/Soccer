# -*- coding:utf-8 --*

from time import time
from collections import defaultdict
import csv
import sys
import os
import shutil
import numpy as np
import matplotlib
#matplotlib.use('Agg') #DIPLAYの設定
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.ticker as tick
from PIL import Image
import seaborn as sns
import math
from sklearn.cluster import KMeans
sns.set(style="whitegrid", context="talk")

#--sys variable--
argvs = sys.argv
argc = len(argvs)
if (argc != 2):
    print "Usage: #python %s team_no" % argvs[0]
    quit()
anal_team = argvs[1]

#------variable------
#--directory--
input_dir = "Dataset/" + str(anal_team)

#--dictionary--
team_dic = {}
player_dic = {}
action_dic = {}

#--list--
game_ids = []
offense_nos = defaultdict(int)#攻撃番号 offense_nos[game_id]
V_all = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))
Feature = []
player_id_all = []

#--scala--
xmin = -5250
xmax = 5250
ymin = -3400
ymax = 3400
period = float(10)#シュートから10秒前まで

#--data--
play = defaultdict(int)#プレイデータ play[game_id]
#0.オフェンス番号
#1.チーム
#2.前半or後半
#3.プレイヤー
#4.行動
#5.x
#6.y
#7.ハーフ開始からの相対時刻（秒）
#8.ゴールorミス

tracking = defaultdict(int)#トラッキングデータ tracking[game_id]
#0.オフェンス番号
#1.チーム
#2.前半or後半
#3.プレイヤー
#4.x
#5.y
#6.ハーフ開始からの相対時刻（秒）


def input():
#--input--

    t0 = time()
    print "\n*input dictionary"
    input_dictionary()
    print "input_dictionary time:%f \n" % (time()-t0)

    t0 = time()
    print "*input play data"
    input_play()
    print "input_play time:%f \n" % (time()-t0)

    t0 = time()
    print "*input tracking data"
    input_tracking()
    print "input_tracking time:%f \n" % (time()-t0)


def input_dictionary():
#--input dictionary--

    dic_dir = input_dir + "/dic"

    fin = open(dic_dir + "/game.csv")
    #fin = open(dic_dir + "/game_small.csv")

    for row in fin:
        temp = row.rstrip("\r\n")
        game_id = temp
        game_ids.append(game_id)
    fin.close()

    fin = open(dic_dir + "/team.csv")
    for row in fin:
        temp = row.rstrip("\r\n").split(",")
        team_id = temp[0]
        team_name = temp[1]
        team_dic[team_id] = team_name
        player_dic[team_id] = {}
    fin.close()

    fin = open(dic_dir + "/player.csv")
    for row in fin:
        temp = row.rstrip("\r\n").split(",")
        team_id = temp[0]
        player_id = temp[1]
        player_name = temp[2]
        player_dic[team_id][player_id] = player_name
    fin.close()

    fin = open(dic_dir + "/action.csv")
    for row in fin:
        temp = row.rstrip("\r\n").split(",")
        action_id = temp[0]
        action_name = temp[1]
        action_dic[action_id] = action_name
    fin.close()


def input_play():
#--input play data--

    for i in range(len(game_ids)):
        game_id = game_ids[i]
        
        fin = open(input_dir + "/" + str(game_id) + "/play.csv")
        
        flag = 0
        for row in fin:
            event = row.rstrip("\r\n").split(",")
            if flag == 0:
                play[game_id] = [event]
                flag = 1
            else:
                play[game_id].append(event)
        fin.close()

    for i in range(len(game_ids)):
        game_id = game_ids[i]
        play[game_id] = np.array(play[game_id])


def input_tracking():
#--input tracking data--

    for i in range(len(game_ids)):
        game_id = game_ids[i]
        print game_id
        
        fin = open(input_dir + "/" + str(game_id) + "/tracking.csv")
        
        flag = 0
        for row in fin:
            event = row.rstrip("\r\n").split(",")
            if flag == 0:
                tracking[game_id] = [event]
                flag = 1
            else:
                tracking[game_id].append(event)
        fin.close()

    for i in range(len(game_ids)):
        game_id = game_ids[i]
        tracking[game_id] = np.array(tracking[game_id])


def speed():

    coop_all_dir = "Dataset/" + str(anal_team)
    if not os.path.exists(coop_all_dir + "/Speed_Shots_Coop_All"):
        os.makedirs(coop_all_dir + "/Speed_Shots_Coop_All")

    if not os.path.exists(coop_all_dir + "/Speed_Shots_Coop_Goals"):
        os.makedirs(coop_all_dir + "/Speed_Shots_Coop_Goals")

    if not os.path.exists(coop_all_dir + "/Speed_Shots_Coop_Misses"):
        os.makedirs(coop_all_dir + "/Speed_Shots_Coop_Misses")


    #player_id_all
    flag = 0
    for i in range(len(game_ids)):
        game_id = game_ids[i]
        if flag == 0:
            P = play[game_id]
            flag = 1
        if flag == 1:
            P = np.vstack([P, play[game_id]])
    
    P_team_line = P[:,1]
    ids = np.where(P_team_line == str(anal_team))[0]
    P_player_line = P[ids,3]
    player_id_all = np.unique(P_player_line)


    for i in range(len(game_ids)):
        game_id = game_ids[i]

        P = play[game_id]
        P_O_no_line = P[:,0]
        P_team_line = P[:,1]
        P_action_line = P[:,4]
        P_g_m_line = P[:,8]

        T = tracking[game_id]
        T_O_no_line = T[:,0]
        T_team_line = T[:,1]

        #{シュート&対象とするチーム}の攻撃No
        ids_shots = np.where((P_action_line == str(15)) & (P_team_line == str(anal_team)))[0]
        O_no_shots = np.unique(P[ids_shots,0].astype(np.int64))

        for j in range(len(O_no_shots)):
            O_no = O_no_shots[j]

            #シュートのタイミングと成功したか失敗したかをplayから抜き出す
            ids_shots = np.where((P_O_no_line == str(O_no)) & (P_team_line == str(anal_team)) & (P_action_line == str(15)))[0]
            shot_times = P[ids_shots,7].astype(np.float64)
            g_ms = P[ids_shots,8]

            #O_noのトラッキングデータを抜き出す
            ids = np.where((T_O_no_line == str(O_no)) & (T_team_line == str(anal_team)))[0]
            TO_player_line = T[ids,3]
            TO_x_line = T[ids,4].astype(np.float64)
            TO_y_line = T[ids,5].astype(np.float64)
            TO_time_line = T[ids,6].astype(np.float64)

            IDS = {}
            if np.size(shot_times) == 1:
                shot_time1 = shot_times[0]
                IDS[0] = np.where( ((shot_time1 - period) < TO_time_line) & (TO_time_line < shot_time1) )[0]
            elif np.size(shot_times) == 2:
                shot_time1 = shot_times[0]
                shot_time2 = shot_times[1]
                IDS[0] = np.where( ((shot_time2 - period) < TO_time_line) & (TO_time_line < shot_time2) )[0]
                #IDS[1] = np.where( (shot_time1 < TO_time_line) & ((shot_time2 - period) < TO_time_line) & (TO_time_line < shot_time2) )[0]
            elif np.size(shot_times) == 3:
                shot_time1 = shot_times[0]
                shot_time2 = shot_times[1]
                shot_time3 = shot_times[2]
                IDS[0] = np.where( ((shot_time3 - period) < TO_time_line) & (TO_time_line < shot_time3) )[0]
                #IDS[1] = np.where( (shot_time1 < TO_time_line) & ((shot_time2 - period) < TO_time_line) & (TO_time_line < shot_time2) )[0]
                #IDS[2] = np.where( (shot_time2 < TO_time_line) & ((shot_time3 - period) < TO_time_line) & (TO_time_line < shot_time3) )[0]
            elif np.size(shot_times) == 4:
                shot_time1 = shot_times[0]
                shot_time2 = shot_times[1]
                shot_time3 = shot_times[2]
                shot_time4 = shot_times[3]
                IDS[0] = np.where( ((shot_time4 - period) < TO_time_line) & (TO_time_line < shot_time4) )[0]
                #IDS[1] = np.where( (shot_time1 < TO_time_line) & ((shot_time2 - period) < TO_time_line) & (TO_time_line < shot_time2) )[0]
                #IDS[2] = np.where( (shot_time2 < TO_time_line) & ((shot_time3 - period) < TO_time_line) & (TO_time_line < shot_time3) )[0]
                #IDS[3] = np.where( (shot_time3 < TO_time_line) & ((shot_time4 - period) < TO_time_line) & (TO_time_line < shot_time4) )[0]
            else:
                print shot_times
                print "err"
                quit()


            if len(IDS[0]) != 0:

                
                for k in range(len(IDS)):
                    ids = IDS[k]
                    TOO_x_line = TO_x_line[ids]
                    TOO_y_line = TO_y_line[ids]
                    TOO_time_line = TO_time_line[ids]
                    start_time = np.min(TOO_time_line)
                    last_time = np.max(TOO_time_line)
                    TOO_player_line = TO_player_line[ids].astype(np.int64)
                    TOO_player_uniq = np.unique(TOO_player_line).astype(np.str)
                    TOO_player_line = TOO_player_line.astype(np.str)
                    g_m = g_ms[k]

                    #fig = plt.figure(figsize=(16,8))

                    num_player = np.size(TOO_player_uniq)
                    for l in range(num_player):
                        player_id = TOO_player_uniq[l]
                        ids_player = np.where(TOO_player_line == player_id)[0]
    
                        X = TOO_x_line[ids_player]
                        Y = TOO_y_line[ids_player]
                        Time = TOO_time_line[ids_player]

                        '''
                        Time = Time - [start_time] * len(Time)
                        print len(Time)
                        observation = [0] * int((last_time - start_time) / 0.04 + 1)
                        print len(observation)
                        if len(Time) != len(observation):
                            print Time
                        '''

                        V = []
                        for m in range(np.size(X)-1):
                            x_now = float(X[m]) * 60 / 5250
                            x_next = float(X[m+1]) * 60 / 5250
                            y_now = float(Y[m]) * 90 / 3400
                            y_next = float(Y[m+1]) * 90 / 3400
                            t_now = float(Time[m])
                            t_next = float(Time[m+1])
                            d = np.sqrt((x_next - x_now)**2 + (y_next - y_now)**2)
                            if d > 10 ** -5:
                                v = d / (t_next - t_now)
                            else:
                                v = 0
                            V.append(v)

                        A = len(Time) - 1
                        B = (last_time - start_time) / 0.04
                        if np.abs(A - B) > 1:
                            ss = [0] * int((Time[0] - start_time) / 0.04)
                            ll = [0] * int(((last_time - Time[np.size(X)-1]) / 0.04))
                            '''
                            if A == 209:
                                print O_no
                                print A
                                print B
                                print ss
                                print ll
                                print Time
                                print len(Time)
                                print start_time
                                print last_time
                                print Time[np.size(X)-1]
                            '''
                            ss.extend(V)
                            ss.extend(ll)
                            V = ss
                        
                        if np.abs(len(V) - B) > 0:
                            add = np.abs(len(V) - B)
                            ll = [0] * int(add)
                            V.extend(ll)

                        if int(B) < len(V):
                            del V[len(V)-1]
                        elif int(B) > len(V):
                            V.extend([0])

                        
                        ytemp = smoozing( V )
                        V_all[int(game_id)][int(O_no)][int(k)][int(player_id)] = ytemp

                        xtemp = [q * 0.04 for q in range(len(ytemp))]
                        plt.subplot(num_player+1,1,l+1)
                        plt.plot(xtemp, ytemp, color="c", linewidth=1.5)
                        plt.axis([0, period + 0.5, 0, 20])
                        plt.gca().xaxis.set_major_locator(tick.MultipleLocator(2))
                        plt.gca().yaxis.set_major_locator(tick.MultipleLocator(10))
                        plt.xticks(size=6)
                        plt.yticks(size=6)
                        plt.ylabel(str(player_id))
                        #plt.tick_params(labelbottom='off')#,labelleft='off')

                    #shots timing
                    plt.subplot(num_player+1,1,0)
                    xtemp = last_time - start_time
                    ytemp = 10
                    if g_m == str(1):
                        plt.scatter(xtemp, ytemp, c = "orange", s=80, marker = "^")
                    elif g_m == str(0):
                        plt.scatter(xtemp, ytemp, c = "grey", s=80, marker = "^")
                    plt.axis([0, period + 0.5, 0, 20])
                    plt.gca().xaxis.set_major_locator(tick.MultipleLocator(2))
                    plt.gca().yaxis.set_major_locator(tick.MultipleLocator(10))
                    plt.xticks(size=6)
                    plt.yticks(size=6)
                    plt.ylabel("Shot")
                    plt.tick_params(labelbottom='off',labelleft='off')
    
                    plt.subplots_adjust(hspace=0.8)
                    plt.savefig(coop_all_dir + "/Speed_Shots_Coop_All" + "/" + str(game_id) + "_no" + str(O_no) + "_" + str(k) + ".png", transparent=True)
                    if g_m == str(1):
                        plt.savefig(coop_all_dir + "/Speed_Shots_Coop_Goals" + "/" + str(game_id) + "_no" + str(O_no) + "_" + str(k) + ".png", transparent=True)
                    elif g_m == str(0):
                        plt.savefig(coop_all_dir + "/Speed_Shots_Coop_Misses" + "/" + str(game_id) + "_no" + str(O_no) + "_" + str(k) + ".png", transparent=True)
                    plt.close()
                    
                    V_all_add( game_id, O_no, TOO_player_uniq, player_id_all, len(V), k )

def smoozing( V ):

    for i in range(len(V)):
        v = V[i]
        if v > 20:
            if i == 0:
                new_v = 0
            else:
                new_v = V[i-1]
            V[i] = new_v                   

    return V


def V_all_add( game_id, O_no, TOO, ALL, length, k ):

    dammy = [0] * length
    for i in range(len(ALL)):
        player_id = ALL[i]
        if player_id not in TOO:
            V_all[int(game_id)][int(O_no)][int(k)][int(player_id)] = dammy

    
def correlation():

    corr_all_dir = "Dataset/" + str(anal_team)
    if not os.path.exists(corr_all_dir + "/Speed_Shots_Corr_All"):
        os.makedirs(corr_all_dir + "/Speed_Shots_Corr_All")

    if not os.path.exists(corr_all_dir + "/Speed_Shots_Corr_Goals"):
        os.makedirs(corr_all_dir + "/Speed_Shots_Corr_Goals")

    if not os.path.exists(corr_all_dir + "/Speed_Shots_Corr_Misses"):
        os.makedirs(corr_all_dir + "/Speed_Shots_Corr_Misses")


    #player_id_all
    flag = 0
    for i in range(len(game_ids)):
        game_id = game_ids[i]
        if flag == 0:
            P = play[game_id]
            flag = 1
        if flag == 1:
            P = np.vstack([P, play[game_id]])
    
    P_team_line = P[:,1]
    ids = np.where(P_team_line == str(anal_team))[0]
    P_player_line = P[ids,3].astype(np.int64)
    player_id_all = np.unique(P_player_line)


    CORR_goals = np.zeros([len(player_id_all), len(player_id_all)])
    goals_count = 0
    CORR_misses = np.zeros([len(player_id_all), len(player_id_all)])
    misses_count = 0
    CORR_all = np.zeros([len(player_id_all), len(player_id_all)])

    for i in range(len(game_ids)):
        game_id = game_ids[i]

        P = play[game_id]
        P_O_no_line = P[:,0]
        P_team_line = P[:,1]
        P_action_line = P[:,4]

        T = tracking[game_id]
        T_O_no_line = T[:,0]
        T_team_line = T[:,1]

        #{シュート&対象とするチーム}の攻撃No
        ids_shots = np.where((P_action_line == str(15)) & (P_team_line == str(anal_team)))[0]
        O_no_shots = np.unique(P[ids_shots,0].astype(np.int64))

        for j in range(len(O_no_shots)):
            O_no = O_no_shots[j]

            #シュートのタイミングと成功したか失敗したかをplayから抜き出す
            ids_shots = np.where((P_O_no_line == str(O_no)) & (P_team_line == str(anal_team)) & (P_action_line == str(15)))[0]
            shot_times = P[ids_shots,7].astype(np.float64)
            g_ms = P[ids_shots,8]

            #O_noのトラッキングデータを抜き出す
            ids = np.where((T_O_no_line == str(O_no)) & (T_team_line == str(anal_team)))[0]
            TO_player_line = T[ids,3]
            TO_x_line = T[ids,4].astype(np.float64)
            TO_y_line = T[ids,5].astype(np.float64)
            TO_time_line = T[ids,6].astype(np.float64)

            IDS = {}
            if np.size(shot_times) == 1:
                shot_time1 = shot_times[0]
                IDS[0] = np.where( ((shot_time1 - period) < TO_time_line) & (TO_time_line < shot_time1) )[0]
            elif np.size(shot_times) == 2:
                shot_time1 = shot_times[0]
                shot_time2 = shot_times[1]
                IDS[0] = np.where( ((shot_time2 - period) < TO_time_line) & (TO_time_line < shot_time2) )[0]
                #IDS[1] = np.where( (shot_time1 < TO_time_line) & ((shot_time2 - period) < TO_time_line) & (TO_time_line < shot_time2) )[0]
            elif np.size(shot_times) == 3:
                shot_time1 = shot_times[0]
                shot_time2 = shot_times[1]
                shot_time3 = shot_times[2]
                IDS[0] = np.where( ((shot_time3 - period) < TO_time_line) & (TO_time_line < shot_time3) )[0]
                #IDS[1] = np.where( (shot_time1 < TO_time_line) & ((shot_time2 - period) < TO_time_line) & (TO_time_line < shot_time2) )[0]
                #IDS[2] = np.where( (shot_time2 < TO_time_line) & ((shot_time3 - period) < TO_time_line) & (TO_time_line < shot_time3) )[0]
            elif np.size(shot_times) == 4:
                shot_time1 = shot_times[0]
                shot_time2 = shot_times[1]
                shot_time3 = shot_times[2]
                shot_time4 = shot_times[3]
                IDS[0] = np.where( ((shot_time4 - period) < TO_time_line) & (TO_time_line < shot_time4) )[0]
                #IDS[1] = np.where( (shot_time1 < TO_time_line) & ((shot_time2 - period) < TO_time_line) & (TO_time_line < shot_time2) )[0]
                #IDS[2] = np.where( (shot_time2 < TO_time_line) & ((shot_time3 - period) < TO_time_line) & (TO_time_line < shot_time3) )[0]
                #IDS[3] = np.where( (shot_time3 < TO_time_line) & ((shot_time4 - period) < TO_time_line) & (TO_time_line < shot_time4) )[0]
            else:
                print shot_times
                print "err"
                quit()


            if len(IDS[0]) != 0:

                for k in range(len(IDS)):

                    g_m = g_ms[k]

                    V = []
                    for l in range(len(player_id_all)):
                        player_id = player_id_all[l]

                        v = V_all[int(game_id)][int(O_no)][int(k)][player_id]
                        V.append(v)

                    #print game_id
                    #print O_no
                    #print k
                    #print V
                    #print np.shape(V)
                    vsize = len(V[0])
                    if vsize != 0:
                        print game_id
                        print O_no
                        print V
                        print len(V)
                        print len(V[0])
                        CORR = np.corrcoef(V)
                        print np.shape(CORR)
                        row = len(CORR)
                        col = len(player_id_all)
                        #print row 
                        #print col
                        for l in range(row):
                            for m in range(col):
                                #print l
                                #print m
                                corr = CORR[l][m]
                                if math.isnan(corr) == True:
                                    CORR[l][m] = 0
    
                        feature_ex( CORR )
    
                        sns.heatmap(np.array(CORR), vmax=.8, square=True)
                        #plt.xticks(player_id_all)
                        #plt.yticks(player_id_all)
                        plt.savefig(corr_all_dir + "/Speed_Shots_Corr_All" + "/" + str(game_id) + "_no" + str(O_no) + "_" + str(k) + ".png", transparent=True)
                        CORR_all = CORR_all + CORR
                        if g_m == str(1):
                            plt.savefig(corr_all_dir + "/Speed_Shots_Corr_Goals" + "/" + str(game_id) + "_no" + str(O_no) + "_" + str(k) + ".png", transparent=True)
                            CORR_goals = CORR_goals + CORR
                            goals_count += 1
                        elif g_m == str(0):
                            plt.savefig(corr_all_dir + "/Speed_Shots_Corr_Misses" + "/" + str(game_id) + "_no" + str(O_no) + "_" + str(k) + ".png", transparent=True)
                            CORR_misses = CORR_misses + CORR
                            misses_count += 1
                        plt.close()
    

    CORR_goals = CORR_goals / goals_count
    sns.heatmap(CORR_goals, vmax=.8, square=True)
    plt.savefig(corr_all_dir + "/CORR_goals.png", transparent=True)
    plt.close()

    CORR_misses = CORR_misses / misses_count
    sns.heatmap(CORR_misses, vmax=.8, square=True)
    plt.savefig(corr_all_dir + "/CORR_misses.png", transparent=True)
    plt.close()

    CORR_all = CORR_all / (goals_count + misses_count)
    sns.heatmap(CORR_all, vmax=.8, square=True)
    plt.savefig(corr_all_dir + "/CORR_all.png", transparent=True)
    plt.close()
    

def feature_ex( CORR ):

    row = np.shape(CORR)[0]
    col = np.shape(CORR)[1]
    
    x = []
    for i in range(row):
        for j in range(col):
            if i < j:
                x.append(CORR[i][j])
    Feature.append(x)


def clustering():

    corr_all_dir = "Dataset/" + str(anal_team)

    #player_id_all
    flag = 0
    for i in range(len(game_ids)):
        game_id = game_ids[i]
        if flag == 0:
            P = play[game_id]
            flag = 1
        if flag == 1:
            P = np.vstack([P, play[game_id]])
    
    P_team_line = P[:,1]
    ids = np.where(P_team_line == str(anal_team))[0]
    P_player_line = P[ids,3].astype(np.int64)
    player_id_all = np.unique(P_player_line)


    K = 5
    X = np.array(Feature)
    model = KMeans(n_clusters=K, init='k-means++', max_iter=300, tol=0.0001).fit(X)
    C = model.cluster_centers_
    print C

    for k in range(K):
        CORR = np.zeros([len(player_id_all), len(player_id_all)])
        counter = 0
        for i in range(len(player_id_all)):
            for j in range(len(player_id_all)):
                if i < j:
                    print C[k][counter]
                    CORR[i][j] = C[k][counter]
                    CORR[j][i] = C[k][counter]
                    counter += 1

        sns.heatmap(CORR, vmax=.8, square=True)
        plt.savefig(corr_all_dir + "/CORR_K" + str(k) + ".png", transparent=True)
        plt.close()

    

#--main--
input()#データ読み込み

speed()

correlation()

clustering()
