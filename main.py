import os
import sys
import select
import time
from src.video_processor import VideoProcessor
from multiprocessing import Pool

def input_with_timeout(prompt, timeout=10):
    """带超时的输入函数"""
    print(prompt, end='', flush=True)
    
    if os.name == 'nt':
        import msvcrt
        start_time = time.time()
        input_str = ''
        while True:
            if msvcrt.kbhit():
                char = msvcrt.getwche()
                if char == '\r':
                    print()
                    break
                input_str += char
            if time.time() - start_time > timeout:
                print('\n等待输入超时！')
                return None
            time.sleep(0.1)
        return input_str
    else:
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            return sys.stdin.readline().strip()
        print('\n等待输入超时！')
        return None

def get_video_files(input_dir):
    """获取输入目录中的所有视频文件"""
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
    video_files = []
    
    for file in os.listdir(input_dir):
        if file.lower().endswith(video_extensions):
            video_files.append(file)
    
    return video_files

def process_video(input_path, output_dir, frame_interval):
    """处理单个视频文件"""
    # 获取视频文件名（不含扩展名）
    video_name = os.path.splitext(os.path.basename(input_path))[0]
    
    # 创建以视频名称命名的输出目录
    video_output_dir = os.path.join(output_dir, video_name)
    
    with VideoProcessor(input_path, video_output_dir) as processor:
        # 获取视频信息
        video_info = processor.get_video_info()
        print(f"\n处理视频：{video_name}")
        print("视频信息：")
        print(f"总帧数：{video_info['total_frames']}")
        print(f"FPS：{video_info['fps']}")
        print(f"分辨率：{video_info['width']}x{video_info['height']}")
        
        # 估算输出大小
        estimated_size = processor.estimate_output_size(frame_interval)
        print(f"预计输出图片总大小：{estimated_size:.2f} MB")
        
        # 提取帧
        print("开始处理...")
        saved_frames = processor.extract_frames(frame_interval)
        print(f"处理完成！共保存了 {saved_frames} 张图片")
        print(f"输出目录：{video_output_dir}")
        
        return saved_frames, estimated_size

def main():
    # 配置路径
    input_dir = "input"
    output_dir = "output"
    
    # 确保输入目录存在
    if not os.path.exists(input_dir):
        print(f"错误：找不到输入目录 {input_dir}")
        return
    
    # 获取所有视频文件
    video_files = get_video_files(input_dir)
    
    if not video_files:
        print(f"错误：在 {input_dir} 目录中没有找到视频文件")
        return
    
    print(f"找到 {len(video_files)} 个视频文件：")
    for i, file in enumerate(video_files, 1):
        print(f"{i}. {file}")
    
    # 设置帧间隔（带10秒超时）
    frame_interval_str = input_with_timeout("\n请输入帧间隔（默认为1，10秒内未输入将取消操作）：", 10)
    
    if frame_interval_str is None:
        print("操作已取消")
        return
        
    frame_interval = int(frame_interval_str or "1")
    
    # 创建进程池处理多个视频
    with Pool() as pool:
        # 准备处理参数
        process_args = [(
            os.path.join(input_dir, video_file),
            output_dir,
            frame_interval
        ) for video_file in video_files]
        
        # 并行处理所有视频
        results = pool.starmap(process_video, process_args)
    
    # 汇总结果
    total_frames = sum(frames for frames, _ in results)
    total_estimated_size = sum(size for _, size in results)
    
    # 输出总结
    print("\n处理总结：")
    print(f"处理完成的视频数量：{len(video_files)}")
    print(f"总共保存的图片数量：{total_frames}")
    print(f"总输出大小：{total_estimated_size:.2f} MB")
    print(f"所有图片都已保存到各自的文件夹中：{output_dir}")

if __name__ == "__main__":
    main()