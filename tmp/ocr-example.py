import os
import time
import pytesseract
import cv2
from difflib import get_close_matches
from pathlib import Path
import json
from pathlib import Path
import re


ocrCONFIG = '--psm 6, -c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.:-_'
ocrCONFIG_NUM = '--psm 6, -c tessedit_char_whitelist=01234567890:'

newstatDICT = {}
scoreboard_STATS = {}
playerSTAT = {}
playstats_combine = {}
tmp_rename = {}
tmp_renam2 = {}
apiNAMES = []



def ocr_process(img_CORDS, ocrCONFIG):
    scale_percent = 300
    width = int(img_CORDS.shape[1] * scale_percent / 100)
    height = int(img_CORDS.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img_CORDS, dim, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    invert = cv2.bitwise_not(gray)
    text = pytesseract.image_to_string(invert, lang="eng",
                                       config=ocrCONFIG)
    replace_string = text.replace('\n', "")
    return replace_string


def closeMatches(names, ocrRESULT):
    match = get_close_matches(ocrRESULT, names)
    print(match)
    return match


def scoreboard_html(current_map):
    f = open('base-new-template.html', 'w')
    payload_list = ['mpl_combat_gauss', 'mpl_combat_fission']
    capture_point_list = ['mpl_combat_dyson', 'mpl_combat_combustion']
    message_payload = """<html>
        <head><meta http-equiv=refresh content=45></head>
        <title>Stats</title>
			<style>
				th, td {
				text-align: center;
				height: 40px;}

				.table_stats{
				color: white;
				border-collapse: separate;
				border-spacing: 0 0.5em;
				width: 100%;}

				#table_orange th, #table_orange td {
				background-color: darkorange;}

				#table_blue th, #table_blue td {
				background-color: dodgerblue;}


				.total_row_orange td {
				background-color: orangered !important;
				font-weight:bold;}


				.total_row_blue td {
				background-color: deepskyblue !important;
				font-weight:bold;}

				.invisible_cell {
				background-color: transparent !important;
				border-collapse: collapse;}

				.split_div {
				width: 50%;
				float: left;}

			</style>
            <div class="split_div">
              <table class="table_stats" id="table_orange">
                <tr.orange>
                    <th>DAMAGE</th>
                    <th>DEATHS</th>
                    <th>ASSISTS</th>
                    <th>KILLS</th>
                    <th>OBJ.TIME</th>
                    <th>OBJ.ELIM</th>
                    <th>ELIM</th>
                    <th class="invisible_cell"></th>
                </tr.orange>


                </tr>
            </table>
        </div>
        <div class="split_div">
            <table class="table_stats" id="table_blue">
                <tr.blue>
                    <th class="invisible_cell"></th>
                    <th>ELIM</th>
                    <th>OBJ.ELIM</th>
                    <th>OBJ.DMG</th>
                    <th>KILLS</th>
                    <th>ASSISTS</th>
                    <th>DEATHS</th>
                    <th>DAMAGE</th>

                </tr.blue>


                </tr>
            </table>
        </div>
    </html>"""

    message_capturepoint = """<html>
            <head><meta http-equiv=refresh content=45></head>
            <title>Stats</title>
			<style>
				th, td {
				text-align: center;
				height: 40px;}

				.table_stats{
				color: white;
				border-collapse: separate;
				border-spacing: 0 0.5em;
				width: 100%;}

				#table_orange th, #table_orange td {
				background-color: darkorange;}

				#table_blue th, #table_blue td {
				background-color: dodgerblue;}


				.total_row_orange td {
				background-color: orangered !important;
				font-weight:bold;}


				.total_row_blue td {
				background-color: deepskyblue !important;
				font-weight:bold;}

				.invisible_cell {
				background-color: transparent !important;
				border-collapse: collapse;}

				.split_div {
				width: 50%;
				float: left;}

			</style>
                <div class="split_div">
                  <table class="table_stats" id="table_orange">
                    <tr.orange>
                        <th>DAMAGE</th>
                        <th>DEATHS</th>
                        <th>ASSISTS</th>
                        <th>KILLS</th>
                        <th>OBJ.DMG</th>
                        <th>OBJ.TIME</th>
                        <th>OBJ.ELIM</th>
                        <th>ELIM</th>
                        <th class="invisible_cell"></th>
                    </tr.orange>


                    </tr>
                </table>
            </div>
            <div class="split_div">
                <table class="table_stats" id="table_blue">
                    <tr.blue>
                        <th class="invisible_cell"></th>
                        <th>ELIM</th>
                        <th>OBJ.ELIM</th>
                        <th>OBJ.TIME</th>
                        <th>OBJ.DMG</th>
                        <th>KILLS</th>
                        <th>ASSISTS</th>
                        <th>DEATHS</th>
                        <th>DAMAGE</th>

                    </tr.blue>


                    </tr>
                </table>
            </div>
        </html>"""
    if current_map in payload_list:
        f.write(message_payload)
    elif current_map in capture_point_list:
        f.write(message_capturepoint)
    f.close()


def createstats_payload(mapname):
    scoreboard_html(mapname)
    with open('base-new-template.html', 'r') as f:
        in_file = f.readlines()
    out_file = []
    for line in in_file:
        out_file.append(line)
        if '</tr.orange>' in line:
            for key, value in tmp_renam2.items():
                if value['team'] == 1:
                    name = key
                    elim = value['elim']
                    objELIM = value['obj.elim']
                    objTIME = value['obj.time']
                    kills = value['kills']
                    assists = value['assists']
                    deaths = value['deaths']
                    damage = value['damage']
                    orange = """<tr>

                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>

                        <td>%s</td>
                        </tr>\n""" % (damage, deaths, assists, kills, objTIME, objELIM, elim, name)

                    out_file.append(orange)
        elif '</tr.blue>' in line:
            for key, value in tmp_renam2.items():
                if value['team'] == 0:
                    name = key
                    elim = value['elim']
                    objELIM = value['obj.elim']
                    objDMG = value['obj.dmg']
                    kills = value['kills']
                    assists = value['assists']
                    deaths = value['deaths']
                    damage = value['damage']
                    blue = """<tr>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>

                        </tr> \n""" % (name, elim, objELIM, objDMG, kills, assists, deaths, damage)
                    out_file.append(blue)

    with open('outnew3.html', 'w') as f:
        f.writelines(out_file)


def createstats_capture_point(mapname):
    scoreboard_html(mapname)
    with open('base-new-template.html', 'r') as f:
        in_file = f.readlines()
    out_file = []
    for line in in_file:
        out_file.append(line)
        if '</tr.orange>' in line:
            for key, value in tmp_renam2.items():
                if value['team'] == 1:
                    name = key
                    elim = value['elim']
                    objELIM = value['obj.elim']
                    objTIME = value['obj.time']
                    objDMG = value['obj.dmg']
                    kills = value['kills']
                    assists = value['assists']
                    deaths = value['deaths']
                    damage = value['damage']
                    orange = """<tr>

                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>

                        <td>%s</td>
                        </tr>\n""" % (damage, deaths, assists, kills, objDMG, objTIME, objELIM, elim, name)

                    out_file.append(orange)
        elif '</tr.blue>' in line:
            for key, value in tmp_renam2.items():
                if value['team'] == 0:
                    name = key
                    elim = value['elim']
                    objELIM = value['obj.elim']
                    objTIME = value['obj.time']
                    objDMG = value['obj.dmg']
                    kills = value['kills']
                    assists = value['assists']
                    deaths = value['deaths']
                    damage = value['damage']
                    blue = """<tr>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>

                        </tr> \n""" % (name, elim, objELIM, objTIME, objDMG, kills, assists, deaths, damage)
                    out_file.append(blue)

    with open('outnew3.html', 'w') as f:
        f.writelines(out_file)


def ocrSCOREBOARD(mapname, IMG):
    print(mapname)
    img = cv2.imread(IMG)
    ocrONLY_NAME_DONT_USE = {'blue 1': img[240:240 + 50, 280:280 + 415],
                             'blue 2': img[289:289 + 50, 280:280 + 415],
                             'blue 3': img[338:338 + 50, 280:280 + 415],
                             'blue 4': img[388:388 + 50, 280:280 + 415],
                             'orange 1': img[548:548 + 50, 280:280 + 415],
                             'orange 2': img[596:596 + 50, 280:280 + 415],
                             'orange 3': img[645:645 + 50, 280:280 + 415],
                             'orange 4': img[694:694 + 50, 280:280 + 415]}
    ocrONLY_NAME_16x9 = {'blue 1': img[300:300 + 56, 355:355 + 510],
                         'blue 2': img[362:362 + 56, 355:355 + 510],
                         'blue 3': img[420:420 + 56, 355:355 + 510],
                         'blue 4': img[480:480 + 56, 355:355 + 510],
                         'orange 1': img[681:681 + 56, 355:355 + 510],
                         'orange 2': img[740:740 + 56, 355:355 + 510],
                         'orange 3': img[800:800 + 56, 355:355 + 510],
                         'orange 4': img[860:860 + 56, 355:355 + 510]}
    ocrPAYLOAD_NUM_DONT_USE = {'blue 1':
                                   {'elim': img[242:242 + 47, 695:695 + 84],
                                    'obj.elim': img[242:242 + 47, 900:900 + 110],
                                    'obj.dmg': img[242:242 + 47, 1065:1065 + 140],
                                    'team': 0},
                               'blue 2':
                                   {'elim': img[292:292 + 47, 695:695 + 84],
                                    'obj.elim': img[292:292 + 47, 900:900 + 110],
                                    'obj.dmg': img[292:292 + 47, 1065:1065 + 140],
                                    'team': 0},
                               'blue 3':
                                   {'elim': img[340:340 + 47, 695:695 + 84],
                                    'obj.elim': img[340:340 + 47, 900:900 + 110],
                                    'obj.dmg': img[340:340 + 47, 1065:1065 + 140],
                                    'team': 0},
                               'blue 4':
                                   {'elim': img[388:388 + 47, 695:695 + 84],
                                    'obj.elim': img[388:388 + 47, 900:900 + 110],
                                    'obj.dmg': img[388:388 + 47, 1065:1065 + 140],
                                    'team': 0},
                               'orange 1':
                                   {'elim': img[550:550 + 47, 695:695 + 84],
                                    'obj.elim': img[550:550 + 47, 900:900 + 110],
                                    'obj.time': img[550:550 + 47, 1065:1065 + 140],
                                    'team': 1},
                               'orange 2':
                                   {'elim': img[598:598 + 47, 695:695 + 84],
                                    'obj.elim': img[598:598 + 47, 900:900 + 110],
                                    'obj.time': img[598:598 + 47, 1065:1065 + 140],
                                    'team': 1},
                               'orange 3':
                                   {'elim': img[645:645 + 47, 695:695 + 84],
                                    'obj.elim': img[645:645 + 47, 900:900 + 110],
                                    'obj.time': img[645:645 + 47, 1065:1065 + 140],
                                    'team': 1},
                               'orange 4':
                                   {'elim': img[695:695 + 47, 695:695 + 84],
                                    'obj.elim': img[695:695 + 47, 900:900 + 110],
                                    'obj.time': img[695:695 + 47, 1065:1065 + 140],
                                    'team': 1}}
    ocrPAYLOAD_NUM_16x9 = {'blue 1':
                               {'elim': img[302:302 + 55, 879:879 + 90],
                                'obj.elim': img[302:302 + 55, 1130:1130 + 125],
                                'obj.dmg': img[302:302 + 55, 1333:1333 + 147],
                                'team': 0},
                           'blue 2':
                               {'elim': img[362:362 + 56, 879:879 + 90],
                                'obj.elim': img[362:362 + 56, 1130:1130 + 125],
                                'obj.dmg': img[362:362 + 56, 1333:1333 + 147],
                                'team': 0},
                           'blue 3':
                               {'elim': img[420:420 + 56, 879:879 + 90],
                                'obj.elim': img[420:420 + 56, 1130:1130 + 125],
                                'obj.dmg': img[420:420 + 56, 1333:1333 + 147],
                                'team': 0},
                           'blue 4':
                               {'elim': img[480:480 + 56, 879:879 + 90],
                                'obj.elim': img[480:480 + 56, 1130:1130 + 125],
                                'obj.dmg': img[480:480 + 56, 1333:1333 + 147],
                                'team': 0},
                           'orange 1':
                               {'elim': img[681:681 + 56, 879:879 + 90],
                                'obj.elim': img[681:681 + 56, 1130:1130 + 125],
                                'obj.time': img[681:681 + 56, 1333:1333 + 147],
                                'team': 1},
                           'orange 2':
                               {'elim': img[740:740 + 56, 879:879 + 90],
                                'obj.elim': img[740:740 + 56, 1130:1130 + 125],
                                'obj.time': img[740:740 + 56, 1333:1333 + 147],
                                'team': 1},
                           'orange 3':
                               {'elim': img[800:800 + 56, 879:879 + 90],
                                'obj.elim': img[800:800 + 56, 1130:1130 + 125],
                                'obj.time': img[800:800 + 56, 1333:1333 + 147],
                                'team': 1},
                           'orange 4':
                               {'elim': img[860:860 + 56, 879:879 + 90],
                                'obj.elim': img[860:860 + 56, 1130:1130 + 125],
                                'obj.time': img[860:860 + 56, 1333:1333 + 147],
                                'team': 1}}
    ocrCAPOINT_NUM_DONT_USE = {
        'blue 1': {'elim': img[242:242 + 47, 695:695 + 84],
                   'obj.elim': img[242:242 + 47, 811:811 + 105],
                   'obj.time': img[242:242 + 47, 955:955 + 120],
                   'obj.dmg': img[242:242 + 47, 1097:1097 + 120],
                   'team': 0},
        'blue 2':
            {'elim': img[292:292 + 47, 695:695 + 84],
             'obj.elim': img[292:292 + 47, 811:811 + 105],
             'obj.time': img[292:292 + 47, 955:955 + 120],
             'obj.dmg': img[292:292 + 47, 1097:1097 + 120],
             'team': 0},
        'blue 3':
            {'elim': img[340:340 + 47, 695:695 + 84],
             'obj.elim': img[340:340 + 47, 811:811 + 105],
             'obj.time': img[340:340 + 47, 955:955 + 120],
             'obj.dmg': img[340:340 + 47, 1097:1097 + 120],
             'team': 0},
        'blue 4':
            {'elim': img[388:388 + 47, 695:695 + 84],
             'obj.elim': img[388:388 + 47, 811:811 + 105],
             'obj.time': img[388:388 + 47, 955:955 + 120],
             'obj.dmg': img[388:388 + 47, 1097:1097 + 120],
             'team': 0},
        'orange 1':
            {'elim': img[550:550 + 47, 695:695 + 84],
             'obj.elim': img[550:550 + 47, 811:811 + 105],
             'obj.time': img[550:550 + 47, 955:955 + 120],
             'obj.dmg': img[550:550 + 47, 1097:1097 + 120],
             'team': 1},
        'orange 2':
            {'elim': img[598:598 + 47, 695:695 + 84],
             'obj.elim': img[598:598 + 47, 811:811 + 105],
             'obj.time': img[598:598 + 47, 955:955 + 120],
             'obj.dmg': img[598:598 + 47, 1097:1097 + 120],
             'team': 1},
        'orange 3':
            {'elim': img[645:645 + 47, 695:695 + 84],
             'obj.elim': img[645:645 + 47, 811:811 + 105],
             'obj.time': img[645:645 + 47, 955:955 + 120],
             'obj.dmg': img[645:645 + 47, 1097:1097 + 120],
             'team': 1},
        'orange 4':
            {'elim': img[695:695 + 47, 695:695 + 84],
             'obj.elim': img[695:695 + 47, 811:811 + 105],
             'obj.time': img[695:695 + 47, 955:955 + 120],
             'obj.dmg': img[695:695 + 47, 1097:1097 + 120], 'team': 1}}
    ocrCAPOINT_NUM_16x9 = {
        'blue 1': {'elim': img[300:300 + 56, 869:869 + 77],
                   'obj.elim': img[300:300 + 56, 1040:1040 + 87],
                   'obj.time': img[300:300 + 56, 1191:1191 + 150],
                   'obj.dmg': img[300:300 + 56, 1378:1378 + 120],
                   'team': 0},
        'blue 2':
            {'elim': img[362:362 + 56, 869:869 + 77],
             'obj.elim': img[362:362 + 56, 1040:1040 + 87],
             'obj.time': img[362:362 + 56, 1191:1191 + 150],
             'obj.dmg': img[362:362 + 56, 1378:1378 + 120],
             'team': 0},
        'blue 3':
            {'elim': img[420:420 + 56, 869:869 + 77],
             'obj.elim': img[420:420 + 56, 1040:1040 + 87],
             'obj.time': img[420:420 + 56, 1191:1191 + 150],
             'obj.dmg': img[420:420 + 56, 1378:1378 + 120],
             'team': 0},
        'blue 4':
            {'elim': img[480:480 + 56, 869:869 + 77],
             'obj.elim': img[480:480 + 56, 1040:1040 + 87],
             'obj.time': img[480:480 + 56, 1191:1191 + 150],
             'obj.dmg': img[480:480 + 56, 1378:1378 + 120],
             'team': 0},
        'orange 1':
            {'elim': img[681:681 + 56, 869:869 + 77],
             'obj.elim': img[681:681 + 56, 1040:1040 + 87],
             'obj.time': img[681:681 + 56, 1191:1191 + 150],
             'obj.dmg': img[681:681 + 56, 1378:1378 + 120],
             'team': 1},
        'orange 2':
            {'elim': img[740:740 + 56, 869:869 + 77],
             'obj.elim': img[740:740 + 56, 1040:1040 + 87],
             'obj.time': img[740:740 + 56, 1191:1191 + 150],
             'obj.dmg': img[740:740 + 56, 1378:1378 + 120],
             'team': 1},
        'orange 3':
            {'elim': img[800:800 + 56, 869:869 + 77],
             'obj.elim': img[800:800 + 56, 1040:1040 + 87],
             'obj.time': img[800:800 + 56, 1191:1191 + 150],
             'obj.dmg': img[800:800 + 56, 1378:1378 + 120],
             'team': 1},
        'orange 4':
            {'elim': img[860:860 + 56, 869:869 + 77],
             'obj.elim': img[860:860 + 56, 1040:1040 + 87],
             'obj.time': img[860:860 + 56, 1191:1191 + 150],
             'obj.dmg': img[860:860 + 56, 1378:1378 + 120], 'team': 1}}
    payload_list = ['mpl_combat_gauss', 'mpl_combat_fission']
    capture_point_list = ['mpl_combat_dyson', 'mpl_combat_combustion']
    for team_POS, cords in ocrONLY_NAME_16x9.items():
        name = ocr_process(cords, ocrCONFIG)
        print(name)
        if mapname in payload_list:
            for team_num, stat_pos in ocrPAYLOAD_NUM_16x9.items():
                temp_stat_dump = {}
                if team_POS == team_num:
                    for key, value in stat_pos.items():
                        if key == 'team':
                            temp_stat_dump.update({key: value})
                            continue
                        stat = ocr_process(value, ocrCONFIG_NUM)
                        temp_stat_dump.update({key: stat})
                    scoreboard_STATS.update({name: temp_stat_dump})

        elif mapname in capture_point_list:
            for team_num, stat_pos in ocrCAPOINT_NUM_16x9.items():
                temp_stat_dump = {}
                if team_POS == team_num:
                    for key, value in stat_pos.items():
                        if key == 'team':
                            temp_stat_dump.update({key: value})
                            continue
                        stat = ocr_process(value, ocrCONFIG_NUM)
                        temp_stat_dump.update({key: stat})
                    scoreboard_STATS.update({name: temp_stat_dump})

    for ocnames, stats in scoreboard_STATS.items():
        newname = closeMatches(apiNAMES, ocnames)
        print(ocnames, newname)
        if not newname:
            continue
        tmp_rename.update({newname[0]: stats})


def ocrPERSONALSTATS():
    for file_loc in players:
        tmp_stat = {}
        img = cv2.imread(f'{file_loc}')
        ocrPLAY_STATS_DONT_USE = {'kills': img[818:818 + 54, 30:30 + 180],
                                  'assists': img[818:818 + 54, 210:210 + 180],
                                  'deaths': img[831:831 + 32, 391:391 + 165],
                                  'damage': img[831:831 + 32, 564:564 + 165]}
        ocrPLAY_STATS = {'kills': img[1026:1026 + 40, 58:58 + 204],
                              'assists': img[1026:1026 + 40, 274:274 + 204],
                              'deaths': img[1026:1026 + 40, 490:490 + 204],
                              'damage': img[1026:1026 + 40, 706:706 + 204]}
        ocrPLAY_STATS_NAME_DONT_USE = {'name': img[775:775 + 33, 175:175 + 205]}
        ocrPLAY_STATS_NAME = {'name': img[960:960 + 37, 219:219 + 249]}
        for stat_name, img_value in ocrPLAY_STATS_NAME.items():
            name = ocr_process(img_value, ocrCONFIG)
            for pl_stats, img_val in ocrPLAY_STATS.items():
                ocr_stat = ocr_process(img_val, ocrCONFIG_NUM)
                tmp_stat.update({pl_stats: ocr_stat})
            playstats_combine.update({name: tmp_stat})
    for ocrnames, stats in playstats_combine.items():
        newname = closeMatches(apiNAMES, ocrnames)
        print(ocrnames, newname)
        if not newname:
            continue
        tmp_renam2.update({newname[0]: stats})


def create_folders(match_id, map_name):
    folder_dir = {'mpl_combat_gauss': 'gauss', 'mpl_combat_fission': 'fission',
                  'mpl_combat_dyson': 'dyson', 'mpl_combat_combustion': 'combustion', 'mpl_arena_a': 'arena'}
    for mapN, map_dir in folder_dir.items():
        if mapN == map_name:
            if Path(f"{map_dir}/{match_id}").exists():
                return True
            Path(f"{map_dir}/{match_id}").mkdir(parents=True, exist_ok=True)


def api_names():
    for teamIndex in range(0, len(apiData["teams"])):
        if "players" in apiData["teams"][teamIndex]:
            teamPlayers = apiData["teams"][teamIndex]["players"]
            for teamPlayer in range(0, len(teamPlayers)):
                if "players" in apiData["teams"][teamIndex] != apiData["teams"][2]:
                    name = teamPlayers[teamPlayer]['name']
                    apiNAMES.append(name)



def ocr_example():
    user_folder_input = input('Enter folder directory of data to begin ocr process:')
    file_list = []
    payload_list = ['mpl_combat_gauss', 'mpl_combat_fission']
    capture_point_list = ['mpl_combat_dyson', 'mpl_combat_combustion']
    global apiData
    apiData = None
    for file in os.listdir(user_folder_input):
        if file.endswith('.json'):
            with open(f'{user_folder_input}/{file}', 'r') as f:
                apiData = json.load(f)
                continue
        if file.endswith('.png'):
            file_list.append(f'{user_folder_input}/{file}')

    mapNAME = apiData['map_name']
    re_scoreboard = re.compile('scoreboard_')
    re_players = re.compile('player.')
    scoreboard = list(filter(re_scoreboard.search, file_list))
    global players
    players = list(filter(re_players.findall, file_list))

    api_names()
    ocrSCOREBOARD(mapNAME, scoreboard[0])
    ocrPERSONALSTATS()
    for key in tmp_renam2:
        if key in tmp_rename:
            tmp_renam2[key].update(tmp_rename[key])
    if mapNAME in payload_list:
        createstats_payload(mapNAME)
    elif mapNAME in capture_point_list:
        createstats_capture_point(mapNAME)
    print(playstats_combine)


ocr_example()


