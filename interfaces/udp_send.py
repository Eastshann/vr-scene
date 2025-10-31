import socket

class UDPSend:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self._init_socket()

    def _init_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        try:
            self.sock.sendto(data, (self.ip, self.port))
            # print(f"[UDPSend] send {data}")
        except Exception as e:
            print("[UDPSend] UDP send error")