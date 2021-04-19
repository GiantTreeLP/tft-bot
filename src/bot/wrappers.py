import ctypes.wintypes
import random
import time
from ctypes import windll
from typing import Union

import cv2
import numpy as np
import pyautogui as auto
import win32gui
import win32ui
from pygetwindow import Win32Window

# Procedure definition for getting child windows aka. controls
enumChildWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

POS_NOT_FOUND = [-1, -1]

DEBUG = False


class Wrappers:
    GAME = "League of Legends (TM) Client"
    LAUNCHER = "League of Legends"
    LAUNCHER_CONTROL = "Chrome Legacy Window"

    ACTIVE_WINDOW = LAUNCHER

    IMAGE_CACHE = dict()

    SCREENSHOT: np.ndarray = None

    @staticmethod
    def search(image: Union[str, np.ndarray], precision: float = 0.8):
        # Optimization
        if isinstance(image, str):
            if not (image in Wrappers.IMAGE_CACHE):
                im = cv2.imread(image, 0)
                if im is None:
                    raise
                # im = cv2.cvtColor(im, cv2.COLOR_BGRA2GRAY)
                Wrappers.IMAGE_CACHE[image] = im
            return Wrappers.search(Wrappers.IMAGE_CACHE[image], precision)
        elif isinstance(image, np.ndarray):
            box = None
            if Wrappers.SCREENSHOT is None:
                box = Wrappers.screenshot_active_window()
            else:
                window = Wrappers.get_tft_window()
                if window is not None:
                    box = window.box

            if box is None:
                return POS_NOT_FOUND

            im = Wrappers.SCREENSHOT

            if im.shape[0] < image.shape[0] or im.shape[1] < image.shape[1]:
                return POS_NOT_FOUND

            im_gray = cv2.cvtColor(im, cv2.COLOR_BGRA2GRAY)
            res = cv2.matchTemplate(im_gray, image, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            if DEBUG:
                cv2.circle(im, max_loc, 16, (0, 0, 255, 255), 4)
                cv2.namedWindow("test")
                im_small = cv2.resize(im, (640, 360))
                cv2.imshow("test", im_small)
                Wrappers.wait(1)

            if max_val < precision:
                return POS_NOT_FOUND

            max_loc = (max_loc[0] + random.randint(0, image.shape[1])), max_loc[1] + random.randint(0, image.shape[0])

            return tuple(np.add(max_loc, (box.left, box.top)))

    @staticmethod
    def screenshot_active_window():
        window = Wrappers.get_tft_window()

        if window is None:
            return None

        Wrappers.SCREENSHOT = Wrappers.screenshot(window)
        return window.box

    @staticmethod
    def get_tft_window() -> Union[Win32Window, None]:
        windows = auto.getAllWindows()

        window = [window for window in windows if window.title == Wrappers.ACTIVE_WINDOW]

        if window:
            window = window[0]

            if Wrappers.ACTIVE_WINDOW != Wrappers.LAUNCHER:
                return window
            else:
                children = []

                def foreach_child(hwnd: int, lparam: int):
                    children.append(auto.Window(hwnd & 0xFFFFFFFF))
                    return True

                win32gui.EnumChildWindows(window._hWnd, enumChildWindowsProc(foreach_child), 0)

                children_by_name = [window for window in children if window.title == Wrappers.LAUNCHER_CONTROL]
                if children_by_name:
                    return children_by_name[0]
        else:
            return None

    @staticmethod
    def screenshot(window: Win32Window) -> np.ndarray:
        width, height = window.width, window.height
        h_wnd = window._hWnd

        h_dc = win32gui.GetWindowDC(h_wnd)

        my_dc = win32ui.CreateDCFromHandle(h_dc)
        new_dc = my_dc.CreateCompatibleDC()

        my_bit_map = win32ui.CreateBitmap()
        my_bit_map.CreateCompatibleBitmap(my_dc, width, height)

        new_dc.SelectObject(my_bit_map)

        windll.user32.PrintWindow(h_wnd, new_dc.GetSafeHdc(), 2)

        array = np.frombuffer(my_bit_map.GetBitmapBits(True), dtype='uint8')
        array.shape = (height, width, -1)

        win32gui.DeleteObject(my_bit_map.GetHandle())
        new_dc.DeleteDC()
        my_dc.DeleteDC()
        win32gui.ReleaseDC(h_dc, h_wnd)

        return array

    @staticmethod
    def onscreen(path, precision=0.8):
        search = Wrappers.search(path, precision)
        return search != POS_NOT_FOUND

    @staticmethod
    def search_to(path):
        pos = Wrappers.search(path)
        if pos != POS_NOT_FOUND:
            auto.moveTo(pos)
            return pos

    @staticmethod
    def click_key(key, delay=0.1):
        auto.keyDown(key)
        Wrappers.wait(int(delay * 1000))
        auto.keyUp(key)

    @staticmethod
    def click_left(delay=0.1):
        auto.mouseDown(button=auto.LEFT)
        Wrappers.wait(int(delay * 1000))
        auto.mouseUp(button=auto.LEFT)

    @staticmethod
    def click_right(delay=0.1):
        auto.mouseDown(button=auto.RIGHT)
        Wrappers.wait(int(delay * 1000))
        auto.mouseUp(button=auto.RIGHT)

    @staticmethod
    def click_to(path, delay=0.1, precision=0.8):
        pos = Wrappers.search(path, precision)
        if pos != POS_NOT_FOUND:
            Wrappers.get_tft_window().activate()
            auto.moveTo(pos, duration=delay)
            Wrappers.click_left(delay)
            print(f"Clicked left at {pos} on {path}")
            # wrappers.click_left(delay)

    @staticmethod
    def click_to_r(path, delay=0.1, precision=0.8):
        pos = Wrappers.search(path, precision)
        if pos != POS_NOT_FOUND:
            Wrappers.get_tft_window().activate()
            auto.moveTo(pos, duration=delay)
            Wrappers.click_right(delay)
            print(f"Clicked right at {pos} on {path}")
            # wrappers.click_right(delay)
        # print(path + " clicked")

    @staticmethod
    def move_to(pos):
        window = Wrappers.get_tft_window()
        window.activate()
        auto.moveTo(tuple(np.add(pos, window.topleft)))

    @staticmethod
    def wait(milliseconds: int):
        if DEBUG:
            cv2.waitKey(milliseconds)
        else:
            time.sleep(milliseconds / 1000)
