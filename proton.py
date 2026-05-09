import os
import warnings
import tkinter as tk
from tkinter import scrolledtext, filedialog
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import subprocess
import threading
import pyautogui
import queue
import time
import fnmatch

# ---------------- Suppress Audio Warnings ----------------
os.environ["AUDIODEV"] = "default"
os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")

# ---------------- Initialize Speech Engine ----------------
engine = pyttsx3.init()
engine.setProperty('rate',175)

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

speech_queue = queue.Queue()

def speech_worker():
    while True:
        text = speech_queue.get()
        if text is None:
            break
        try:
            engine.say(text)
            engine.runAndWait()
        except:
            pass
        speech_queue.task_done()

threading.Thread(target=speech_worker,daemon=True).start()

def speak(text):
    speech_queue.put(text)

# ---------------- Speech Recognition ----------------
r = sr.Recognizer()

def take_command():
    try:
        with sr.Microphone() as source:
            print("[Listening...]")
            r.adjust_for_ambient_noise(source,duration=1)
            audio = r.listen(source,phrase_time_limit=5)

        query = r.recognize_google(audio,language='en-in')
        print("[You Said]:",query)
        return query

    except:
        return ""

# ---------------- Chat Display ----------------
def update_chat(sender,message):
    chat_window.configure(state="normal")
    chat_window.insert(tk.END,f"{sender}: {message}\n\n")
    chat_window.configure(state="disabled")
    chat_window.see(tk.END)

# ---------------- Volume Control ----------------

def volume_up():
    subprocess.call(["amixer","-D","pulse","sset","Master","5%+"])
    return "Volume increased"

def volume_down():
    subprocess.call(["amixer","-D","pulse","sset","Master","5%-"])
    return "Volume decreased"

def volume_mute():
    subprocess.call(["amixer","-D","pulse","set","Master","toggle"])
    return "Volume toggled"

# ---------------- WiFi Control ----------------

def wifi_on():
    subprocess.call(["nmcli","radio","wifi","on"])
    return "WiFi turned on"

def wifi_off():
    subprocess.call(["nmcli","radio","wifi","off"])
    return "WiFi turned off"

# ---------------- File Search ----------------
def search_and_open_file(name):

    home_dir = os.path.expanduser("~")

    for root_dir,dirs,files in os.walk(home_dir):
        for item in dirs + files:

            if fnmatch.fnmatch(item.lower(),f"*{name.lower()}*"):

                path=os.path.join(root_dir,item)
                subprocess.Popen(["xdg-open",path])
                return f"Opening {item}"

    return f"Sorry, I couldn’t find {name}"

# ---------------- Screenshot ----------------
def take_screenshot():

    file_path=os.path.join(
        os.path.expanduser("~"),
        f"screenshot_{int(time.time())}.png"
    )

    pyautogui.screenshot(file_path)

    return f"Screenshot saved to {file_path}"

# ---------------- Response Logic ----------------
def respond(query,update_chat):

    query=query.lower().strip()

    if "time" in query:
        reply=f"The time is {datetime.datetime.now().strftime('%I:%M %p')}."

    elif "date" in query:
        reply=f"Today's date is {datetime.date.today()}"

    elif "open youtube" in query:
        webbrowser.open("https://youtube.com")
        reply="Opening YouTube"

    elif "open google" in query:
        webbrowser.open("https://google.com")
        reply="Opening Google"

    elif "search" in query:
        term=query.replace("search","").strip()
        webbrowser.open(f"https://google.com/search?q={term}")
        reply=f"Searching for {term}"

# ---------- BROWSER ----------

    elif "open chrome" in query:
        subprocess.Popen(["google-chrome"])
        reply="Opening Chrome"

    elif "open firefox" in query:
        subprocess.Popen(["firefox"])
        reply="Opening Firefox"

    elif "open python tutorial in firefox" in query:
        subprocess.Popen(["firefox","https://www.google.com/search?q=python+tutorial"])
        reply="Opening Python tutorial"

# ---------- APPLICATIONS ----------

    elif "open text editor" in query:
        subprocess.Popen(["gedit"])
        reply="Opening Text Editor"

    elif "open vlc" in query:
        subprocess.Popen(["vlc"])
        reply="Opening VLC"

    elif "open terminal" in query:
        subprocess.Popen(["gnome-terminal"])
        reply="Opening Terminal"

    elif "open calculator" in query:
        subprocess.Popen(["gnome-calculator"])
        reply="Opening Calculator"

