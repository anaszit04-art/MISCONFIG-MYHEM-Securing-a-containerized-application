import os
import requests
import socket

TARGET = "http://localhost"

def check_env():
    print("[+] .env exposure:", requests.get(TARGET + "/.env").status_code)

def check_debug():
    print("[+] Debug endpoint:", requests.get(TARGET + "/debug/info").status_code)

def check_headers():
    r = requests.get(TARGET)
    headers = r.headers
    needed = ["X-Frame-Options", "Content-Security-Policy", "X-Content-Type-Options"]
    for h in needed:
        print(f"[+] {h}:", h in headers)

def check_ports():
    ports = [80, 443, 5432, 9000]
    for p in ports:
        s = socket.socket()
        res = s.connect_ex(("127.0.0.1", p))
        print(f"[+] Port {p} open:", res == 0)
        s.close()

check_env()
check_debug()
check_headers()
check_ports()
