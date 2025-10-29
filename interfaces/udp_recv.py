import socket
import time

class UDPRecv:
    def __init__(self, ip: str = '0.0.0.0', port: int = 5005, recv_buf_size: int = 65536):
        self.ip = ip
        self.port = port
        self.recv_buf_size = recv_buf_size

        self._init_socket()

    def _init_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

    def recv(self):
        """
        receive data from UDP socket
        0-1     frame_id
        2-3     total
        4-5     idx
        6-...   image data
        """
        try:
            packet, addr = self.sock.recvfrom(65536)
            if len(packet) < 6:
                return None, None, None
            return packet, addr, time.time()

        except socket.timeout:
            return None, None, None
