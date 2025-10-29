import numpy as np
from typing import Literal
from .tmp_utils import *

class ControllerData:
    def __init__(self, side: Literal["left", "right"] = "left"):

        self.side = side
        self.side_state = side+"State"

        self.matrix = None                  # 4x4齐次变换矩阵
        self.R = None                       # 3x3旋转矩阵
        self.t = None                       # 3x1平移矩阵
        self.q = None                       # 四元数

        self.trigger = False                # 板机
        self.squeeze = False                # 侧边板机
        self.thumbstick = False             # 摇杆
        self.aButton = False                # 按钮A
        self.bButton = False                # 按钮B

        self.trigger_value = None
        self.squeeze_value = None
        self.thumbstick_value = None
        self.aButton_value = None
        self.bButton_value = None

    def update(self, value):
        self.matrix = controller_matrix(value, side=self.side)
        if self.matrix is not None:
            self.R, self.t = parse_matrix(self.matrix)
            self.q = R2q(self.R)
        else:
            self.R, self.t = None, None
            self.q = None

        self.trigger = controller_state(value, side_state=self.side_state, item="trigger")
        self.squeeze = controller_state(value, side_state=self.side_state, item="squeeze")
        self.thumbstick = controller_state(value, side_state=self.side_state, item="thumbstick")
        self.aButton = controller_state(value, side_state=self.side_state, item="aButton")
        self.bButton = controller_state(value, side_state=self.side_state, item="bButton")

        self.trigger_value = controller_state(value, side_state=self.side_state, item="triggerValue")
        self.squeeze_value = controller_state(value, side_state=self.side_state, item="squeezeValue")
        self.thumbstick_value = controller_state(value, side_state=self.side_state, item="thumbstickValue")
        self.aButton_value = controller_state(value, side_state=self.side_state, item="aButtonValue")
        self.bButton_value = controller_state(value, side_state=self.side_state, item="bButtonValue")

    def get_data(self):
        data = {
            "matrix" : self.matrix.tolist() if self.matrix is not None else None,
            "R" : self.R.tolist() if self.R is not None else None,
            "t" : self.t.tolist() if self.t is not None else None,
            "q" : self.q.tolist() if self.q is not None else None,

            "trigger" : self.trigger,
            "squeeze" : self.squeeze,
            "thumbstick" : self.thumbstick,
            "aButton" : self.aButton,
            "bButton" : self.bButton,

            "trigger_value" : self.trigger_value,
            "squeeze_value" : self.squeeze_value,
            "thumbstick_value" : self.thumbstick_value
        }

        return data


