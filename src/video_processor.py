import cv2 # 导入opencv库,这个库的作用是处理视频帧，
import os
from typing import Optional
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

class VideoProcessor:
    def __init__(self, input_path: str, output_dir: str, max_workers: int = 4):
        self.input_path = input_path
        self.output_dir = output_dir
        self.cap = None
        self.max_workers = max_workers
        self.lock = Lock()
        
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
        """保存单帧图片的工作函数"""
        frame, saved_count = args
        output_path = os.path.join(
            self.output_dir, 
            f"frame_{saved_count:06d}.jpg"
        )
        # 优化JPEG压缩参数
        encode_params = [
            cv2.IMWRITE_JPEG_QUALITY, 75,
            cv2.IMWRITE_JPEG_OPTIMIZE, 1
        ]
        cv2.imwrite(output_path, frame, encode_params)
    
    def extract_frames(self, frame_interval: int = 1):
        if not self.cap:
            raise ValueError("视频未打开")
        
        frame_count = 0
        saved_count = 0
        frames_to_save = []
        
        # 使用线程池处理图片保存
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                    
                if frame_count % frame_interval == 0:
                    frames_to_save.append((frame.copy(), saved_count))
                    saved_count += 1
                    
                    # 当累积足够的帧时，批量提交处理
                    if len(frames_to_save) >= self.max_workers * 2:
                        executor.map(self._save_frame, frames_to_save)
                        frames_to_save = []
                
                frame_count += 1
            
            # 处理剩余的帧
            if frames_to_save:
                executor.map(self._save_frame, frames_to_save)
        
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