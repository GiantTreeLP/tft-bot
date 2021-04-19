import os

import requests

from bot.extra import Extra


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
                return 1
            elif request_json["state"] == "InProgress":
                if rc:
                    return 2
                return 1
        elif request_json["httpStatus"] == 404:
            return False

    @staticmethod
    def get_current_summoner_ready_check(lcu_data, rc=False):
        is_in_q = LCU.get_current_summoner_in_queue(lcu_data, True)
        if is_in_q == 2:
            return 1
        if is_in_q == 1 and rc:
            return 2
        return False

    @staticmethod
    def auto_accept_current_ready_check(lcu_data):
        ready_check = LCU.get_current_summoner_ready_check(lcu_data, True)
        if ready_check == 1:
            headers = LCU.get_lcu_headers(lcu_data)
            url = lcu_data["url"] + "/lol-matchmaking/v1/ready-check/accept"
            requests.post(url, headers=headers, verify=False)
            return "Accepted!"
        elif ready_check == 2:
            return "Waiting for ready check..."
        else:
            return "Not in queue!"
