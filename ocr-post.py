import numpy as np
import aiohttp
import asyncio
import simpleobsws
import time
from PIL import Image
import pytesseract
import json


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


async def war_room():
    warROOM = None
    async with aiohttp.ClientSession() as session:
        apiData = await fetch_api(session, "http://127.0.0.1:6721/session")
        if apiData is None:
            return False
        for teamIndex in range(0, len(apiData["teams"])):
            if "players" in apiData["teams"][teamIndex]:
                teamPlayers = apiData["teams"][teamIndex]["players"]
                for teamPlayer in teamPlayers:
                    if "players" in apiData["teams"][teamIndex] != apiData["teams"][2]:
                        x = teamPlayer["head"]["position"][0]
                        y = teamPlayer["head"]["position"][1]
                        z = teamPlayer["head"]["position"][2]
                        warROOM = 176.90 <= x <= 199.10 and -16.70 <= y <= -7.85 and 16.70 <= z <= 46.70
        return warROOM



async def camera_control():
    matchID = None
    screenTAKEN = False
    mapDATA = {'mpl_combat_gauss': '{\"px\" : 187.98, \"py\" : -11.09, \"pz\" : 44.0900004,\"fovy\" : 1.6}',
               'mpl_combat_fission': '{\"px\" : 187.97, \"py\" : -10.75, \"pz\" : 44.0900004,\"fovy\" : 1.6}',
               'mpl_combat_dyson': '{\"px\" : 187.95, \"py\" : -11.186001, \"pz\" : 44.0900004,\"fovy\" : 1.6}',
               'mpl_combat_combustion': '{\"px\" : 187.968, \"py\" : -11.696, \"pz\" : 44.0900004,\"fovy\" : 1.6}'}
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
                                    screenSHOT = await ws.call('TakeSourceScreenshot',
                                                               {"sourceName": "Game Capture", "embedPictureFormat": "png",
                                                                'saveToFilePath': f'C:/Users/dualg/Documents/echo-py/{nameSCSHOT}.png'})

                                    #pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                                    #filename = f'{nameSCSHOT}.png'
                                    #image = np.array(Image.open(filename))
                                    #text = pytesseract.image_to_string(image)
                                    #print(text)
                                    await ws.disconnect()
                                    screenTAKEN = True
                                else:
                                    print(f'not this map {mapNAME}')

                else:
                    matchID = apiData["sessionid"]
                    screenTAKEN = False

            except KeyError:
                pass
            except ValueError:
                pass



async def moon():
    ka = loop.create_task(camera_control())
    await asyncio.wait([ka])
loop = asyncio.get_event_loop()
loop.run_until_complete(moon())