# ---------- FOLDERS ----------

    elif "open desktop" in query:
        subprocess.Popen(["xdg-open",os.path.expanduser("~/Desktop")])
        reply="Opening Desktop"

    elif "open downloads" in query:
        subprocess.Popen(["xdg-open",os.path.expanduser("~/Downloads")])
        reply="Opening Downloads"

    elif "open documents" in query:
        subprocess.Popen(["xdg-open",os.path.expanduser("~/Documents")])
        reply="Opening Documents"

# ---------- FILES ----------

    elif "open python file" in query:
        path=filedialog.askopenfilename(filetypes=[("Python Files","*.py")])

        if path:
            subprocess.Popen(["code",path])
            reply="Opening Python file"

        else:
            reply="No file selected"

    elif "open file from folder" in query:

        path=filedialog.askopenfilename()

        if path:
            subprocess.Popen(["xdg-open",path])
            reply=f"Opening {os.path.basename(path)}"

        else:
            reply="No file selected"

    elif "open folder" in query:

        path=filedialog.askdirectory()

        if path:
            subprocess.Popen(["xdg-open",path])
            reply="Opening folder"

        else:
            reply="No folder selected"

    elif "open file" in query:

        name=query.replace("open file","").strip()
        reply=search_and_open_file(name)

# ---------- SYSTEM CONTROL ----------

    elif "volume up" in query:
        reply=volume_up()

    elif "volume down" in query:
        reply=volume_down()

    elif "mute" in query:
        reply=volume_mute()

    elif "wifi on" in query:
        reply=wifi_on()

    elif "wifi off" in query:
        reply=wifi_off()

    elif "screenshot" in query:
        reply=take_screenshot()

# ---------- EXIT ----------

    elif "exit" in query or "bye" in query:
        reply="Goodbye! Have a nice day"
        update_chat("Proton",reply)
        speak(reply)
        root.after(1500,root.quit)
        return

    elif query=="":
        reply="Sorry I didn't hear anything"

    else:
        reply="Sorry, I don't know that command yet"

    update_chat("Proton",reply)
    speak(reply)

# ---------------- Command Handling ----------------
def listen_command():
    update_chat("Proton","🎤 Listening...")
    threading.Thread(target=_listen_and_respond,daemon=True).start()

def _listen_and_respond():
    query=take_command()

    if query:
        update_chat("You",query)
        respond(query,update_chat)
    else:
        update_chat("Proton","Sorry I didn't hear anything")

def send_text_command():

    query=user_input.get().strip()

    if query:
        update_chat("You",query)
        user_input.delete(0,tk.END)

        threading.Thread(
            target=respond,
            args=(query,update_chat),
            daemon=True
        ).start()

# ---------------- UI Setup ----------------
root=tk.Tk()
root.title("🔹 Proton Voice Assistant 🔹")
root.geometry("600x550")
root.configure(bg="#0b132b")

title=tk.Label(
    root,
    text="Proton Voice Assistant",
    font=("Arial",18,"bold"),
    bg="#0b132b",
    fg="#5bc0be"
)
title.pack(pady=10)

chat_window=scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    width=65,
    height=20,
    bg="#1c2541",
    fg="white",
    font=("Arial",12)
)

chat_window.pack(padx=10,pady=10)
chat_window.configure(state="disabled")

frame=tk.Frame(root,bg="#0b132b")
frame.pack(pady=10)

user_input=tk.Entry(frame,width=45,font=("Arial",12))
user_input.grid(row=0,column=0,padx=10)

send_button=tk.Button(
    frame,
    text="Send",
    font=("Arial",12,"bold"),
    bg="#5bc0be",
    fg="black",
    command=send_text_command
)
send_button.grid(row=0,column=1,padx=5)

listen_button=tk.Button(
    frame,
    text="🎙 Speak",
    font=("Arial",12,"bold"),
    bg="#5bc0be",
    fg="black",
    command=listen_command
)
listen_button.grid(row=0,column=2,padx=5)

# ---------------- Greeting ----------------
update_chat(
    "Proton",
    "Hello! I am Proton, your voice assistant. How may I help you today?"
)

speak(
    "Hello! I am Proton, your voice assistant. How may I help you today?"
)

root.mainloop()                                                                                                                                                                           