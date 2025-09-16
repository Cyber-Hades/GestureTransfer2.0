import socket
import threading

HOST = "0.0.0.0"
PORT = 9999

clients = {}  # {conn: code}
code_counter = 1000
lock = threading.Lock()

def assign_code(conn):
    global code_counter
    with lock:
        code = f"{code_counter:04d}"
        code_counter += 1
    clients[conn] = code
    return code

def handle_client(conn, addr):
    code = assign_code(conn)
    print(f"[+] Connected: {addr} → Code {code}")
    conn.sendall((json_encode({"type": "assign_code", "code": code}) + "\n").encode())

    buffer = ""
    try:
        while True:
            data = conn.recv(1024 * 1024)
            if not data:
                break
            buffer += data.decode()

            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                if msg.strip():
                    payload = json_decode(msg)
                    route_message(payload, conn)
    except Exception as e:
        print(f"[X] Error with {addr}: {e}")
    finally:
        if conn in clients:
            print(f"[-] Disconnected: {addr} (Code {clients[conn]})")
            del clients[conn]
        conn.close()

def route_message(payload, sender_conn):
    """Route message based on destination code"""
    dest_code = payload.get("dest")
    message = json_encode(payload) + "\n"

    if dest_code == "9999":  # broadcast
        for c in clients:
            if c != sender_conn:
                try:
                    c.sendall(message.encode())
                except:
                    c.close()
    else:
        for c, code in clients.items():
            if code == dest_code:
                try:
                    c.sendall(message.encode())
                except:
                    c.close()

def start_server():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"[Relay] Listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def json_encode(obj):
    import json
    return json.dumps(obj)

def json_decode(s):
    import json
    return json.loads(s)

if __name__ == "__main__":
    start_server()
