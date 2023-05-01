import pyautogui
from datetime import datetime

ss = pyautogui.screenshot()

curr_date_time = datetime.now()
dt_string = curr_date_time.strftime("%d-%m-%Y_%H-%M-%S")

ss.save(f'screenshots/{dt_string}.jpg')