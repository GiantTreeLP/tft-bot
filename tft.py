# Detergent's TFT Bot
# Branch: main
from typing import Union

import cv2
import numpy as np
import pkg_resources
import requests
import base64
import os
import pyautogui as auto
from pygetwindow import Win32Window
import time
from printy import printy
import urllib3
import pydirectinput
import win32con
import win32gui
import win32ui

pkg_resources.require("PyAutoGUI~=0.9.50")
pkg_resources.require("opencv-python~=4.5.1.48")


urllib3.disable_warnings()
# If you haven't installed your game in default path (Windows) set your path here
PATH = r"G:\Games\Riot Games\League of Legends\lockfile"
auto.FAILSAFE = False
pydirectinput.FAILSAFE = False


class Extra:

    @staticmethod
    def base64encode(text: str):
        text = base64.b64encode(text.encode("ascii")).decode("ascii")
        return text


class LCU:
    @staticmethod
    def connect(lockfile_path="default"):
        if lockfile_path == "default":
            lockfile_path = "C:\\Riot Games\\League of Legends\\lockfile"
        if LCU.check_exist(lockfile_path):
            return LCU.read_file(lockfile_path)
        else:
            raise Exception("Couldn't read lockfile!\nThis could mean that either the \
path is not the right or the League Client is not opened!")

    @staticmethod
    def check_exist(lockfile_path):
        return os.path.exists(lockfile_path)

    @staticmethod
    def read_file(lockfile_path):
        lockfile = open(lockfile_path, "r")
        data = lockfile.read().split(":")
        data_dict = {
            "port": data[2],
            "url": "https://127.0.0.1:{}".format(data[2]),
            "auth": "riot:{}".format(data[3]),
            "connection_method": data[4]
        }
        return data_dict

    @staticmethod
    def start_search(lcu_data):
        headers = LCU.get_lcu_headers(lcu_data)
        url = lcu_data["url"] + "/lol-lobby/v2/lobby/matchmaking/search"
        request = requests.post(url, headers=headers, verify=False)
        return request.status_code

    @staticmethod
    def play_again(lcu_data):
        headers = LCU.get_lcu_headers(lcu_data)
        url = lcu_data["url"] + "/lol-lobby/v2/play-again"
        request = requests.post(url, headers=headers, verify=False)
        return request.status_code

    @staticmethod
    def create_game_lobby_tft(lcu_data, gm: str = "Normal"):
        if gm.upper() not in ("NORMAL", "RANKED"):
            raise ValueError(
                "Defined gamemode is invalid!\nValid gamemodes are Normal and Ranked.")
        else:
            if gm.upper() == "NORMAL":
                q_id = 1090
            if gm.upper() == "RANKED":
                q_id = 1100
        headers = LCU.get_lcu_headers(lcu_data)
        data = '{{"queueId":{}}}'.format(q_id)
        url = lcu_data["url"] + "/lol-lobby/v2/lobby/"
        request = requests.post(url, headers=headers, data=data, verify=False)
        return request.status_code

    @staticmethod
    def create_tutorial_lobby_tft(lcu_data):
        headers = LCU.get_lcu_headers(lcu_data)
        data = '{"queueId":1110}'
        url = lcu_data["url"] + "/lol-lobby/v2/lobby/"
        request = requests.post(url, headers=headers, data=data, verify=False)
        return request.json()

    @staticmethod
    def get_lcu_headers(lcu_data):
        auth = Extra.base64encode(lcu_data["auth"])
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": F"Basic {auth}"
        }
        return headers

    @staticmethod
    def get_current_summoner_in_queue(lcu_data, rc=False):
        auth: str = Extra.base64encode(lcu_data["auth"])
        headers = {
            "Accept": "application/json",
            "Authorization": F"Basic {auth}"
        }
        url = lcu_data["url"] + "/lol-matchmaking/v1/ready-check"
        request = requests.get(url, headers=headers, verify=False)
        request_json = request.json()
        if "state" in request_json:
            if request_json["state"] == "Invalid":
                return True
            elif request_json["state"] == "InProgress":
                if rc:
                    return 2
                return True
        elif request_json["httpStatus"] == 404:
            return False

    @staticmethod
    def get_current_summoner_ready_check(lcu_data, rc=False):
        is_in_q = LCU.get_current_summoner_in_queue(lcu_data, True)
        if is_in_q == 2:
            return True
        if is_in_q == True and is_in_q != 2 and rc == True:
            return 2
        return False

    @staticmethod
    def auto_accept_current_ready_check(lcu_data):
        ready_check = LCU.get_current_summoner_ready_check(lcu_data, True)
        if ready_check:
            headers = LCU.get_lcu_headers(lcu_data)
            url = lcu_data["url"] + "/lol-matchmaking/v1/ready-check/accept"
            requests.post(url, headers=headers, verify=False)
            return "Accepted!"
        elif ready_check == 2:
            return "Waiting for ready check..."
        else:
            return "Not in queue!"


