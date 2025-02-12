import cv2
import os

def extract_frames():
    # 创建输出目录
    if not os.path.exists('output'):
        os.makedirs('output')
    
    # 获取输入视频文件
    input_dir = 'input'
    video_files = [f for f in os.listdir(input_dir) if f.endswith(('.mp4', '.avi', '.mov'))]
    
    for video_file in video_files:
        # 打开视频
        video_path = os.path.join(input_dir, video_file)
        cap = cv2.VideoCapture(video_path)
        
        # 创建视频对应的输出目录
        video_name = os.path.splitext(video_file)[0]
        output_path = os.path.join('output', video_name)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # 读取并保存帧
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # 保存帧
            output_file = os.path.join(output_path, f'frame_{frame_count:06d}.jpg')
            cv2.imwrite(output_file, frame)
            frame_count += 1
        
        cap.release()
        print(f'已处理视频 {video_file}，共提取 {frame_count} 帧')

if __name__ == '__main__':
    extract_frames()
