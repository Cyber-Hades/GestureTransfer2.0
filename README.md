# ✋ Gesture Transfer 2.0

Seamless **gesture-based file and message transfer** across **LAN or the Internet**.  
This project combines **Human-Computer Interaction (HCI)** with **socket programming** and **Ngrok tunneling** to enable contactless sharing using **hand gestures**.  

---

## ✨ Overview
**Gesture Transfer 2.0** allows you to send files or messages to another device using **hand gestures as triggers**.  
It works in two modes:  

- 🔹 **LAN Mode** → Share between devices on the same local network  
- 🔹 **Global Mode (Relay + Ngrok)** → Share files/messages with anyone worldwide via a relay server  

Built with **Python, OpenCV, Mediapipe, and Sockets**, this project demonstrates how gesture recognition can be integrated with networking for a unique, contactless experience.  

---

## 🛠 Tech Stack
- 🐍 **Python 3.x** – Core language  
- 👁 **OpenCV** – Computer vision  
- 🖐 **Mediapipe** – Hand tracking & gesture recognition  
- 🌐 **Socket Programming** – LAN & Relay communication  
- 🚀 **Ngrok** – Port forwarding for global connectivity  

---

## ⚡ Features
- ✋ Gesture-triggered transfers (no clicks needed)  
- 📡 Real-time file/message transfer across LAN or worldwide  
- 🔒 Configurable IP & Port (LAN) or Ngrok relay for global use  
- 💻 Cross-platform prototype (Windows/Linux tested)  
- 🌍 Unique **relay server codes** for targeting specific nodes or broadcasting  

---

## 🚀 Getting Started
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Cyber-Hades/GestureTransfer2.0
cd GestureTransfer2.0
```
---
### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
---
### 3️⃣ Relay + Ngrok Global Mode Setup
#### 3.1 Create Ngrok Config (ngrok.yml)
**Windows: C:\Users\<username>\AppData\Local\ngrok\ngrok.yml**
```bash
version: "3"
agent:
  authtoken: <YOUR_NGROK_AUTH_TOKEN>

tunnels:
  http-tunnel:
    proto: http
    addr: 5000

  tcp-tunnel:
    proto: tcp
    addr: 9999
```
#### 3.2 Start Ngrok
```bash
ngrok start --all
```
- **Ngrok will output public URLs:**
     - **HTTP → https://xxxx.ngrok.io** 
     - **TCP → tcp://0.tcp.ngrok.io:99999**

#### 3.3 Update Client config.json
```bash
{
  "relay_ip": "0.tcp.ngrok.io",
  "port": 99999
}
```
### 4️⃣ Run Relay Server
```bash
python relay.py
```
- **Relay assigns unique codes to clients**
- **Routes files/messages between nodes**
- **Supports node-to-node transfers or broadcast (9999)**
### 5️⃣ Run Client main.py
```bash
python main.py
```
- **Connects to the relay via Ngrok**
- **Receives a unique code**
- **Can now send files/messages to specific nodes or broadcast**
## 🎯 Use Cases

- 📂 **Contactless file sharing in labs, classrooms, or offices**
- 🖐 **Exploring Human-Computer Interaction (HCI) concepts**
- 🌍 **Worldwide file sharing via Ngrok relay server**
- 🎓 **Academic projects combining networking & gesture recognition**