# Start utility methods
class Wrappers:

    IMAGE_CACHE = dict()

    @staticmethod
    def search(image: Union[str, np.ndarray], precision: float = 0.8):
        # Optimization
        if isinstance(image, str):
            if not (image in Wrappers.IMAGE_CACHE):
                im = cv2.imread(image, 0)
                if im is None:
                    raise
                Wrappers.IMAGE_CACHE[image] = im
            return Wrappers.search(Wrappers.IMAGE_CACHE[image], precision)
        elif isinstance(image, np.ndarray):
            window = Wrappers.get_tft_window()
            im = Wrappers.screenshot(window)
            # im = auto.screenshot(region=wrappers.get_tft_window().box)
            # if is_retina:
            #     im.thumbnail(
            #         (round(im.size[0] * 0.5), round(im.size[1] * 0.5)))
            # im = cv2.cvtColor(np.array(im), cv2.COLOR_BGR2GRAY)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(im, image, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val < precision:
                return [-1, -1]
            cv2.circle(im, max_loc, 16, (0, 0, 255, 255), 4)
            cv2.namedWindow("test")
            cv2.imshow("test", im)
            cv2.waitKey(1)
            return np.add(max_loc, window.topleft)

    @staticmethod
    def get_tft_window() -> Win32Window:
        return auto.getWindowsWithTitle("League of Legends")[0]

    @staticmethod
    def screenshot(window: Win32Window) -> np.ndarray:
        left, top, width, height = window.box
        hDC = win32gui.GetWindowDC(window._hWnd)

        myDC = win32ui.CreateDCFromHandle(hDC)
        newDC = myDC.CreateCompatibleDC()

        myBitMap = win32ui.CreateBitmap()
        myBitMap.CreateCompatibleBitmap(myDC, width, height)

        newDC.SelectObject(myBitMap)

        newDC.BitBlt((0, 0), (width, height), myDC, (0, 0), win32con.SRCCOPY)
        myBitMap.Paint(newDC)

        array = np.fromstring(myBitMap.GetBitmapBits(True), dtype='uint8')
        array.shape = (height, width, -1)

        win32gui.DeleteObject(myBitMap.GetHandle())
        newDC.DeleteDC()
        myDC.DeleteDC()
        win32gui.ReleaseDC(hDC, window._hWnd)

        return array

    @staticmethod
    def onscreen(path, precision=0.8):
        return Wrappers.search(path, precision)[0] != -1

    @staticmethod
    def search_to(path):
        pos = Wrappers.search(path)
        # if wrappers.onscreen(path):
        if pos[0] != -1:
            auto.moveTo(pos)
            return pos

    @staticmethod
    def click_key(key, delay=.1):
        Wrappers.get_tft_window().activate()
        auto.press(key)

    @staticmethod
    def click_left(delay=.1):
        Wrappers.get_tft_window().activate()
        auto.leftClick()

    @staticmethod
    def click_right(delay=.1):
        Wrappers.get_tft_window().activate()
        auto.rightClick()

    @staticmethod
    def click_to(path, delay=.1):
        pos = Wrappers.search(path)
        # if wrappers.onscreen(path):
        if pos[0] != -1:
            # auto.moveTo(pos)
            Wrappers.get_tft_window().activate()
            auto.leftClick(pos)
            # wrappers.click_left(delay)

    @staticmethod
    def click_to_r(path, delay=.1):
        pos = Wrappers.search(path)
        # if wrappers.onscreen(path):
        if pos[0] != -1:
            # auto.moveTo(pos)
            Wrappers.get_tft_window().activate()
            auto.rightClick(pos)
            # wrappers.click_right(delay)
        # print(path + " clicked")

# End utility methods


