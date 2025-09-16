import socket
import threading
import json
import os
import base64
import pyperclip
import pyautogui
import cv2
import mediapipe as mp
import subprocess
import time
import win32clipboard
import win32con
import win32gui
from queue import Queue

# 🔧 Load config
with open("config.json", "r") as f:
    CONFIG = json.load(f)

RELAY_IP = CONFIG["relay_ip"]
PORT = CONFIG["port"]
FALLBACK_FOLDER = "D:/Data_Transfer_AI"
os.makedirs(FALLBACK_FOLDER, exist_ok=True)

relay_socket = None
incoming_queue = Queue()
my_code = None

#  Hand Gesture Detection
class HandGestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                tips = [8, 12, 16, 20]
                fingers = [hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y for tip in tips]
                return "open" if all(fingers) else "closed"
        return None

#  Clipboard
def capture_clipboard():
    win32clipboard.OpenClipboard()
    if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
        files = win32clipboard.GetClipboardData(win32con.CF_HDROP)
        win32clipboard.CloseClipboard()
        payload_files = []
        for path in files:
            if os.path.isfile(path):
                with open(path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                payload_files.append({
                    "filename": os.path.basename(path),
                    "data": encoded
                })
        return {"type": "files", "files": payload_files}
    win32clipboard.CloseClipboard()
    text = pyperclip.paste()
    if text.strip():
        return {"type": "text", "data": text}
    return None

#  Send
def send_data(payload, dest_code):
    global relay_socket
    try:
        payload["dest"] = dest_code
        msg = json.dumps(payload) + "\n"
        relay_socket.sendall(msg.encode())
        print(f"[✓] Sent data to {dest_code}")
    except Exception as e:
        print("[X] Send failed:", e)

#  Receive
def save_received_data(data):
    incoming_queue.put(data)
    print(f"[📨] Queued data from {data.get('src','?')} of type {data['type']}")

#  Get focused folder
def get_focused_folder():
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    if "File Explorer" in title or "\\" in title:
        return title
    return None

# ️ Paste all queued
def perform_paste():
    global incoming_queue
    if incoming_queue.empty():
        print("[!] Queue empty.")
        return

    folder_path = get_focused_folder()
    if not folder_path or not os.path.exists(folder_path):
        folder_path = FALLBACK_FOLDER

    while not incoming_queue.empty():
        data = incoming_queue.get()
        data_type = data.get("type")
        if data_type == "text":
            subprocess.Popen(["notepad.exe"])
            time.sleep(1)
            pyperclip.copy(data["data"])
            pyautogui.hotkey("ctrl", "v")
            print("[📝] Text pasted.")
        elif data_type == "files":
            for file in data["files"]:
                filename = file.get("filename", "file.unknown")
                filepath = os.path.join(folder_path, filename)
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(file["data"]))
                os.startfile(filepath)
                print(f"[📁] File saved & opened: {filename}")

#  Connect
def connect_to_relay():
    global relay_socket, my_code
    while True:
        try:
            relay_socket = socket.socket()
            relay_socket.connect((RELAY_IP, PORT))
            print(f"[🔌] Connected to relay {RELAY_IP}:{PORT}")
            break
        except Exception as e:
            print(f"[X] Connection failed: {e}. Retrying in 3s...")
            time.sleep(3)

    def listen():
        global relay_socket, my_code
        buffer = ""
        while True:
            try:
                data = relay_socket.recv(1024*1024)
                if not data:
                    break
                buffer += data.decode()
                while "\n" in buffer:
                    msg, buffer = buffer.split("\n", 1)
                    if msg.strip():
                        payload = json.loads(msg)
                        if payload.get("type") == "assign_code":
                            my_code = payload["code"]
                            print(f"[🆔] Your node code: {my_code}")
                        else:
                            save_received_data(payload)
            except Exception as e:
                print("[!] Relay connection lost:", e)
                break

    threading.Thread(target=listen, daemon=True).start()

#  Gesture monitor
def monitor_gestures():
    detector = HandGestureDetector()
    cap = cv2.VideoCapture(0)
    prev = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gesture = detector.detect(frame)
        if gesture != prev:
            if prev == "open" and gesture == "closed":
                pyautogui.hotkey("ctrl", "a")
                pyautogui.hotkey("ctrl", "c")
                time.sleep(0.5)
                payload = capture_clipboard()
                if payload:
                    print("[📤] Clipboard captured.")
                    dest_code = input("Enter 4-digit code (9999=broadcast, 0000=discard): ").strip()
                    if dest_code != "0000":
                        payload["src"] = my_code
                        send_data(payload, dest_code)
                else:
                    print("[!] Nothing to send.")
            elif prev == "closed" and gesture == "open":
                print("[📥] Performing paste from queue...")
                perform_paste()
            prev = gesture

        cv2.imshow("Gesture", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

#  Entry Point
if __name__ == "__main__":
    connect_to_relay()
    monitor_gestures()
