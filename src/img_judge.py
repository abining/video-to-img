import cv2
import numpy as np
from typing import Tuple

class ImageComparator:
    def __init__(self, similarity_threshold: float = 0.98):
        """
        初始化图片比较器
        :param similarity_threshold: 相似度阈值，默认0.98（98%）
        """
        self.similarity_threshold = similarity_threshold
        self.last_hash = None
        self.hash_size = 8  # dhash 大小，可以根据需要调整
        
    def calculate_dhash(self, image: np.ndarray) -> np.ndarray:
        """
        计算图片的 dhash
        :param image: OpenCV 格式的图片
        :return: dhash 值
        """
        # 调整图片大小为 9x8
        resized = cv2.resize(image, (self.hash_size + 1, self.hash_size))
        
        # 转换为灰度图
        if len(resized.shape) == 3:
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        else:
            gray = resized
            
        # 计算差异值
        diff = gray[:, 1:] > gray[:, :-1]
        
        return diff

    def hamming_distance(self, hash1: np.ndarray, hash2: np.ndarray) -> float:
        """
        ��算两个哈希值的汉明距离
        :return: 相似度（0-1之间，1表示完全相同）
        """
        if hash1 is None or hash2 is None:
            return 0
            
        distance = np.count_nonzero(hash1 != hash2)
        total_bits = hash1.size
        similarity = 1 - (distance / total_bits)
        
        return similarity

    def is_similar_to_last(self, image: np.ndarray) -> Tuple[bool, float]:
        """
        判断当前图片是否与上一张图片相似
        :param image: OpenCV 格式的图片
        :return: (是否相似, 相似度)
        """
        current_hash = self.calculate_dhash(image)
        
        if self.last_hash is None:
            self.last_hash = current_hash
            return False, 0.0
            
        similarity = self.hamming_distance(current_hash, self.last_hash)
        self.last_hash = current_hash
        
        return similarity >= self.similarity_threshold, similarity

    def reset(self):
        """重置比较器状态"""
        self.last_hash = None
