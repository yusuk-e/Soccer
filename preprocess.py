# -*- coding:utf-8 -*-

from time import time
from collections import defaultdict
import csv
import sys
import os
import numpy as np
import matplotlib
#matplotlib.use('Agg') #DIPLAYの設定
import matplotlib.pyplot as plt
from PIL import Image

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
except_game_id = [2015072506, 2015071507, 2015072921]
#2015072506 後半だけframeの後に:が二つ入っている
#2015081507 後半だけログの最後の;:がなく変な改行が入っている
#2015072921 frame.csvの前半開始と前半終了が同じ時間になっている

#--scala--
xmin = -5250
xmax = 5250
ymin = -3400
ymax = 3400

#--data--
play = defaultdict(int)#プレイデータ play[game_id]
new_play = defaultdict(int)
tracking = defaultdict(int)#トラッキングデータ tracking[game_id]
new_tracking = defaultdict(int)


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
    #print tracking


def input_play():
#--input play data--

    fin = open(play_file)
    print play_file

    reader = csv.reader(fin)
    header = next(reader)#ヘッダとばし

    for row in reader:
        flag = 0#欠損など問題のあるログを削除するためのフラグ

        if toNumber(row[0]) == "False":
            flag = 1
        else:
            game_id = int(row[0])

        if game_id not in except_game_id:

            #--game--
            if game_id not in game_ids:
                game_ids.append(game_id)
                offense_nos[game_id] = []
                flag2 = 1#一つ目のログを識別するためのフラグ

            #--game_status--
            if toNumber(row[2]) == "False":
                flag = 1
            else:
                game_status = int(row[2])#game_status:前半1or後半2

            #--team--
                if int(row[3]) == 0 or toNumber(row[3]) == "False":#row[3]==0:前後半開始終了,中断を除く
                    flag = 1
                else:
                    team_id = int(row[3])
                    if team_id not in team_dic:
                        team_name = row[4]
                        team_dic[team_id] = team_name
                        player_dic[team_id] = {}
                        #print "%d %s" % (team_id, team_dic[team_id])

            #--player--
            if toNumber(row[7]) == "False":
                flag = 1
            else:
                player_id = int(row[7])
                if player_id not in player_dic[team_id]:
                    player_name = row[6]
                    player_dic[team_id][player_id] = player_name

            #--action--
            if toNumber(row[9]) == "False":
                flag = 1
            else:
                action_id = int(row[9])
                if action_id not in action_dic:
                    action_name = row[10]
                    action_dic[action_id] = action_name
                    #print "%d %s" % (action_id, action_dic[action_id])

            #--home away--
            if toNumber(row[12]) == "False":
                flag = 1
            else:
                h_a = int(row[12])#1:home, 2:away

            #--offense no--
            if toNumber(row[13]) == "False":
                flag = 1
            else:
                offense_no = int(row[13])
                if offense_no not in offense_nos[game_id]:
                    offense_nos[game_id].append(offense_no)

            #--x axis--
            if toNumber(row[15]) == "False":
                flag = 1
            else:
                x = float(row[15]) * 100 / 3
                if x < xmin or xmax < x:
                    flag = 1
                
            #--y axis--
            if toNumber(row[16]) == "False":
                flag = 1
            else:
                y = float(row[16]) * -1 * 100 / 3
                if y < ymin or ymax < y:
                    flag = 1
                #x,y座標の変換（トラッキングデータに合わせる）

            #--direction--攻撃方向
            if toNumber(row[17]) == "False":
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
    #game_ids = [2015072921]
    for i in range(len(game_ids)):
        game_id = game_ids[i]

        tracking_dir = "tracking/" + str(game_id)

        f_start, f_end, s_start, s_end = input_frame( tracking_dir )
        #前半・後半の開始，終了時刻読み込み
        #print f_start
        #print f_end
        #print s_start
        #print s_end
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
                    #print frame_id
                if f_start <= frame_id and frame_id <= f_end:
                    game_status = 1
                    #print game_status
                    re_time = float(frame_id - f_start) / 25
                elif s_start <= frame_id and frame_id <= s_end:
                    #print game_status
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
                            if toNumber(player_loc[0]) == "False":
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
                            if len(player_loc[2].rstrip("\r\n").split(".")) != 1 or \
                                    toNumber(player_loc[2]) == "False":
                                flag = 1
                            else:
                                player_id = int(player_loc[2])
        
                            #--x axis--
                            if toNumber(player_loc[3]) == "False" or \
                                    len(player_loc[3].rstrip("\r\n").split(".")) != 1:
                                flag = 1
                            else:
                                x = float(player_loc[3])
                                if x < xmin or xmax < x:
                                    flag = 1
        
                            #--y axis--
                            if toNumber(player_loc[4]) == "False" or \
                                    len(player_loc[4].rstrip("\r\n").split(".")) != 1:
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


