# -*- coding:utf-8 -*-

from time import time
from collections import defaultdict
import csv
import sys
import numpy as np

#--sys variable--
argvs = sys.argv
argc = len(argvs)
if (argc != 2):
    print "Usage: #python %s team_no" % argvs[0]
    quit()
anal_team = argvs[1]

#------variable------

#--file--
#play_file = "play/" + anal_team + ".csv"
play_file = "play/" + anal_team + "_small.csv"

#--dictionary--
team_dic = {}
player_dic = {}
action_dic = {}

#--list--
game_ids = []
offense_nos = defaultdict(int)#攻撃番号 offense_nos[game_id]

#--scala--
xmin = -5250
xmax = 5250
ymin = -3400
ymax = 3400

#--data--
play = defaultdict(int)#プレイデータ play[game_id]
tracking = defaultdict(int)#トラッキングデータ tracking[game_id]


def input():
#--input--

    t0 = time()
    print "\n*input play data"
    input_play()
    print "input_play time:%f \n" % (time()-t0)

    t0 = time()
    print "*input tracking data"
    input_tracking()
    print "input_tracking time:%f \n" % (time()-t0)


def input_play():
#--input play data--

    fin = open(play_file)
    print play_file

    reader = csv.reader(fin)
    header = next(reader)#ヘッダとばし

    for row in reader:
        flag = 0#欠損など問題のあるログを削除するためのフラグ

        #--game--
        if len(row[0]) == 0 or row[0].isdigit() == False:
            flag = 1
        else:
            game_id = int(row[0])
            if game_id not in game_ids:
                game_ids.append(game_id)
                offense_nos[game_id] = []
                flag2 = 1#一つ目のログを識別するためのフラグ

        #--game_status--
        if len(row[2]) == 0 or row[2].isdigit() == False:
            flag = 1
        else:
            game_status = int(row[2])#game_status:前半1or後半2

        #--team--
        if len(row[3]) == 0 or int(row[3]) == 0 or row[3].isdigit() == False:#row[3]==0:前後半開始終了,中断を除く
            flag = 1
        else:
            team_id = int(row[3])
            if team_id not in team_dic:
                team_name = row[4]
                team_dic[team_id] = team_name
                player_dic[team_id] = {}
                #print "%d %s" % (team_id, team_dic[team_id])

        #--player--
        if len(row[7]) == 0 or row[7].isdigit() == False:
            flag = 1
        else:
            player_id = int(row[7])
            if player_id not in player_dic[team_id]:
                player_name = row[6]
                player_dic[team_id][player_id] = player_name

        #--action--
        if len(row[9]) == 0 or row[9].isdigit() == False:
            flag = 1
        else:
            action_id = int(row[9])
            if action_id not in action_dic:
                action_name = row[10]
                action_dic[action_id] = action_name
                #print "%d %s" % (action_id, action_dic[action_id])

        #--home away--
        if len(row[12]) == 0 or row[12].isdigit() == False:
            flag = 1
        else:
            h_a = int(row[12])#1:home, 2:away

        #--offense no--
        if len(row[13]) == 0 or row[13].isdigit() == False:
            flag = 1
        else:
            offense_no = int(row[13])
            if offense_no not in offense_nos[game_id]:
                offense_nos[game_id].append(offense_no)

        #--x axis--
        if len(row[15]) == 0:
            flag = 1
            print row[15]
        else:
            x = float(row[15]) * 100 / 3
            if x < xmin or xmax < x:
                flag = 1
                
        #--y axis--
        if len(row[16]) == 0:
            flag = 1
        else:
            y = float(row[16]) * -1 * 100 / 3
            if y < ymin or ymax < y:
                flag = 1
            #x,y座標の変換（トラッキングデータに合わせる）

        #--direction--攻撃方向
        if len(row[17]) == 0 or row[17].isdigit() == False:
            flag = 1
        else:
            d = int(row[17])
            #前後半で1か2．対象とするチームが1になるように後で反転させる

        #--re_time_s--
        re_time_temp = row[22]
        re_time_temp_list = list(re_time_temp)
        if len(re_time_temp_list) == 1:
            re_time_m = 0
            re_time_s = int(re_time_temp_list[0])
        elif len(re_time_temp_list) == 2:
            re_time_m = 0
            re_time_s = int( re_time_temp_list[0] + re_time_temp_list[1] )
        elif len(re_time_temp_list) == 3:
            re_time_m = int( re_time_temp_list[0] )
            re_time_s = int( re_time_temp_list[1] + re_time_temp_list[2] )
        elif len(re_time_temp_list) == 4:
            re_time_m = int( re_time_temp_list[0] + re_time_temp_list[1] )
            re_time_s = int( re_time_temp_list[2] + re_time_temp_list[3] )

        #--re_time_mi--
        re_time_mi = int(row[23])

        #--re_time--
        re_time = float(str(re_time_m * 60 + re_time_s) + "." + str(re_time_mi))

        if flag == 0:
            event = [team_id, offense_no, game_status, h_a, player_id, action_id, d, x, y, re_time]
            #チーム，オフェンス番号，前半or後半，ホームアウェイ，プレイヤー，行動，
            #攻撃方向, x, y, ハーフ開始からの相対時刻（秒）

            if flag2 == 1:
                play[game_id] = [event]
                flag2 = 0
            else:
                play[game_id].append(event)
        

