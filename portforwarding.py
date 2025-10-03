import socket
import threading
import sys
import time

LISTEN_HOST = "127.0.0.1"#localhost
LISTEN_PORT = 7777
TARGET_HOST = "192.168.0.32"
TARGET_PORT = 446
BUFFER_SIZE = 4096
CONNECT_TIMEOUT = 10

def relay(src_sock, dst_sock):
    try:
        while True:
            data = src_sock.recv(BUFFER_SIZE)
            if not data:
                break
            dst_sock.sendall(data)
    except Exception:
        pass
    finally:
        try:
            dst_sock.shutdown(socket.SHUT_WR)
        except Exception:
            pass

def handle_client(client_sock, client_addr):
    print(f"[+] New client: {client_addr} -> forwarding to {TARGET_HOST}:{TARGET_PORT}")
    try:
        remote = socket.create_connection((TARGET_HOST, TARGET_PORT), timeout=CONNECT_TIMEOUT)
    except Exception as e:
        print(f"[-] Failed to connect to target {TARGET_HOST}:{TARGET_PORT} : {e}")
        client_sock.close()
        return

    t1 = threading.Thread(target=relay, args=(client_sock, remote), daemon=True)
    t2 = threading.Thread(target=relay, args=(remote, client_sock), daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    try:
        client_sock.close()
    except Exception:
        pass
    try:
        remote.close()
    except Exception:
        pass
    print(f"[-] Connection closed: {client_addr}")

def serve():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((LISTEN_HOST, LISTEN_PORT))
    srv.listen(200)
    print(f"[+] Listening on {LISTEN_HOST}:{LISTEN_PORT} -> forwarding to {TARGET_HOST}:{TARGET_PORT}")
    try:
        while True:
            client_sock, client_addr = srv.accept()
            t = threading.Thread(target=handle_client, args=(client_sock, client_addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("Interrupted by user, shutting down.")
    except Exception as e:
        print("Server error:", e)
    finally:
        srv.close()

if __name__ == "__main__":
    print("tcp_forwarder_fixed starting...")
    serve()