def toNumber(num_str):
#--文字列を適切な型の数値に変換する
    try:
        value=float(num_str)
        if value==int(value):
            return int(value)
    except ValueError:
        return "False"


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
#--pre processing--
    
    #play 処理前
    #チーム，オフェンス番号，前半or後半，ホームアウェイ，プレイヤー，行動，
    #攻撃方向, x, y, ハーフ開始からの相対時刻（秒）

    #play 処理後
    #チーム，オフェンス番号，前半or後半，（ホームアウェイ），プレイヤー，行動，
    #（攻撃方向）, x, y, 「【trackingの時間粒度に変換】ハーフ開始からの相対時刻（秒）」


    #tracking 処理前
    #ホームアウェイ，前半or後半，プレイヤー，x, y, ハーフ開始からの相対時刻（秒）

    #tracking 処理後
    #「オフェンス番号」，「チーム」，前半or後半，プレイヤー，
    #x, y, ハーフ開始からの相対時刻（秒）

    print "*preprocess"

    t0 = time()
    #print "*play time convert"
    play_time_convert()#playの時間をtrackingの時間粒度に合わせる
    print "play time convert:%f" % (time()-t0)

    t0 = time()
    #print "*team name"
    team_name()#playを使ってtrackingのログにチーム名を付加する
    print "team name:%f" % (time()-t0)    

    t0 = time()
    #print "*tracking segmentation"
    tracking_segmentation()#playのオフェンス番号を用いて該当する部分のトラッキングデータを取り出す
    print "tracking_segmentation:%f" % (time()-t0)

    t0 = time()
    #print "*reverse"
    reverse()#前後半で反転させる
    print "reverse:%f" % (time()-t0)

    #print "\n"


def play_time_convert():
#--playの時間をtrackingの時間粒度に合わせる--

    for i in range(len(game_ids)):
        game_id = game_ids[i]
        #print game_id

        P = np.array(play[game_id])
        T = np.array(tracking[game_id])
        #print np.where(T[:,4] < 0)
        #print len(np.where(T[:,4] < 0)[0])
        #for n in range(1000):
        #    print T[n,:]
        #print P
        #print T
        #print np.shape(P)
        #print np.shape(T)

        T_first_half_ids = np.where(T[:,1] == 1)[0]
        T_second_half_ids = np.where(T[:,1] == 2)[0]
        #print T_first_half_ids
        #print T_second_half_ids
        T_time_first = T[T_first_half_ids,5]
        T_time_second = T[T_second_half_ids,5]
        #print T_time_second
        T_time_first_uniq = np.unique(T_time_first)
        T_time_second_uniq = np.unique(T_time_second)
        #print T_time_second_uniq

        P_first_half_ids = np.where(P[:,2] == 1)[0]
        for n in range(len(P_first_half_ids)):
            ids = P_first_half_ids[n]
            P_time = P[ids][9]

            lst = [P_time for i in range(len(T_time_first_uniq))]
            lst = np.array(lst)
            diff = np.abs(lst - T_time_first_uniq)
            mini = np.min(diff)
            mini_ids = np.where( diff == mini )[0][0]
            new_P_time = T_time_first_uniq[mini_ids]

            P[ids][9] = new_P_time


        P_second_half_ids = np.where(P[:,2] == 2)[0]
        for n in range(len(P_second_half_ids)):
            ids = P_second_half_ids[n]
            P_time = P[ids][9]

            lst = [P_time for i in range(len(T_time_second_uniq))]
            lst = np.array(lst)
            diff = np.abs(lst - T_time_second_uniq)
            #print diff
            mini = np.min(diff)
            mini_ids = np.where( diff == mini )[0][0]
            new_P_time = T_time_second_uniq[mini_ids]

            P[ids][9] = new_P_time

        new_play[game_id] = P


