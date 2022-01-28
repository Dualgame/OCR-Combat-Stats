import numpy as np
import aiohttp
import asyncio
import simpleobsws
import time
from PIL import Image
import pytesseract
import json
import cv2
from pytesseract import Output


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


global newstatDICT
newstatDICT = {}
async def war_room():
    fix = {}
    async with aiohttp.ClientSession() as session:
        apiData = await fetch_api(session, "http://127.0.0.1:6721/session")
        if apiData is None:
            return False
        for teamIndex in range(0, len(apiData["teams"])):
            if "players" in apiData["teams"][teamIndex]:
                teamPlayers = apiData["teams"][teamIndex]["players"]
                for teamPlayer in range(0, len(teamPlayers)):
                    if "players" in apiData["teams"][teamIndex] != apiData["teams"][2]:
                        x = teamPlayers[teamPlayer]["head"]["position"][0]
                        y = teamPlayers[teamPlayer]["head"]["position"][1]
                        z = teamPlayers[teamPlayer]["head"]["position"][2]
                        name = teamPlayers[teamPlayer]['name']
                        userid = teamPlayers[teamPlayer]['userid']
                        team = teamIndex
                        arraypos = teamPlayer
                        warROOM = 176.90 <= x <= 199.10 and -16.70 <= y <= -7.85 and 16.70 <= z <= 46.70
                        update = {userid: warROOM}
                        fix.update(update)
                        if team == 0:
                            if arraypos == 0:
                                numbers = 6
                                update = {name: {'userid': userid, 'num': numbers, 'team': team}}
                                newstatDICT.update(update)
                            elif arraypos == 1:
                                numbers = 7
                                update = {name: {'userid': userid, 'num': numbers, 'team': team}}
                                newstatDICT.update(update)
                            elif arraypos == 2:
                                numbers = 8
                                update = {name: {'userid': userid, 'num': numbers, 'team': team}}
                                newstatDICT.update(update)
                            elif arraypos == 3:
                                numbers = 9
                                update = {name: {'userid': userid, 'num': numbers, 'team': team}}
                                newstatDICT.update(update)
                        elif team == 1:
                            if arraypos == 0:
                                numbers = 1
                                update = {name: {'userid': userid, 'num': numbers, 'team': team}}
                                newstatDICT.update(update)
                            elif arraypos == 1:
                                numbers = 2
                                update = {name: {'userid': userid, 'num': numbers, 'team': team}}
                                newstatDICT.update(update)
                            elif arraypos == 2:
                                numbers = 3
                                update = {name: {'userid': userid, 'num': numbers, 'team': team}}
                                newstatDICT.update(update)
                            elif arraypos == 3:
                                numbers = 4
                                update = {name: {'userid': userid, 'num': numbers, 'team': team}}
                                newstatDICT.update(update)
        if all(value == 1 for value in fix.values()):
            return True
        else:
            return False


async def camera_control():
    matchID = None
    screenTAKEN = False
    playerSTAT = {}
    ocrCONFIG = '--psm 6, -c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.:-_'
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
                                    print('map names ', mapNAME, mapDATA)
                                    await posting_api(session, "http://127.0.0.1:6721/camera_transform", DATA)
                                    data = {'enabled': False}
                                    await posting_api(session, "http://127.0.0.1:6721/ui_visibility", json.dumps(data))
                                    ws = simpleobsws.obsws(host='127.0.0.1', port=4450)
                                    await ws.connect()
                                    timeSCSHOT = time.time()
                                    nameSCSHOT = f'{matchID}-{timeSCSHOT}'
                                    await ws.call('TakeSourceScreenshot',
                                                  {"sourceName": "Game Capture", "embedPictureFormat": "png",
                                                   'saveToFilePath': f'C:/Users/dualg/Documents/echo-py/{nameSCSHOT}.png'})
                                    data = {'enabled': True}
                                    await posting_api(session, "http://127.0.0.1:6721/ui_visibility", json.dumps(data))
                                    for name, info in newstatDICT.items():
                                        for k, v in info.items():
                                            if k == 'num':
                                                print(v)
                                                player_timeSCSHOT = time.time()
                                                player_nameSCSHOT = f'{matchID}-{player_timeSCSHOT}'
                                                update = {name: {'img': player_nameSCSHOT}}
                                                playerSTAT.update(update)
                                                data = {'mode': 'pov', 'num': v}
                                                await posting_api(session, "http://127.0.0.1:6721/camera_mode",
                                                                  json.dumps(data))
                                                await asyncio.sleep(.2)
                                                await ws.call('TakeSourceScreenshot',
                                                              {"sourceName": "Game Capture",
                                                               "embedPictureFormat": "png",
                                                               'saveToFilePath': f'C:/Users/dualg/Documents/echo-py/{player_nameSCSHOT}.png'})
                                    img = cv2.imread(f'{nameSCSHOT}.png')
                                    ocrDICT = {'blue': img[240:240 + 240, 278:278 + 960],
                                               'orange': img[548:548 + 240, 278:278 + 960]}
                                    for colour in ocrDICT.values():
                                        scale_percent = 300
                                        width = int(colour.shape[1] * scale_percent / 100)
                                        height = int(colour.shape[0] * scale_percent / 100)
                                        dim = (width, height)
                                        resized = cv2.resize(colour, dim, interpolation=cv2.INTER_AREA)
                                        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                                        text = pytesseract.image_to_string(gray, lang="eng",
                                                                           config=ocrCONFIG)
                                        print(text)
                                    for nam, namdata in playerSTAT.items():
                                        for kv, sv in namdata.items():
                                            scale_percent = 400
                                            img = cv2.imread(f'{sv}.png')
                                            player_stats = img[778:778 + 90, 30:30 + 700]
                                            width = int(player_stats.shape[1] * scale_percent / 100)
                                            height = int(player_stats.shape[0] * scale_percent / 100)
                                            dim = (width, height)
                                            resized = cv2.resize(player_stats, dim, interpolation=cv2.INTER_AREA)
                                            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                                            text = pytesseract.image_to_string(gray, lang="eng",
                                                                               config=ocrCONFIG)
                                            print(text)

                                    await ws.disconnect()
                                    screenTAKEN = True
                                    break
                                else:
                                    print(f'not this map {mapNAME}')

                else:
                    matchID = apiData["sessionid"]
                    screenTAKEN = False
                    newstatDICT.clear()
                    playerSTAT.clear()
                    await asyncio.sleep(5)

            except KeyError:
                pass
            except ValueError:
                pass



async def moon():
    ka = loop.create_task(camera_control())
    await asyncio.wait([ka])
loop = asyncio.get_event_loop()
loop.run_until_complete(moon())
