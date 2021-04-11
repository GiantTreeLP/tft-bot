import random
import time

import cv2
import pyautogui as auto
import pydirectinput

from bot.wrappers import Wrappers
from lol.lcu import LCU


class Main:

    def __init__(self, combo_json, champs_req, path):
        self.combo_json = combo_json
        self.champs_req = champs_req
        self.path = path
        self.combo_champs = []
        self.combo = random.choice(combo_json)

    def generate_combo(self):
        self.combo = random.choice(self.combo_json)
        self.combo_champs = []
        for x in list(self.champs_req["data"]):
            try:
                if self.combo[1]["Champions"][x]:
                    self.combo_champs.append(x)
            except KeyError:
                pass

    def queue(self):
        Wrappers.ACTIVE_WINDOW = Wrappers.LAUNCHER
        lcu_data = LCU.connect(self.path)
        print("Creating tft lobby...")
        LCU.create_game_lobby_tft(lcu_data)
        LCU.start_search(lcu_data)
        time.sleep(2)  # Sleep in order to make sure the queue has enough time to start
        while True:
            if auto.getWindowsWithTitle(Wrappers.GAME):
                print("Game running, skipping queue...")
                break
            response = LCU.auto_accept_current_ready_check(lcu_data)
            if response == "Accepted!":
                time.sleep(5)
                response = LCU.auto_accept_current_ready_check(lcu_data)
                if response == "Not in queue!":
                    break
            # elif response == "Not in queue!":
            #     break
            time.sleep(2)
        self.loading()

    def loading(self):
        Wrappers.ACTIVE_WINDOW = Wrappers.GAME
        print("Loading...")
        while not Wrappers.onscreen("../captures/1-1.png"):
            if Wrappers.onscreen("../captures/reroll.png"):
                break
            cv2.waitKey(1000)
        print("Match starting!")
        self.start()

    def start(self):
        Wrappers.ACTIVE_WINDOW = Wrappers.GAME
        print("In the match now!")

        self.generate_combo()
        print(f"Selected combo: {self.combo_champs}")

        self.main()

    def buy(self, iterations: int = 1):
        Wrappers.ACTIVE_WINDOW = Wrappers.GAME
        for i in range(iterations):
            for champ in self.combo_champs:
                Wrappers.click_to(f"../captures/champions/{champ.lower()}.png")

    def buy_reroll(self):
        Wrappers.ACTIVE_WINDOW = Wrappers.GAME

        for champ in self.combo_champs:
            Wrappers.click_to(f"../captures/champions/{champ.lower()}.png")
        if not any(Wrappers.onscreen(f"../captures/champions/{champ.lower()}.png") for champ in self.combo_champs):
            # Only re-roll if there is no champ we want to buy
            Wrappers.click_to("../captures/reroll.png")

    def main(self):
        Wrappers.ACTIVE_WINDOW = Wrappers.GAME

        stage = "1-1"

        while Wrappers.get_tft_window():

            if Wrappers.onscreen("../captures/exit.png"):
                Wrappers.click_to("../captures/exit.png")
                self.exit_game()
                break

            # Main loop
            if stage == "1-1":
                self.pick_champ("../captures/1-1.png")
                stage = "1-2"
            elif stage == "1-2":
                self.buy_loop("../captures/2-4.png")
                print("2-4 reached")
                stage = "2-4"
            elif stage == "2-4":
                self.pick_champ("../captures/2-4.png")
                print("2-5 reached")
                stage = "2-5"
            elif stage == "2-5":
                self.buy_reroll_loop("../captures/3-4.png", precision=0.95)
                print("3-4 reached")
                stage = "3-4"
            elif stage == "3-4":
                self.pick_champ("../captures/3-4.png")
                stage = "3-5"
            elif stage == "3-5":
                self.buy_reroll_loop("../captures/4-4.png", precision=0.95)
                print("4-4 reached")
                stage = "4-4"
            elif stage == "4-4":
                self.pick_champ("../captures/4-4.png")
                stage = "4-5"
            elif stage == "4-5":
                self.buy_reroll_loop("../captures/5-3.png", precision=0.95)
                print("5-3 reached")
                stage = "5-3"
            elif stage == "5-3":
                if Wrappers.onscreen("../captures/5-3.png", precision=0.95):
                    print("Surrendering now!")
                    self.surrender()

    def pick_champ(self, path: str):
        Wrappers.ACTIVE_WINDOW = Wrappers.GAME
        while Wrappers.onscreen(path):
            top_left = Wrappers.get_tft_window().topleft
            auto.rightClick(top_left.x + 928 + random.randint(-25, 25), top_left.y + 396 + random.randint(-10, 10))
            cv2.waitKey(1000)
        cv2.waitKey(4000)

    def orbs(self, iterations: int = 1):
        Wrappers.ACTIVE_WINDOW = Wrappers.GAME
        for i in range(iterations):
            Wrappers.click_to_r("../captures/orb_white.png", precision=0.82)
            Wrappers.click_to_r("../captures/orb_blue.png", precision=0.7)
            Wrappers.click_to_r("../captures/orb_red.png", precision=0.8)
            # wrappers.click_to("./captures/orb_fortune.png")

    def surrender(self):
        Wrappers.ACTIVE_WINDOW = Wrappers.GAME
        while not Wrappers.onscreen("../captures/surrender 2.png"):
            pydirectinput.press('enter')
            auto.write("/ff")
            pydirectinput.press('enter')
        cv2.waitKey(1000)
        Wrappers.click_to("../captures/surrender 2.png")
        self.exit_game()

    def buy_loop(self, path: str, precision: float = 0.8):
        while not Wrappers.onscreen(path, precision) and not Wrappers.onscreen("../captures/exit.png"):
            self.orbs(1)
            self.buy()
            cv2.waitKey(1000)

    def buy_reroll_loop(self, path: str, precision: float = 0.8):
        while not Wrappers.onscreen(path, precision) and not Wrappers.onscreen("../captures/exit.png"):
            self.orbs(1)
            self.buy_reroll()
            cv2.waitKey(1000)

    def exit_game(self):
        Wrappers.ACTIVE_WINDOW = Wrappers.LAUNCHER
        cv2.waitKey(15000)
        while Wrappers.onscreen("../captures/missions ok.png"):
            Wrappers.click_to("../captures/missions ok.png")
            cv2.waitKey(5000)
        while Wrappers.onscreen("../captures/skip waiting for stats.png"):
            Wrappers.click_to("../captures/skip waiting for stats.png")
        cv2.waitKey(5000)
        lcu_data = LCU.connect(self.path)
        LCU.play_again(lcu_data)
        cv2.waitKey(10000)
        print("Queuing up again!")
