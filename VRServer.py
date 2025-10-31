import time
import json
import cv2
import queue
from queue                  import Queue
from threading              import Thread
from asyncio                import sleep
from vuer                   import Vuer, VuerSession
from vuer.schemas           import CoordsMarker, MotionControllers, ImageBackground

from data                   import HeadData, ControllerData, CameraData
from interfaces             import UDPSend

LEFT_COORD_KEY = "left-controller-box"
RIGHT_COORD_KEY = "right-controller-box"
LEFT_INITIAL_KEY = "left-initial-coord"
RIGHT_INITIAL_KEY = "right-initial-coord"

class VRServer:
    def __init__(self, ip, port, sleep_time=0.05):
        self.ip = ip
        self.port = port
        # data
        self.left_controller    = ControllerData(side="left")
        self.right_controller   = ControllerData(side="right")
        self.head_data          = HeadData()
        self.camera_data        = CameraData()
        self.vr_queue = Queue()
        # WebXR
        self.app = Vuer()
        self.app.add_handler("CONTROLLER_MOVE")(self._on_control_move)
        self.app.add_handler("CAMERA_MOVE")(self._on_camera_move)
        # register two background tasks
        # self.app.spawn()(self._main_loop)
        self.app.spawn()(self._camera_stream_loop)
        # udp
        self.udp_send = UDPSend(self.ip, self.port)     # send quest3 data to teleop
        self.send_thread = Thread(target=self._send_data, daemon=True)
        self.send_thread.start()

        self.sleep_time = sleep_time
        self.state_0 = False  # 校正点状态
        self.last_time = None
        self.count = 0

    async def _main_loop(self, session: VuerSession):
        self._init_session(session)
        while True:
            # update component
            self._update_controller_marker(session, self.left_controller, LEFT_COORD_KEY)
            self._update_controller_marker(session, self.right_controller, RIGHT_COORD_KEY)
            # create fixed point
            # if (self.state_0 == False) and self.left_controller.trigger:
            #     self._update_controller_marker(session, self.left_controller, LEFT_INITIAL_KEY)
            #     self._update_controller_marker(session, self.right_controller, RIGHT_INITIAL_KEY)
            #     self.state_0 = True

            await sleep(self.sleep_time)  # 20Hz

    def _init_session(self, session: VuerSession):
        session.upsert(
            MotionControllers(
                stream=True,
                key="motion-controller",
                left=True,
                right=True,
                fps=60
            )
        )

    def _update_controller_marker(self, session: VuerSession, controller: ControllerData, key: str):
        if controller.matrix is not None:
            x, y, z = controller.t
            session.upsert(
                CoordsMarker(
                    position=[x, y, z],  # 位置
                    quaternion=controller.q,  # 四元数
                    scale=0.1,
                    key=key,
                )
            )

    async def _camera_stream_loop(self, session: VuerSession):
        """后台协程任务：不断从 camera_data.frame_queue 取帧并显示"""
        self._init_session(session)
        print("[CameraStream] started.")
        while True:
            if not self.camera_data.frame_queue.empty():
                frame = self.camera_data.frame_queue.get()
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if frame is not None:
                    # 将图像帧显示到WebXR场景
                    session.upsert(
                        ImageBackground(
                            rgb_frame,
                            format="jpeg",
                            quality=60,
                            aspect=16 / 9,
                            key="camera_stream",
                            fixed=True,
                            # distanceToCamera=1.5,
                            position=[0, 1, -20],
                        )
                    )
            await sleep(0.016)  # 控制帧率约60FPS

    async def _on_control_move(self, event, session):
        value = event.value
        self.left_controller.update(value)
        self.right_controller.update(value)

        self._add_data2queue()

    async def _on_camera_move(self, event, session):
        value = event.value
        self.head_data.update(value)

    def _add_data2queue(self):
        data = {
            "left": self.left_controller.get_data(),
            "right": self.right_controller.get_data()
        }
        self.vr_queue.put(data)

    def _send_data(self):
        while True:
            try:
                data = self.vr_queue.get(timeout=0.1)
                msg = json.dumps(data).encode('utf-8')
                self.udp_send.send(msg)
            except queue.Empty:
                continue

    def _count_hz(self):
        self.count += 1
        now = time.time()
        if self.last_time is None:
            self.last_time = now
        elif now - self.last_time >= 1.0:  # 每秒统计一次
            print(f"频率: {self.count} Hz")
            self.count = 0
            self.last_time = now

    def run(self):
        self.app.run()

if __name__ == "__main__":
    service = VRServer(ip="192.168.110.152", port=8090, sleep_time=0.05)
    service.run()