# Start main process
class Main:

    def __init__(self):
        self.combo = 1

    def queue(self):
        lcu_data = LCU.connect(PATH)
        print("Creating tft lobby...")
        LCU.create_game_lobby_tft(lcu_data)
        LCU.start_search(lcu_data)
        while True:
            response = LCU.auto_accept_current_ready_check(lcu_data)
            if response == "Accepted!":
                time.sleep(5)
                response = LCU.auto_accept_current_ready_check(lcu_data)
                if response == "Not in queue!":
                    break
            elif response == "Not in queue!":
                break
            time.sleep(2)
        self.loading()

    def loading(self):
        while not Wrappers.onscreen("./captures/1-1.png"):
            time.sleep(1)
        print("Match starting!")
        self.start()

    def start(self):
        while Wrappers.onscreen("./captures/1-1.png"):
            auto.moveTo(888, 376)
            Wrappers.click_right()
        print("In the match now!")
        self.main()

    def buy(self, iterations: int):
        wanted_champs = self.get_combo(1)
        for i in range(iterations):
            for x in wanted_champs:
                Wrappers.click_to("./captures/champions/{}.png".format(x.lower()))

    def get_combo(self, set: str = 1):
        wanted_champs = []
        set = "Set{}".format(int(set))
        for x in list(champs_req["data"]):
            try:
                if combo_json[set]["Champions"][x]:
                    wanted_champs.append(x)
            except KeyError:
                pass
        # print("Strategy: {}".format(wanted_champs))
        return wanted_champs

    def main(self):
        while not Wrappers.onscreen("./captures/2-4.png"):
            self.orbs(1)
            self.buy(1)
            time.sleep(1)
        print("2-4 reached")
        while Wrappers.onscreen("./captures/2-4.png"):
            auto.moveTo(928, 396)
            Wrappers.click_right()
            time.sleep(0.25)
        time.sleep(5)

        if Wrappers.onscreen("./captures/2-5.png"):
            print("2-5 reached")
            while not Wrappers.onscreen("./captures/3-2.png"): # change this if you want to surrender at a different stage
                self.orbs(1)
                self.buy(1)
                pydirectinput.press('d')
                time.sleep(1)
        if Wrappers.onscreen("./captures/3-2.png"): # (and this)
            print("Surrendering now!")
            self.surrender()

    def orbs(self, iterations: int = 1):
        for i in range(iterations):
            Wrappers.click_to_r("./captures/orb_white.png")
            Wrappers.click_to_r("./captures/orb_blue.png")
            Wrappers.click_to_r("./captures/orb_red.png")
            # wrappers.click_to("./captures/orb_fortune.png")

    def surrender(self):
        while not Wrappers.onscreen("./captures/surrender 2.png"):
            pydirectinput.press('enter')
            auto.write("/ff")
            pydirectinput.press('enter')
        time.sleep(1)
        Wrappers.click_to("./captures/surrender 2.png")
        time.sleep(15)

        while Wrappers.onscreen("./captures/missions ok.png"):
            Wrappers.click_to("./captures/missions ok.png")
            time.sleep(5)
        while Wrappers.onscreen("./captures/skip waiting for stats.png"):
            Wrappers.click_to("./captures/skip waiting for stats.png")
        time.sleep(5)
        lcu_data = LCU.connect(PATH)
        LCU.play_again(lcu_data)
        time.sleep(10)
        print("Queuing up again!")

# End main process

if __name__ == '__main__':
    print("Downloading resources...")

    # Load resources once at the start
    version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
    champs_req = requests.get(F"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json").json()
    combo_json = requests.get(
        "https://raw.githubusercontent.com/BadMaliciousPyScripts/combo_json/main/combos.json").json()

    printy(rf"""
    LoL Version: {version}
    Number of champions: {len(champs_req["data"])}
    Number of available combos: {len(combo_json)}
    """)

    # Start auth + main script
    print("Developed by:")
    printy(r"""
    [c>] _____       _                            _   @
    [c>]|  __ \     | |                          | |  @
    [c>]| |  | | ___| |_ ___ _ __ __ _  ___ _ __ | |_ @
    [c>]| |  | |/ _ \ __/ _ \ '__/ _` |/ _ \ '_ \| __|@
    [c>]| |__| |  __/ ||  __/ | | (_| |  __/ | | | |_ @
    [c>]|_____/ \___|\__\___|_|  \__, |\___|_| |_|\__|@
    [c>]                          __/ |               @
    [c>]                         |___/                @
    """)

    printy(f"Welcome! You're running Detergent's TFT bot.\nPlease feel free to ask questions or contribute at "
           f"https://github.com/Detergent13/tft-bot", "nB")
    print("Bot started, queuing up!")

    m = Main()

    while True:
        m.queue()

# End auth + main script