def team_name():
#--playを使ってtrackingのログにチーム名を付加する--
    
    for i in range(len(game_ids)):
        game_id = game_ids[i]

        P = new_play[game_id]
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
#--playのオフェンス番号を用いて該当する部分のトラッキングデータを取り出す--
    for i in range(len(game_ids)):
        game_id = game_ids[i]

        P = new_play[game_id]
        T = tracking[game_id]
        O_nos = offense_nos[game_id]

        n = 0
        flag = 0
        count1 = 0
        period = 0
        for j in range(len(O_nos)):
            O_no = O_nos[j]

            if O_no != 0:
                O_no_ids = np.where(P[:,1] == O_no)[0]
                P_offense = P[O_no_ids,:]

                if len(P_offense) != 0:
                    O_start = P_offense[0][9]
                    O_end = P_offense[np.shape(P_offense)[0]-1][9]
                    P_status = int(P_offense[0][2])

                    #print "%f %f \n" % (O_start, O_end)
                    period += (O_end - O_start)
                    while True:
                        if n == np.shape(T)[0]:
                            break

                        event = list(T[n,:])
                        t = event[5]
                        T_status = int(event[1])

                        if P_status == T_status:
                            if O_start <= t and t <= O_end:
                                count1 += 1
                                O_no_list = [O_no]
                                O_no_list.extend(event)
                                new_event= O_no_list
                                if flag == 0:
                                    new_tracking[game_id] = [new_event]
                                    flag = 1
                                else:
                                    new_tracking[game_id].append(new_event)

                            elif O_end < t:
                                break
                            
                        n += 1

        #print "%d %d" % (n, count1)
        #print period

def reverse():
#--前後半で反転させる--

    for i in range(len(game_ids)):
        game_id = game_ids[i]

        P = new_play[game_id]
        T = np.array(new_tracking[game_id])
        
        first_half_ids = np.where(P[:,2] == 1)[0]
        P_first_half = P[first_half_ids,:]

        anal_team_ids = np.where(P_first_half[:,0] == float(anal_team))[0]
        direction = P_first_half[anal_team_ids[0]][6]

        #anal_teamの攻撃方向が1になるように反転させる
        if direction == 1:#second_halfを反転
            reverse_status = 2
        elif direction == 2:#first_halfを反転
            reverse_status = 1

        for n in range(np.shape(P)[0]):
            game_status = P[n][2]
            if game_status == reverse_status:
                P[n][7] = -1 * P[n][7]
                P[n][8] = -1 * P[n][8]
        
        for n in range(np.shape(T)[0]):
            game_status = T[n][2]
            if game_status == reverse_status:
                T[n][4] = -1 * T[n][4]
                T[n][5] = -1 * T[n][5]
        
        new_play[game_id] = P
        new_tracking[game_id] = T


def output():
#--出力--    

    print "*output"

    t0 = time()
    file_output()#データをファイルに出力
    print "file output:%f" % (time()-t0)

    #print "\n"


def file_output():
#--データをファイルに出力--

    for i in range(len(game_ids)):
        game_id = game_ids[i]

        output_dir = "Dataset/" + str(anal_team) + "/" + str(game_id)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
        f = open(output_dir + "/play.csv", "w")
        csvWriter = csv.writer(f)
        P = np.array(new_play[game_id])
        for n in range(np.shape(P)[0]):
            p = list(P[n,:])
            event = [int(p[1]), int(p[0]), int(p[2]), int(p[4]), int(p[5]), round(p[7], 3), round(p[8], 3), round(p[9], 2)]
            #オフェンス番号，チーム，前半or後半，プレイヤー，行動，x, y, ハーフ開始からの相対時刻（秒）
            csvWriter.writerow(event)
        f.close()

        f = open(output_dir + "/tracking.csv", "w")
        csvWriter = csv.writer(f)
        T = np.array(new_tracking[game_id])
        for n in range(np.shape(T)[0]):
            t = list(T[n,:])
            event = [int(t[0]), int(t[1]), int(t[2]), int(t[3]), round(t[4], 3), round(t[5], 3), round(t[6], 2)]
            #オフェンス番号，チーム，前半or後半，プレイヤー，x, y, ハーフ開始からの相対時刻（秒）
            csvWriter.writerow(event)
        f.close()


        output_dir = "Dataset/" + str(anal_team) + "/dic"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        f = open(output_dir + "/game.csv", "w")
        for n in range(len(game_ids)):
            game_id = game_ids[n]
            f.write("%d\n" % game_id)
        f.close()

        f = open(output_dir + "/team.csv", "w")
        csvWriter = csv.writer(f)
        for team_id in team_dic.iterkeys():
            team_name = team_dic[team_id]
            pair = [team_id, team_name]
            csvWriter.writerow(pair)
        f.close()
        
        f = open(output_dir + "/player.csv", "w")
        csvWriter = csv.writer(f)
        for team_id in team_dic.iterkeys():
            for player_id in player_dic[team_id].iterkeys():
                player_name = player_dic[team_id][player_id]
                pair = [team_id, player_id, player_name]
                csvWriter.writerow(pair)
        f.close()

        f = open(output_dir + "/action.csv", "w")
        csvWriter = csv.writer(f)
        for action_id in action_dic.iterkeys():
            action_name = action_dic[action_id]
            pair = [action_id, action_name]
            csvWriter.writerow(pair)
        f.close()

        
