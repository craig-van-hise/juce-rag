import socket
import struct
import time
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
TARGET_MAC = os.getenv("WOL_MAC", "XX-XX-XX-XX-XX-XX")       # Your Windows PC Wi-Fi MAC
BROADCAST_IP = os.getenv("WOL_BROADCAST_ADDR")       # General Broadcast
OLLAMA_URL = os.getenv("OLLAMA_URL")

# Parse IP/Port from URL
from urllib.parse import urlparse
try:
    parsed = urlparse(OLLAMA_URL)
    OLLAMA_IP = parsed.hostname
    OLLAMA_PORT = parsed.port or 11434
except:
    OLLAMA_IP = os.getenv("OLLAMA_HOST_IP")
    OLLAMA_PORT = 11434
# ---------------------

def create_magic_packet(macaddress):
    # (Same function as before)
    if len(macaddress) == 12:
        pass
    elif len(macaddress) == 17:
        sep = macaddress[2]
        macaddress = macaddress.replace(sep, '')
    else:
        raise ValueError('Incorrect MAC address format')
    data = b'FFFFFFFFFFFF' + (macaddress * 16).encode()
    send_data = b''
    for i in range(0, len(data), 2):
        send_data += struct.pack('B', int(data[i: i + 2], 16))
    return send_data

def wake_device():
    print(f"Sending Wake-on-LAN packet to {TARGET_MAC}...")
    packet = create_magic_packet(TARGET_MAC)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (BROADCAST_IP, 9))
        sock.sendto(packet, (BROADCAST_IP, 7))

def wait_for_ollama(ip, port, timeout=60):
    """Loops until Ollama responds or timeout is reached."""
    print(f"Waiting for Ollama to become reachable at {ip}:{port}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Try to connect to the TCP port (fast check)
            with socket.create_connection((ip, port), timeout=1):
                print(f"✅ Server is UP! (Connected in {int(time.time() - start_time)}s)")
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            # Wait 2 seconds before trying again
            time.sleep(2)
            print(".", end="", flush=True)

    print("\n❌ Timed out waiting for server.")
    return False

if __name__ == '__main__':
    wake_device()
    
    # This will pause the script here until the PC is actually ready
    if wait_for_ollama(OLLAMA_IP, OLLAMA_PORT):
        print("\n🚀 Starting Embedding Task...")
        # --- YOUR EMBEDDING CODE GOES HERE ---
    else:
        print("\nCould not connect. Is the PC actually waking up?")