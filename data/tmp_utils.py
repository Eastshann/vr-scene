from msgpack import ExtType
import numpy as np
from typing import Literal, Optional, Any


def controller_matrix(value: dict, side: Literal["left", "right"]= "left") -> Optional[np.ndarray]:
    """
    解析运动控制器齐次变换矩阵

    Args:
        value (dict): 控制器运动事件返回的数据
        side   (str): 选择左右

    Returns:
        np.array: 4x4齐次变换矩阵
    """
    matrix = value.get(side)
    if isinstance(matrix, ExtType):
        return None
    matrix = list2array(matrix)
    return matrix

def controller_state(value: dict,
                     side_state: Literal["leftState", "rightState"] = "leftState",
                     item: str="trigger") -> Any:
    """
    解析运动控制器按钮状态数据

    Args:
        value     (dict): 控制器运动事件返回的数据
        side_state (str): 选择左右
        item       (str): 查询项

    Returns:
        Any: 查询项的值
    """
    side_state = value[side_state]
    state = side_state.get(item, None)
    if state is None:
        return None

    return state

def list2array(matrix: list,
               order: Literal['F', 'C'] = 'F') -> np.ndarray:
    """
    将长度为16的列表转换为4x4的矩阵

    Args:
        matrix (list): 列表
        order   (str): 选择列主序或者行主序

    Returns:
        np.ndarray: 4x4的矩阵
    """
    arr = np.array(matrix)
    mat = arr.reshape(4, 4, order=order)
    return mat

def parse_matrix(matrix: np.ndarray)->tuple[np.ndarray, np.ndarray]:
    """
    解析齐次变换矩阵，把R,t拆解出来

    Args:
        matrix (array): 4x4齐次变换矩阵

    Returns:
        np.ndarray, np.ndarray: 旋转矩阵, 平移矩阵
    """
    R = matrix[:3,:3]
    t = matrix[:3, 3]

    return R, t

def R2q(R: np.ndarray):
    """
    将旋转矩阵转换为四元数
    """
    R = np.array(R, dtype=float)
    assert R.shape == (3, 3)

    t = np.trace(R)
    if t > 0:
        w = 0.5 * np.sqrt(1 + t)
        x = (R[2, 1] - R[1, 2]) / (4 * w)
        y = (R[0, 2] - R[2, 0]) / (4 * w)
        z = (R[1, 0] - R[0, 1]) / (4 * w)
    else:
        if R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
            x = 0.5 * np.sqrt(1 + R[0, 0] - R[1, 1] - R[2, 2])
            y = (R[0, 1] + R[1, 0]) / (4 * x)
            z = (R[0, 2] + R[2, 0]) / (4 * x)
            w = (R[2, 1] - R[1, 2]) / (4 * x)
        elif R[1, 1] > R[2, 2]:
            y = 0.5 * np.sqrt(1 - R[0, 0] + R[1, 1] - R[2, 2])
            x = (R[0, 1] + R[1, 0]) / (4 * y)
            z = (R[1, 2] + R[2, 1]) / (4 * y)
            w = (R[0, 2] - R[2, 0]) / (4 * y)
        else:
            z = 0.5 * np.sqrt(1 - R[0, 0] - R[1, 1] + R[2, 2])
            x = (R[0, 2] + R[2, 0]) / (4 * z)
            y = (R[1, 2] + R[2, 1]) / (4 * z)
            w = (R[1, 0] - R[0, 1]) / (4 * z)

    q = np.array([x, y, z, w])
    return q / np.linalg.norm(q)  # 归一化

def camera_matrix(camera_data):
    matrix = camera_data.get("matrix")
    if isinstance(matrix, list):
        matrix = list2array(matrix)
        return matrix
    return None

def controll2camera(Hand_t: np.ndarray, Head_t: np.ndarray):
    """
    计算手部坐标相对于头部坐标的位移

    Args:
        Hand_t (np.ndarray): 手部坐标
        Head_t (np.ndarray): 头部坐标

    Returns:
        np.ndarray: 相对位移
    """
    C = Hand_t - Head_t
    return C