def vis():
#--軌跡を描写--

    print "*visualization"

    t0 = time()
    vis_ball()#ボール軌跡を描写
    print "vis_ball:%f" % (time()-t0)
    
    t0 = time()
    vis_ball_player()#ボールとプレイヤー軌跡を描写
    print "vis_ball_player:%f" % (time()-t0)

    #print "\n"

def vis_ball():
#--ボール軌跡を描写--

    B_color = "yellow"
    B = "Ball"

    #im = Image.open('soccer.png')
    #im = np.array(im)

    for i in range(len(game_ids)):
        game_id = game_ids[i]

        P = new_play[game_id]
        T = new_tracking[game_id]
        O_nos = offense_nos[game_id]
        
        output_dir = "Dataset/" + str(anal_team) + "/" + str(game_id) + "/vis/Ball"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for j in range(len(O_nos)):
            O_no = O_nos[j]

            if O_no != 0:
                O_no_ids = np.where(P[:,1] == O_no)[0]
                P_offense = P[O_no_ids,:]

                if len(P_offense) != 0:
                    #print P_offense
                    x = P_offense[:,7]
                    y = P_offense[:,8]
                    
                    fig = plt.figure(figsize=(16,8))
                    plt.title(B, color=B_color, size= 35, loc='left')
                    plt.tick_params(labelbottom='off',labelleft='off')
                    #plt.imshow(im)

                    plt.quiver(x[:-1], y[:-1], x[1:]-x[:-1], y[1:]-y[:-1], width=0.002, \
                               headwidth=5, headlength=7, headaxislength=7, scale_units='xy',\
                               angles='xy', scale=1, color='grey')
                    #angles='xy', scale=1, color='darkcyan')
                    #quive(x,y,u,v) (x,y):始点 (u,v):方向ベクトル
                    plt.scatter(x,y,s = 40, color=B_color,alpha=0.5)
                    plt.axis([-5250, 5250, -3400, 3400])
                    
                    plt.savefig(output_dir + "/no" + str(O_no) +'.png', transparent=True)
                    plt.close()