def input_tracking():
#--input tracking data--

    for i in range(len(game_ids)):
        game_id = game_ids[i]

        tracking_dir = "tracking/" + str(game_id)

        f_start, f_end, s_start, s_end = input_frame( tracking_dir )
        #前半・後半の開始，終了時刻読み込み

        filename = tracking_dir + "/udp.out"

        fin = open(filename)

        print filename
        count0 = 0
        count1 = 0
        count2 = 0
        flag2 = 1#一つ目のログを識別するためのフラグ
        for row in fin:
            temp = row.rstrip("\r\n").split(":")
            flag3 = 0#前半or後半に含まれないログを削除するためのフラグ

            if len(temp) == 4:
        
                if len(temp[0]) != 0 and temp[0].isdigit() == True:
                    frame_id = int(temp[0])

                if f_start <= frame_id and frame_id <= f_end:
                    game_status = 1
                    re_time = float(frame_id - f_start) / 25
                elif s_start <= frame_id and frame_id <= s_end:
                    game_status = 2
                    re_time = float(frame_id - s_start) / 25
                else:
                    flag3 = 1

                if flag3 == 0:

                    player_locs = temp[1].rstrip("\r\n").split(";")
                    num_systems = len(player_locs) - 1                            
                    for i in range(num_systems):
                        flag = 0#欠損など問題があるログを削除するためのフラグ
                        player_loc = player_locs[i].rstrip("\r\n").split(",")

                        if len(player_loc) == 6:

                            #--home or away--
                            if len(player_loc[0]) == 0 or player_loc[0].isdigit() == False:
                                flag = 1
                            else:
                                h_a = player_loc[0]
                                if h_a == "0" or h_a == "1":
                                    h_a = int(h_a)
                                    #0:away, 1:home
                                    if h_a == 0:
                                        h_a = 2#プレイデータに合わせる1:home, 2:away
                                else:
                                    flag = 1
        
                            #--player--
                            if len(player_loc[2]) == 0 or \
                                    len(player_loc[2].rstrip("\r\n").split(".")) != 1 or \
                                    player_loc[2].isdigit() == False:
                                flag = 1
                            else:
                                player_id = int(player_loc[2])
        
                            #--x axis--
                            if len(player_loc[3]) == 0 or \
                                    len(player_loc[3].rstrip("\r\n").split(".")) != 1 or \
                                    len(player_loc[3].rstrip("\r\n").split("-")) > 2:
                                flag = 1
                            else:
                                x = float(player_loc[3])
                                if x < xmin or xmax < x:
                                    flag = 1
        
                            #--y axis--
                            if len(player_loc[4]) == 0 or \
                                    len(player_loc[4].rstrip("\r\n").split(".")) != 1 or \
                                    len(player_loc[4].rstrip("\r\n").split("-")) > 2:
                                flag = 1
                            else:
                                y = float(player_loc[4])
                                if y < ymin or ymax < y:
                                    flag = 1

                            if flag == 0:
                                count0 += 1
                                event = [h_a, game_status, player_id, x, y, re_time]
                                #ホームアウェイ，前半or後半，プレイヤー，x, y, 
                                #ハーフ開始からの相対時刻（秒）
                                #print event
        
                                if flag2 == 1:
                                    tracking[game_id] = [event]
                                    flag2 = 0
                                else:
                                    tracking[game_id].append(event)
                            #elif flag == 1
                            #count1 += 1
                
        #print count0
        #print count1

def input_frame( dir ):
#--input frame no--

    fin = open(dir + "/frame.csv")
    reader = csv.reader(fin)
    header = next(reader)

    temp = next(reader)

    f_start = int(temp[1])#前半開始
    f_end = int(temp[2])#前半終了
    s_start = int(temp[3])
    s_end = int(temp[4])
    
    return(f_start, f_end, s_start, s_end)


def process():
    
    #play 処理前
    #チーム，オフェンス番号，前半or後半，ホームアウェイ，プレイヤー，行動，
    #攻撃方向, x, y, ハーフ開始からの相対時刻（秒）

    #play 処理後
    #チーム，オフェンス番号，前半or後半，（ホームアウェイ），プレイヤー，行動，
    #（攻撃方向）, x, y, 「【trackingの時間粒度に変換】ハーフ開始からの相対時刻（秒）」


    #tracking 処理前
    #ホームアウェイ，前半or後半，プレイヤー，x, y, ハーフ開始からの相対時刻（秒）

    #tracking 処理後
    #「チーム」，「オフェンス番号」，（ホームアウェイ），前半or後半，プレイヤー，
    #x, y, ハーフ開始からの相対時刻（秒）

    t0 = time()
    print "*play time convert"
    play_time_convert()#playの時間をtrackingの時間粒度に合わせる
    print "play time convert:%f \n" % (time()-t0)

    t0 = time()
    print "*team name"
    team_name()#playを使ってtrackingのログにチーム名を付加する
    print "team name:%f \n" % (time()-t0)    

    t0 = time()
    print "*tracking segmentation"
    tracking_segmentation()#playのオフェンス番号を用いて該当する部分のトラッキングデータを取り出す
    print "tracking_segmentation:%f \n" % (time()-t0)


