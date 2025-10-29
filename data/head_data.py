from .tmp_utils import camera_matrix, parse_matrix, R2q

class HeadData:
    def __init__(self):
        self.matrix = None          # 4x4齐次变换矩阵
        self.R = None               # 3x3旋转矩阵
        self.t = None               # 3x1平移矩阵
        self.position = None        # 位置
        self.rotation = None        # 欧拉角
        self.q = None               # 四元数

    def update(self, value):
        camera_data = value["camera"]

        self.matrix = camera_matrix(camera_data)
        self.R, self.t = parse_matrix(self.matrix)
        self.q = R2q(self.R)

        self.position = camera_data["position"]
        self.rotation = camera_data["rotation"]