def vis_ball_player():
#--ボールとプレイヤー軌跡を描写--

    B_color = "yellow"
    B = "Ball"

    #im = Image.open('soccer.png')
    #im = np.array(im)

    for i in range(len(game_ids)):
        game_id = game_ids[i]

        P = new_play[game_id]
        T = new_tracking[game_id]
        O_nos = offense_nos[game_id]
        #for n in range(1000):
        #    print T[n,:]
            
        team_line = P[:,0]
        team_line_uniq = np.unique(team_line)
        
        output_dir = "Dataset/" + str(anal_team) + "/" + str(game_id) + "/vis/Ball_Player"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for j in range(len(O_nos)):
            O_no = O_nos[j]

            if O_no != 0:
                O_no_ids = np.where(P[:,1] == O_no)[0]
                P_offense = P[O_no_ids,:]

                if len(P_offense) != 0:

                    team_line = P_offense[:,0]                    
                    if len(np.where(team_line == team_line_uniq[0])[0]) < len(np.where(team_line == team_line_uniq[1])[0]):
                        O_team = team_line_uniq[1]
                    else:
                        O_team = team_line_uniq[0]

                    #print O_team

                    if O_team == float(anal_team):
                        OD_anal = "Offense"
                        OD_anal_color = "red"
                        OD_not_anal = "Diffense"
                        OD_not_anal_color = "blue"
                        ball_fig = 1
                    else:
                        OD_anal = "Diffense"
                        OD_anal_color = "blue"
                        OD_not_anal = "Offense"
                        OD_not_anal_color = "red"
                        ball_fig = 2


                    fig = plt.figure(figsize=(16,16))

                    #--anal team--
                    plt.subplot("211")
                    #print T[:,0]
                    #print O_no
                    #print T[:,2]
                    #print anal_team

                    T_O_no_ids = np.where((T[:,0] == O_no) & (T[:,1] == float(anal_team)))[0]
                    T_offense = T[T_O_no_ids,:]

                    #player_line = T_offense[:,3]
                    #player_line_uniq = np.unique(player_line)
                    #for n in range(len(player_line_uniq)):
                        
                    x = T_offense[:,4]
                    y = T_offense[:,5]
                    #print x
                    #print y
                    
                    plt.scatter(x, y, s = 10, color = OD_anal_color, alpha = 0.5)
                    plt.axis([-5250, 5250, -3400, 3400])
                    
                    plt.title(OD_anal, color=OD_anal_color, size=45, loc='left')
                    plt.ylabel(str(anal_team),size=45)
                    plt.tick_params(labelbottom='off',labelleft='off')

                    if ball_fig == 1:
                        O_no_ids = np.where(P[:,1] == O_no)[0]
                        P_offense = P[O_no_ids,:]

                        if len(P_offense) != 0:

                            x = P_offense[:,7]
                            y = P_offense[:,8]

                            plt.quiver(x[:-1], y[:-1], x[1:]-x[:-1], y[1:]-y[:-1], width=0.002, \
                                           headwidth=5, headlength=7, headaxislength=7, scale_units='xy',\
                                           angles='xy', scale=1, color='grey')
                            #angles='xy', scale=1, color='darkcyan')
                            #quive(x,y,u,v) (x,y):始点 (u,v):方向ベクトル
                            plt.scatter(x,y,s = 55, color=B_color,alpha=0.8)


                    #--not anal team--
                    plt.subplot("212")

                    not_anal_team = team_line_uniq[np.where(team_line_uniq != float(anal_team))[0]]
                    #print not_anal_team[0]

                    T_O_no_ids = np.where((T[:,0] == O_no) & (T[:,1] == not_anal_team[0]))[0]
                    T_offense = T[T_O_no_ids,:]
                    #print T_O_no_ids
                    #print T_offense

                    #player_line = T_offense[:,3]
                    #player_line_uniq = np.unique(player_line)
                    #for n in range(len(player_line_uniq)):
                        
                    x = T_offense[:,4]
                    y = T_offense[:,5]

                    plt.scatter(x, y, s = 10, color = OD_not_anal_color, alpha = 0.5)
                    plt.axis([-5250, 5250, -3400, 3400])

                    plt.title(OD_not_anal, color=OD_not_anal_color, size=45, loc='left')
                    plt.ylabel(str(int(not_anal_team)),size=45)
                    plt.tick_params(labelbottom='off',labelleft='off')

                    if ball_fig == 2:
                        O_no_ids = np.where(P[:,1] == O_no)[0]
                        P_offense = P[O_no_ids,:]

                        if len(P_offense) != 0:
                            #print P_offense
                            x = P_offense[:,7]
                            y = P_offense[:,8]

                            plt.quiver(x[:-1], y[:-1], x[1:]-x[:-1], y[1:]-y[:-1], width=0.002, \
                                           headwidth=5, headlength=7, headaxislength=7, scale_units='xy',\
                                           angles='xy', scale=1, color='grey')
                            #angles='xy', scale=1, color='darkcyan')
                            #quive(x,y,u,v) (x,y):始点 (u,v):方向ベクトル
                            plt.scatter(x,y,s = 55, color=B_color,alpha=0.8)


                    plt.savefig(output_dir + "/no" + str(O_no) +'.png', transparent=True)
                    plt.close()



#--main--
input()#データ読み込み

process()#playとtrackingを紐付ける

output()#出力

vis()#軌跡を描写
