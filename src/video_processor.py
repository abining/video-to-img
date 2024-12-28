import cv2 # 导入opencv库,这个库的作用是处理视频帧，
import os
from typing import Optional
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from .img_judge import ImageComparator

class VideoProcessor:
    def __init__(self, input_path: str, output_dir: str, max_workers: int = 4):
        self.input_path = input_path
        self.output_dir = output_dir
        self.cap = None
        self.max_workers = max_workers
        self.lock = Lock()
        self.image_comparator = ImageComparator(similarity_threshold=0.98)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def __enter__(self):
        self.cap = cv2.VideoCapture(self.input_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cap:
            self.cap.release()
    
    def estimate_output_size(self, frame_interval: int = 1) -> float:
        """
        估算输出图片的总大小（MB）
        """
        if not self.cap:
            raise ValueError("视频未打开")
            
        # 读取一帧来计算单张图片大小
        ret, frame = self.cap.read()
        if not ret:
            return 0
            
        # 重置视频位置
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        # 计算单张图片大小（以JPEG格式估算，压缩质量75%）
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        single_image_size = len(buffer) / (1024 * 1024)  # 转换为MB
        
        # 计算总帧数
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        estimated_frames = total_frames // frame_interval
        
        return single_image_size * estimated_frames
    
    def _save_frame(self, args):
        """保存单帧图片的工作函��"""
        frame, saved_count = args
        
        # 检查图片相似度
        with self.lock:  # 使用锁确保线程安全
            is_similar, similarity = self.image_comparator.is_similar_to_last(frame)
            
        if not is_similar:
            output_path = os.path.join(
                self.output_dir, 
                f"frame_{saved_count:06d}.jpg"
            )
            encode_params = [
                cv2.IMWRITE_JPEG_QUALITY, 75,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1
            ]
            cv2.imwrite(output_path, frame, encode_params)
            return True
        return False
    
    def extract_frames(self, frame_interval: int = 1):
        if not self.cap:
            raise ValueError("视频未打开")
        
        frame_count = 0
        saved_count = 0
        frames_to_save = []
        
        # 重置图片比较器
        self.image_comparator.reset()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                    
                if frame_count % frame_interval == 0:
                    frames_to_save.append((frame.copy(), saved_count))
                    
                    # 当累积足够的帧时，批量提交处理
                    if len(frames_to_save) >= self.max_workers * 2:
                        results = list(executor.map(self._save_frame, frames_to_save))
                        saved_count += sum(1 for r in results if r)
                        frames_to_save = []
                
                frame_count += 1
            
            # 处理剩余的帧
            if frames_to_save:
                results = list(executor.map(self._save_frame, frames_to_save))
                saved_count += sum(1 for r in results if r)
        
        return saved_count
    
    def get_video_info(self) -> dict:
        """获取视频信息"""
        if not self.cap:
            raise ValueError("视频未打开")
            
        return {
            "total_frames": int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "fps": self.cap.get(cv2.CAP_PROP_FPS),
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        }