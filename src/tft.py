# Detergent's TFT Bot
# Branch: main
import json

import pkg_resources
import requests
import urllib3
from printy import printy

from bot.main import Main

pkg_resources.require("PyAutoGUI~=0.9.50")
pkg_resources.require("opencv-python~=4.5.1.48")
pkg_resources.require("pywin32>=300")
pkg_resources.require("PyDirectInput~=1.0.4")

urllib3.disable_warnings()
# If you haven't installed your game in default path (Windows) set your path here
PATH = r"G:\Games\Riot Games\League of Legends\lockfile"
# auto.FAILSAFE = False
# pydirectinput.FAILSAFE = False

if __name__ == '__main__':
    print("Downloading resources...")

    # Load resources once at the start
    version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
    champs_req = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json").json()
    # combo_json = list(requests.get(
    #     "https://raw.githubusercontent.com/BadMaliciousPyScripts/combo_json/main/combos.json").json().items())

    with open("combos.json") as f:
        combo_json = list(json.load(f).items())

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

    m = Main(combo_json, champs_req, PATH)

    while True:
        m.queue()
