这是一个视频帧提取工具，可以提取视频中的帧，并保存为图片。

## 使用方法

1. 将视频文件放入input文件夹中
2. 运行main.py
3. 输入帧间隔，默认为1，即每帧都保存
4. 输入是否继续，默认为y，即继续
5. 等待处理完成，处理完成的图片会保存到output文件夹中

正常情况下，控制台会输出处理总结，包括处理完成的频数量，总共保存的图片数量，以及总输出大小。

![20241221174700](https://raw.githubusercontent.com/abining/picgo_imgs/main/images/20241221174700.png)

## 注意事项

1. 处理的视频数量较多时，可能会出现等待输入超时的情况，请耐心等待
2. 处理的视频数量较多时，可能会出现内存不足的情况，请耐心等待
3. 处理的视频数量较多时，可能会出现输出文件夹过大，请耐心等待

## 代码实现


### 使用到的第三方库介绍

```python
import cv2 # 导入opencv库,这个库的作用是处理视频帧，
import os
from typing import Optional
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
```
#### 1. cv2库

cv2库是opencv库的python接口，可以用来处理视频帧，可以通过如下的demo来了解cv2库的使用

```python
import cv2

# 打开视频文件
cap = cv2.VideoCapture('input/video.mp4')

# 读取视频帧
ret, frame = cap.read()
```

对视频帧的处理，可以参考如下的demo

```python
# 读取视频帧
ret, frame = cap.read()

# 显示视频帧
cv2.imshow('frame', frame)
```
####  os库介绍
os库是python标准库，可以用来处理文件和目录，可以通过如下的demo来了解os库的使用

```python
import os

# 获取当前工作目录
print(os.getcwd())
``` 

#### 3. typing库

typing库是python标准库，可以用来处理类型注解，可以通过如下的demo来了解typing库的使用

```python
from typing import Optional

# 定义一个函数，参数为可选类型
def add(a: Optional[int] = None, b: Optional[int] = None) -> Optional[int]:
    return a + b
```

#### 4. numpy库

numpy库是python标准库，可以用来处理数组，可以通过如下的demo来了解numpy库的使用

```python
import numpy as np

# 创建一个数组
a = np.array([1, 2, 3])
```

#### 5. concurrent.futures库

concurrent.futures库是python标准库，可以用来处理多线程，多进程，可以通过如下的demo来了解concurrent.futures库的使用

```python
from concurrent.futures import ThreadPoolExecutor

# 创建一个线程池
with ThreadPoolExecutor() as executor:
    # 提交任务
    future = executor.submit(task)
```

#### 6. threading库

threading库是python标准库，可以用来处理线程，可以通过如下的demo来了解threading库的使用

```python
from threading import Lock

# 创建一个锁
lock = Lock()
```

### 项目主要代码介绍

使用到了多进程，多线程，以及一些其他库，如果需要了解具体实现，请查看src文件夹中的代码。

#### 1. 视频帧提取

视频帧提取使用的是FFmpeg库，核心代码如下




#### 2. 图片保存

对于图片的保存，使用的是PIL库，核心代码如下

```python
from PIL import Image

def save_image(image, output_dir, frame_index):
    image.save(os.path.join(output_dir, f"frame_{frame_index}.jpg"))
```

PIL库的save方法，可以保存为jpg，png，bmp等格式，但是保存为jpg格式时，会丢失一部分图片信息，所以保存为jpg格式时，图片会变得模糊。






