import struct
import time
import cv2
import numpy as np
from threading import Thread
from queue import Queue

from interfaces import UDPRecv

class CameraData:
    def __init__(self):
        self.udp_recv           = UDPRecv()
        self.frame_buffer       = {}
        self.last_frame_time    = {}
        self.frame_queue        = Queue(maxsize=5)
        self.recv_thread        = Thread(target=self._update_data, daemon=True)
        self.recv_thread.start()

    def _update_data(self):
        while True:
            packet, addr, rcv_time = self.udp_recv.recv()
            if packet is None:
                continue

            frame_id, total, index = struct.unpack("!HHH", packet[:6])
            data = packet[6:]

            if frame_id not in self.frame_buffer:
                self.frame_buffer[frame_id] = [None] * total    # init frame
                self.last_frame_time[frame_id] = time.time()
            self.frame_buffer[frame_id][index] = data

            # check is receive all
            if all(part is not None for part in self.frame_buffer[frame_id]):
                jpeg_bytes = b"".join(self.frame_buffer[frame_id])
                frame = cv2.imdecode(np.frombuffer(jpeg_bytes, np.uint8), cv2.IMREAD_COLOR)
                if frame is not None and not self.frame_queue.full():
                    self.frame_queue.put(frame)

                # clear
                del self.frame_buffer[frame_id]
                del self.last_frame_time[frame_id]

            now = time.time()
            for f_id in list(self.last_frame_time.keys()):
                if now - self.last_frame_time[f_id] > 1.0:
                    del self.frame_buffer[f_id]
                    del self.last_frame_time[f_id]

if __name__ == '__main__':
    camera = CameraData()
    while True:
        if not camera.frame_queue.empty():
            frame = camera.frame_queue.get()
            cv2.imshow("UDP Video", frame)
        if cv2.waitKey(1) == 27:  # ESC退出
            break
    cv2.destroyAllWindows()
