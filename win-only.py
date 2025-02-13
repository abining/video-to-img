import cv2
import os

# 创建输出文件夹
output_folder = 'out'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 获取目录中的所有视频文件
input_folder = './input'  # 替换成你的视频文件夹路径
video_files = [f for f in os.listdir(input_folder) if f.endswith(('.mp4', '.avi', '.mov'))]  # 你可以根据需要添加更多的视频格式

# 逐个处理视频文件
for video_file in video_files:
    video_path = os.path.join(input_folder, video_file)
    cap = cv2.VideoCapture(video_path)
    
    # 检查视频是否成功打开
    if not cap.isOpened():
        print(f"无法打开视频文件: {video_file}")
        continue
    
    # 获取视频的总帧数和帧率
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"正在处理视频: {video_file}，总帧数: {total_frames}，帧率: {fps}")
    
    # 逐帧读取并保存
    frame_number = 0
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # 构建保存帧的文件名
        output_filename = os.path.join(output_folder, f"{video_file}_frame_{frame_number:04d}.jpg")
        
        # 保存帧为图像文件
        cv2.imwrite(output_filename, frame)
        
        frame_number += 1
    
    # 释放视频捕捉对象
    cap.release()

print("视频帧截取完成！")
