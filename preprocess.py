# -*- coding:utf-8 -*-

from time import time
from collections import defaultdict
import csv
import sys


#--sys variable--
argvs = sys.argv
argc = len(argvs)
if (argc != 2):
    print "Usage: #python %s team_no" % argvs[0]
    quit()
anal_team = argvs[1]

#------variable------

#--file--
play_file = "play/" + anal_team + ".csv"
#play_file = "play/" + anal_team + "_small.csv"

#--dictionary--
team_dic = {}
player_dic = {}
action_dic = {}

#--list--
game_ids = []
game_statuses = [] #game_status:前半1or後半2

#--scala--

#--data--
play = defaultdict(lambda: defaultdict(int))#プレイデータ play[game_id][game_status]
tracking = defaultdict(lambda: defaultdict(int))#トラッキングデータ tracking[game_id][game_status]


def input():
#--input--

    t0 = time()
    input_play()
    print "input_play time:%f \n" % (time()-t0)

    t0 = time()
    input_tracking()
    print "input_tracking time:%f \n" % (time()-t0)


def input_play():
#--input play data--

    fin = open(play_file)
    print play_file

    reader = csv.reader(fin)
    header = next(reader)#ヘッダとばし

    prev_game_status = -1
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

        #--game_status--
        if len(row[2]) == 0:
            flag = 1
        else:
            game_status = int(row[2])
            if game_status not in game_statuses:
                game_statuses.append(game_status)
            if prev_game_status != game_status:
                flag2 = 1
                prev_game_status = game_status

        #--team--
        if len(row[3]) == 0 or int(row[3]) == 0:#row[3]==0:前後半開始終了,中断を除く
            flag = 1
        else:
            team_id = int(row[3])
            if team_id not in team_dic:
                team_name = row[4]
                team_dic[team_id] = team_name
                player_dic[team_id] = {}
                #print "%d %s" % (team_id, team_dic[team_id])

        #--player--
        if len(row[7]) == 0:
            flag = 1
        else:
            player_id = int(row[7])
            if player_id not in player_dic[team_id]:
                player_name = row[6]
                player_dic[team_id][player_id] = player_name

        #--action--
        if len(row[9]) == 0:
            flag = 1
        else:
            action_id = int(row[9])
            if action_id not in action_dic:
                action_name = row[10]
                action_dic[action_id] = action_name
                #print "%d %s" % (action_id, action_dic[action_id])

        #--home away--
        if len(row[12]) == 0:
            flag = 1
        else:
            h_a = int(row[12])#1:home, 2:away

        #--x axis--
        if len(row[15]) == 0:
            flag = 1
        else:
            x = float(row[15]) * 100 / 3

        #--y axis--
        if len(row[16]) == 0:
            flag = 1
        else:
            y = float(row[16]) * -1 * 100 / 3
            #x,y座標の変換（トラッキングデータに合わせる）

        #--direction--攻撃方向
        if len(row[17]) == 0:
            flag = 1
        else:
            d = int(row[17])
            #前後半で1か2．対象とするチームが1になるように後で反転させる

        #--re_time_s--
        re_time_s = int(row[22])

        #--re_time_m--
        re_time_m = int(row[23])

        #--re_time--
        re_time = float(str(re_time_s) + "." + str(re_time_m))

        if flag == 0:
            event = [team_id, h_a, player_id, action_id, d, x, y, re_time]
            #チーム，ホームアウェイ，プレイヤー，行動，攻撃方向, x, y, 
            #ハーフ開始からの相対時刻（秒）

            if flag2 == 1:
                play[game_id][game_status] = [event]
                flag2 = 0
            else:
                play[game_id][game_status].append(event)
        

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

        flag2 = 0
        flag3 = 0

        for row in fin:
            temp = row.rstrip("\r\n").split(":")
            flag = 0
            if len(temp) == 4:
        
                if len(temp[0]) != 0 and temp[0].isdigit() == True:
                    frame_id = int(temp[0])
                    player_locs = temp[1].rstrip("\r\n").split(";")
                    ball_loc = temp[2].rstrip("\r\n").split(";")[0].rstrip("\r\n").split(",")

                    #--possesion team (home or away)--
                    if len(ball_loc[4]) == 0:
                        flag = 1
                    else:
                        possesion_h_a = ball_loc[4]
                        if possesion_h_a == "H":
                            possesion_h_a = 1
                        elif possesion_h_a == "A":
                            possesion_h_a = 0

                    #--ball status (Alive or Dead)--
                    if len(ball_loc[5]) == 0:
                        flag = 1
                    else:
                        ball_status = ball_loc[5]
                        if ball_status == "Alive":
                            ball_status = 0
                        elif ball_status == "Dead":
                            ball_status = 1
                            
                    num_systems = len(player_locs) - 1
                    flag4 = 0
                    for i in range(num_systems):
                        if len(player_locs[i].rstrip("\r\n").split(",")) != 6:
                            flag4 = 1

                    if f_start <= frame_id and frame_id <= f_end:
                    
                        if len(ball_loc) > 5 and flag4 == 0:

                            game_status = 1
                            re_time = float(frame_id - f_start) / 25
                            
                            for i in range(num_systems):
                                player_loc = player_locs[i].rstrip("\r\n").split(",")

                                #--home or away--
                                if len(player_loc[0]) == 0:
                                    flag = 1
                                else:
                                    h_a = player_loc[0]
                                    if h_a == "0" or h_a == "1":
                                        h_a = int(h_a)
        
                                #--player--
                                if len(player_loc[2]) == 0 or \
                                        len(player_loc[2].rstrip("\r\n")\
                                                .split(".")) != 1 or \
                                                player_loc[2].isdigit() == False:
                                    flag = 1
                                else:
                                    player_id = int(player_loc[2])
        
                                #--x axis--
                                if len(player_loc[3]) == 0:
                                    flag = 1
                                else:
                                    x = float(player_loc[3])
        
                                #--y axis--
                                if len(player_loc[4]) == 0:
                                    flag = 1
                                else:
                                    y = float(player_loc[4])

                                if flag == 0:
                                    event = [h_a, player_id, x, y, re_time]
                                    #ホームアウェイ，プレイヤー，x, y, 
                                    #ハーフ開始からの相対時刻（秒）
        
                                    if flag2 == 0:
                                        tracking[game_id][game_status] = [event]
                                        flag2 = 1
                                    else:
                                        tracking[game_id][game_status].append(event)
                                            
        
                    elif s_start <= frame_id and frame_id <= s_end:

                        if flag3 == 0:
                            flag2 = 0
                            flag3 = 1

                        if len(ball_loc) > 5 and flag4 == 0:

                            game_status = 2
                            re_time = float(frame_id - f_start) / 25

                            for i in range(num_systems):
                                player_loc = player_locs[i].rstrip("\r\n").split(",")

                                #--home or away--
                                if len(player_loc[0]) == 0:
                                    flag = 1
                                else:
                                    h_a = player_loc[0]
                                    if h_a == "0" or h_a == "1":
                                        h_a = int(h_a)
        
                                #--player--
                                if len(player_loc[2]) == 0 or \
                                        len(player_loc[2].rstrip("\r\n")\
                                                .split(".")) != 1 or \
                                                player_loc[2].isdigit() == False:
                                    flag = 1
                                else:
                                    player_id = int(player_loc[2])
        
                                #--x axis--
                                if len(player_loc[3]) == 0:
                                    flag = 1
                                else:
                                    x = float(player_loc[3])
        
                                #--y axis--
                                if len(player_loc[4]) == 0:
                                    flag = 1
                                else:
                                    y = float(player_loc[4])


                                if flag == 0:
                                    event = [h_a, player_id, x, y, re_time]
                                    #ホームアウェイ，プレイヤー，x, y, 
                                    #ハーフ開始からの相対時刻（秒）
        
                                    if flag2 == 0:
                                        tracking[game_id][game_status] = [event]
                                        flag2 = 1
                                    else:
                                        tracking[game_id][game_status].append(event)


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




#--main--
input()#データ読み込み
pdb.set_trace()




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
