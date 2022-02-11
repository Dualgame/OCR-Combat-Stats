import PIL.Image
import aiohttp
import asyncio
import simpleobsws
from pathlib import Path
import time
import pytesseract
import json
import cv2
from difflib import get_close_matches

# Character name & number whitelist for OCR
ocrCONFIG = '--psm 6, -c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.:-_'
ocrCONFIG_NUM = '--psm 6, -c tessedit_char_whitelist=01234567890:'

# General dictionaries for ocr results that get merged
newstatDICT = {}
scoreboard_STATS = {}
playerSTAT = {}
playstats_combine = {}
tmp_rename = {}
tmp_renam2 = {}
# This stores all names from the api that we use for a diff against ocr results in closeMatches
apiNAMES = []


async def posting_api(session, url, data):
    try:
        async with session.post(url, data=data):
            pass
    except aiohttp.ClientConnectorError as e:
        print('Connection Error', str(e))
    except aiohttp.client_exceptions.ServerDisconnectedError as e:
        print('Server disconnected', str(e))
    except aiohttp.client_exceptions.ClientOSError as e:
        print('Client ', str(e))


async def fetch_api(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200 or response.status == 500:
                api = await response.json()
                return api
            else:
                print(response.status)
                await asyncio.sleep(5)
    except aiohttp.ClientConnectorError as e:
        print('Connection Error ', str(e))
        await asyncio.sleep(5)
    except aiohttp.client_exceptions.ServerDisconnectedError as e:
        print('Server disconnected ', str(e))
    except aiohttp.client_exceptions.ClientOSError as e:
        print('Client ', str(e))


def ocr_process(img_CORDS, ocrCONFIG):
    """
    This is the main ocr process that begins by resizing, converting to gray and finally inverting the image.

    :param img_CORDS: exact area to crop in on image
    :param ocrCONFIG: the whitelist we set from the start, otherwise any specific Tesseract options can be passed here
    :return: returns ocr result as string without \n
    """
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


def ocr_process_playerSTATS(img_CORDS, ocrCONFIG):
    scale_percent = 300
    width = int(img_CORDS.shape[1] * scale_percent / 100)
    height = int(img_CORDS.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img_CORDS, dim, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    (thresh, black_white) = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    invert = cv2.bitwise_not(gray)
    text = pytesseract.image_to_string(invert, lang="eng",
                                       config=ocrCONFIG)
    replace_string = text.replace('\n', "")
    return replace_string


def closeMatches(names, ocrRESULT):
    """
    This is to quickly diff and get a correct name from the ocr results
    :param names: Using the apiNAME list as correct names to diff against ocr results
    :param ocrRESULT: Single ocr string to compare against
    :return: returns compared name from names list vs ocrRESULT
    """
    match = get_close_matches(ocrRESULT, names)
    return match


def scoreboard_html(current_map):
    """
    Creates template for scoreboard based on if its a payload or capture point
    :param current_map: specify current map
    """
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
    """
    Once the base scoreboard has been generated it goes through and fills in name and stats for all players based on
    team value 0 for blue and 1 for orange
    :param mapname: specify current map
    """
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
    """
    Once the base scoreboard has been generated it goes through and fills in name and stats for all players based on
    team value 0 for blue and 1 for orange
    :param mapname: specify current map
    """
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
    """
    Loops through all the dictionaries values to be sent to ocr_process and return into temp dict that will later be
    combined with individual player stats.
    The main ocr Dictionaries at the start are all hard coded regions based on a 1920x1080 image of the scoreboard.
    Final temp dictionary should result in Name for key and nested dictionary with all stats from the scoreboard.
    Last step is to update all names against apiNAME list with closeMatches.

    :param mapname: specify current map
    :param IMG: image filename to be used
    """
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
        if not newname:
            continue
        tmp_rename.update({newname[0]: stats})


def ocrPERSONALSTATS():
    """
    Similar to ocrSCOREBOARD this loops through to generate the ocr player stats. Main difference being we dont pass
    img as its already stored in the dictionary we iterate through to pull out the image location.
    Final temp dictionary should result in Name for key and nested dictionary with all stats.
    """
    for nam, namdata in playerSTAT.items():
        for kv, sv in namdata.items():
            tmp_stat = {}
            img = cv2.imread(f'{sv}.png')
            ocrPLAY_STATS_DONT_USE = {'kills': img[818:818 + 54, 30:30 + 180],
                                      'assists': img[818:818 + 54, 210:210 + 180],
                                      'deaths': img[831:831 + 32, 391:391 + 165],
                                      'damage': img[831:831 + 32, 564:564 + 165]}
            ocrPLAY_STATS_16x9 = {'kills': img[1026:1026 + 40, 58:58 + 204],
                                  'assists': img[1026:1026 + 40, 274:274 + 204],
                                  'deaths': img[1026:1026 + 40, 490:490 + 204],
                                  'damage': img[1026:1026 + 40, 706:706 + 204]}
            ocrPLAY_STATS_NAME_DONT_USE = {'name': img[775:775 + 33, 175:175 + 205]}
            ocrPLAY_STATS_NAME_16x9 = {'name': img[960:960 + 37, 219:219 + 249]}
            for stat_name, img_value in ocrPLAY_STATS_NAME_16x9.items():
                name = ocr_process_playerSTATS(img_value, ocrCONFIG)
                for pl_stats, img_val in ocrPLAY_STATS_16x9.items():
                    ocr_stat = ocr_process_playerSTATS(img_val, ocrCONFIG_NUM)
                    tmp_stat.update({pl_stats: ocr_stat})
                playstats_combine.update({name: tmp_stat})
    for ocrnames, stats in playstats_combine.items():
        newname = closeMatches(apiNAMES, ocrnames)
        if not newname:
            continue
        tmp_renam2.update({newname[0]: stats})


def create_folders(match_id, map_name):
    """
    WIP
    Currently changed my saving process into sub folders of the map names vs having all images saved in current working
    directory of the script
    """
    folder_dir = {'mpl_combat_gauss': 'gauss', 'mpl_combat_fission': 'fission',
                  'mpl_combat_dyson': 'dyson', 'mpl_combat_combustion': 'combustion', 'mpl_arena_a': 'arena'}
    for mapN, map_dir in folder_dir.items():
        if mapN == map_name:
            if Path(f"{map_dir}/{match_id}").exists():
                return True
            Path(f"{map_dir}/{match_id}").mkdir(parents=True, exist_ok=True)


def image_size(img):
    image = PIL.Image.OPEN(f'{img}.png')
    width, height = image.size
    if width == 1920 and height == 1080:
        return True
    else:
        return False


def image_blank(img):
    image = cv2.imread(f'{img}.png')
    if cv2.countNonZero(image) == 0:
        return True
    else:
        return False


async def war_room():
    """
    Main function is to return if ALL players have spawned into the celebration room to indicate game is over.
    Also serves the purpose of generating apiName list with correct names and filling in a dictionary that has all
    values related to changing camera to individual players for screen capture.
    :return: Loop through to see if all players in dictionary are true
    """
    fix = {}
    async with aiohttp.ClientSession() as session:
        apiData = await fetch_api(session, "http://127.0.0.1:6721/session")
        if apiData is None:
            return False
        newstatDICT.clear()
        apiNAMES.clear()
        for teamIndex in range(0, len(apiData["teams"])):
            if "players" in apiData["teams"][teamIndex]:
                teamPlayers = apiData["teams"][teamIndex]["players"]
                for teamPlayer in range(0, len(teamPlayers)):
                    if "players" in apiData["teams"][teamIndex] != apiData["teams"][2]:
                        x = teamPlayers[teamPlayer]["head"]["position"][0]
                        y = teamPlayers[teamPlayer]["head"]["position"][1]
                        z = teamPlayers[teamPlayer]["head"]["position"][2]
                        name = teamPlayers[teamPlayer]['name']
                        apiNAMES.append(name)
                        userid = teamPlayers[teamPlayer]['userid']
                        #check if player is in celebration room
                        warROOM = 176.90 <= x <= 199.10 and -16.70 <= y <= -7.85 and 16.70 <= z <= 46.70
                        fix.update({userid: warROOM})
                        #player number used to write camera position
                        if teamIndex == 0:
                            if teamPlayer == 0:
                                newstatDICT.update({name: {'userid': userid, 'num': 6, 'team': teamIndex}})
                            elif teamPlayer == 1:
                                newstatDICT.update({name: {'userid': userid, 'num': 7, 'team': teamIndex}})
                            elif teamPlayer == 2:
                                newstatDICT.update({name: {'userid': userid, 'num': 8, 'team': teamIndex}})
                            elif teamPlayer == 3:
                                newstatDICT.update({name: {'userid': userid, 'num': 9, 'team': teamIndex}})
                        elif teamIndex == 1:
                            if teamPlayer == 0:
                                newstatDICT.update({name: {'userid': userid, 'num': 1, 'team': teamIndex}})
                            elif teamPlayer == 1:
                                newstatDICT.update({name: {'userid': userid, 'num': 2, 'team': teamIndex}})
                            elif teamPlayer == 2:
                                newstatDICT.update({name: {'userid': userid, 'num': 3, 'team': teamIndex}})
                            elif teamPlayer == 3:
                                newstatDICT.update({name: {'userid': userid, 'num': 4, 'team': teamIndex}})
        if all(value == 1 for value in fix.values()):
            return True
        else:
            return False


async def camera_control():
    """
    Start by checking if any api is None and if so wait and try against in a few seconds. Next step is to check if the
    current match is the same by comparing session_id and if not storing the new current value. Begin the process of
    calling war_room and checking if all players have entered celebration room and will begin process of taking photos
    and generating ocr data to be stored in dictionary and used for generating the scoreboard.

    mapDATA is all the predefined spots we place the camera ingame for taking pictures of the scoreboard
    """
    matchID = None
    screenTAKEN = False
    payload_list = ['mpl_combat_gauss', 'mpl_combat_fission']
    capture_point_list = ['mpl_combat_dyson', 'mpl_combat_combustion']

    mapDATA = {'mpl_combat_gauss': '{\"px\" : 187.951, \"py\" : -11.085, \"pz\" : 44.0900004,\"fovy\" : 1.6}',
               'mpl_combat_fission': '{\"px\" : 187.97, \"py\" : -10.73, \"pz\" : 44.0900004,\"fovy\" : 1.6}',
               'mpl_combat_dyson': '{\"px\" : 187.968, \"py\" : -11.186001, \"pz\" : 44.0900004,\"fovy\" : 1.6}',
               'mpl_combat_combustion': '{\"px\" : 187.968, \"py\" : -11.45, \"pz\" : 44.0900004,\"fovy\" : 1.6}'}
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                apiData = await fetch_api(session, "http://127.0.0.1:6721/session")
                if apiData is None:
                    await asyncio.sleep(2)
                    continue
                if matchID == apiData["sessionid"]:
                    if screenTAKEN:
                        await asyncio.sleep(5)
                        print('screen shot already taken')
                        continue
                    else:
                        if await war_room():
                            for mapNAME, DATA in mapDATA.items():
                                if mapNAME == apiData['map_name']:
                                    """
                                    Turn the hud off and sets camera to scoreboard location.
                                    Start saving pictures of scoreboard and looping through player cameras.
                                    Save location currently is based on sub folders of dyson, combustion, gauss, fission
                                    """
                                    screenTAKEN = True
                                    folderlocation = f'{mapNAME}/{matchID}'
                                    create_folders(matchID, mapNAME)
                                    await posting_api(session, "http://127.0.0.1:6721/camera_transform", DATA)
                                    data = {'enabled': False}
                                    await posting_api(session, "http://127.0.0.1:6721/ui_visibility", json.dumps(data))
                                    ws = simpleobsws.obsws(host='127.0.0.1', port=4450)
                                    await ws.connect()
                                    timeSCSHOT = time.time()
                                    nameSCSHOT = f'{matchID}-{timeSCSHOT}'
                                    await ws.call('TakeSourceScreenshot',
                                                  {"sourceName": "Game Capture", "embedPictureFormat": "png",
                                                   'saveToFilePath': f'{folderlocation}/{nameSCSHOT}.png'})
                                    data = {'enabled': True}
                                    await posting_api(session, "http://127.0.0.1:6721/ui_visibility", json.dumps(data))
                                    for name, info in newstatDICT.items():
                                        for k, v in info.items():
                                            if k == 'num':
                                                player_timeSCSHOT = time.time()
                                                player_nameSCSHOT = f'{folderlocation}/{matchID}-{player_timeSCSHOT}'
                                                playerSTAT.update({name: {'img': player_nameSCSHOT}})
                                                data = {'mode': 'pov', 'num': v}
                                                await posting_api(session, "http://127.0.0.1:6721/camera_mode",
                                                                  json.dumps(data))
                                                await asyncio.sleep(.05)
                                                await ws.call('TakeSourceScreenshot',
                                                              {"sourceName": "Game Capture",
                                                               "embedPictureFormat": "png",
                                                               'saveToFilePath':
                                                                   f'{player_nameSCSHOT}.png'})
                                    await ws.disconnect()
                                    """
                                    Begin the ocr process and creating and combining dictionaries. 
                                    """
                                    image = f'{folderlocation}/{nameSCSHOT}.png'
                                    ocrSCOREBOARD(mapNAME, image)
                                    ocrPERSONALSTATS()
                                    for key in scoreboard_STATS:
                                        if key in playstats_combine:
                                            scoreboard_STATS[key].update(playstats_combine[key])

                                    for key in tmp_renam2:
                                        if key in tmp_rename:
                                            tmp_renam2[key].update(tmp_rename[key])
                                    if mapNAME in payload_list:
                                        createstats_payload(mapNAME)
                                    elif mapNAME in capture_point_list:
                                        createstats_capture_point(mapNAME)
                                    break
                                else:
                                    print(f'not this map {mapNAME}')
                else:
                    """
                    Clear all dictionaries and set session_id 
                    wait before continuing loop as people spawn by default into it once the match starts and will
                    auto start the sequence of taking photos even though game has not ended
                    """
                    matchID = apiData["sessionid"]
                    screenTAKEN = False
                    newstatDICT.clear()
                    playerSTAT.clear()
                    playstats_combine.clear()
                    scoreboard_STATS.clear()
                    apiNAMES.clear()
                    tmp_rename.clear()
                    tmp_renam2.clear()
                    await asyncio.sleep(10)

            except KeyError:
                pass
            except ValueError:
                pass


async def moon():
    ka = loop.create_task(camera_control())
    await asyncio.wait([ka])


loop = asyncio.get_event_loop()
loop.run_until_complete(moon())