def play_time_convert():

    for i in range(len(game_ids)):
        game_id = game_ids[i]
        #print game_id

        P = np.array(play[game_id])
        T = np.array(tracking[game_id])
        #print np.shape(P)
        #print np.shape(T)
        
        T_first_half_ind = np.where(T[:,1] == 1)[0]
        T_second_half_ind = np.where(T[:,1] == 2)[0]

        T_time_first = T[T_first_half_ind,5]
        T_time_second = T[T_second_half_ind,5]

        T_time_first_uniq = np.unique(T_time_first)
        T_time_second_uniq = np.unique(T_time_second)


        P_first_half_ind = np.where(P[:,2] == 1)[0]
        for n in range(len(P_first_half_ind)):
            ind = P_first_half_ind[n]
            P_time = P[ind][9]

            lst = [P_time for i in range(len(T_time_first_uniq))]
            lst = np.array(lst)
            diff = np.abs(lst - T_time_first_uniq)
            mini = np.min(diff)
            mini_ind = np.where( diff == mini )[0][0]
            new_P_time = T_time_first_uniq[mini_ind]

            P[ind][9] = new_P_time


        P_second_half_ind = np.where(P[:,2] == 2)[0]
        for n in range(len(P_second_half_ind)):
            ind = P_second_half_ind[n]
            P_time = P[ind][9]

            lst = [P_time for i in range(len(T_time_second_uniq))]
            lst = np.array(lst)
            diff = np.abs(lst - T_time_second_uniq)
            mini = np.min(diff)
            mini_ind = np.where( diff == mini )[0][0]
            new_P_time = T_time_second_uniq[mini_ind]

            P[ind][9] = new_P_time

        play[game_id] = P


def team_name():
    
    for i in range(len(game_ids)):
        game_id = game_ids[i]

        P = np.array(play[game_id])
        T = np.array(tracking[game_id])
    
        h_a_team = {}
        for j in range(np.shape(P)[0]):
          h_a = P[j][3]
          if h_a not in h_a_team:
              team_id = P[j][0]
              h_a_team[h_a] = team_id

        for j in range(np.shape(T)[0]):
            T[j][0] = h_a_team[T[j][0]]
        
        tracking[game_id] = T


def tracking_segmentation():
    
    new_tracking = defaultdict(int)

    for i in range(len(game_ids)):
        game_id = game_ids[i]

        P = np.array(play[game_id])
        T = np.array(tracking[game_id])
        O_nos = offense_nos[game_id]

        n = 0
        flag = 0
        for j in range(len(O_nos)):
            O_no = O_nos[j]
            O_no_ind = np.where(P[:,1] == O_no)[0]
            P_offense = P[O_no_ind,:]

            if len(P_offense) != 0:
                #print P_offense
                O_start = P_offense[0][9]
                O_end = P_offense[np.shape(P_offense)[0]-1][9]
                #print "%f %f \n" % (O_start, O_end)

                while True:
                    
                    event = list(T[n,:])
                    t = event[5]
                    print event
                    if O_start <= t:
                        event = list(float(O_no)).extend(event)
                        print event
                     


                    #if flag == 0:
                     
                #else:
                    n += 1
                     


#--main--
input()#データ読み込み

process()#playとtrackingを紐付ける






'''
            #分析対象のチームの攻撃方向1，相手チームの攻撃方向2となるようにx,yを修正
            if team_dic[team_id] == 0 and d == 2:
                #分析対象のチームで方向2のときは反転
                event = np.array([[team_dic[team_id], h_a, \
                                       player_dic[team_id][player_id], \
                                       position_dic[position_id], \
                                       action_dic[action_id], \
                                       x * -1, y * -1, re_time]])
            elif team_dic[team_id] != 0 and d == 1:
                #相手チームで方向1のときは反転
                event = np.array([[team_dic[team_id], h_a, \
                                       player_dic[team_id][player_id], \
                                       position_dic[position_id], \
                                       action_dic[action_id], \
                                       x * -1, y * -1, re_time]])
            else:

    for team_id in team_dic.iterkeys():
        print team_id
        print "%d %s" % (team_id, team_dic[team_id])
        for player_id in player_dic[team_id].iterkeys():
            print "%d %d %s" % (team_id, player_id, player_dic[team_id][player_id])
'''
