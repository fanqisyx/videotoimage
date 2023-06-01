import cv2
import os
import datetime
import time
import pytesseract
from PIL import Image
import concurrent.futures
import chardet
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import concurrent.futures
from tkinter import ttk


time_interval = 1.0  # 默认时间间隔为1秒
num_threads = 6  # 默认线程数为1



def select_video_folder():
    folder_path = filedialog.askdirectory()
    video_folder_entry.delete(0, tk.END)
    video_folder_entry.insert(0, folder_path)

def select_output_folder():
    folder_path = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, folder_path)

def set_time_interval():
    try:
        new_interval = float(time_interval_entry.get())
        if new_interval <= 0:
            raise ValueError
        global time_interval
        time_interval = new_interval
    except ValueError:
        messagebox.showerror("Error", "Invalid time interval. Please enter a positive numeric value.")

def process_videos2_wrapper():
    global progress_var, progress_label

    # 重置进度条和标签
    progress_var.set(0)
    progress_label.config(text="Processed Videos: 0")

    video_folder = video_folder_entry.get()
    output_folder = output_folder_entry.get()

    if not video_folder or not output_folder:
        messagebox.showerror("Error", "Please select video folder and output folder.")
        return

    process_videos2(video_folder, output_folder)


def extract_frames(video_path, output_path):
    # 打开视频文件
    video = cv2.VideoCapture(video_path)

    # 确定帧速率
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"(fps:{fps})total_frames: {total_frames}")
    # 初始化计数器和当前时间点
    count = 0
    current_time = 0
    time_elapsed = 0
    #cv2.namedWindow('ROI Image', cv2.WINDOW_NORMAL)
    while True:
        if time_elapsed >= time_interval:
            start_time = time.perf_counter()
            # 跳到下一秒的帧
            target_frame =count# int((current_time + 1) * fps)
            video.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

            # 读取一帧图像
            ret, frame = video.read()
            #print(frame)
            if not ret:
                break
            if count > total_frames:
                break


            # 计算当前时间点
            #current_time = count / fps

            # 取整到最近的一秒
            #current_time = round(current_time)

            # 转换为时间对象
            #time_obj = datetime.datetime.fromtimestamp(current_time)

            # 格式化时间点为字符串（时-分-秒-毫秒）
            #time_str = time_obj.strftime('%H-%M-%S-%f')[:-3]




            # 提取左上角区域（根据实际情况调整坐标和大小）



            #print(f"result: {result} (time_str {time_str})")
            Videofile_name = os.path.splitext(os.path.basename(video_path))[0]
            if not os.path.exists(output_path + '/' + Videofile_name):
                os.makedirs(output_path + '/' + Videofile_name)

            # 保存图像
            filename = output_path + '/' + Videofile_name+'/' + Videofile_name + "__count_{:06d}.jpg".format(count)
            current_time1 = datetime.datetime.now()
            print(f"(count:{count} current_time1:{current_time1})filename: {filename}")
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            time_elapsed = 0

        count += 1
        time_elapsed += (1 / fps)

    # 释放视频对象
    video.release()
    #cv2.destroyAllWindows()

def process_videos2(folder_path, output_folder):
    # 遍历文件夹中的文件和子文件夹
    total_videos = len(
        [filename for filename in os.listdir(folder_path) if filename.endswith('.mp4') or filename.endswith('.avi')])
    processed_videos = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            if os.path.isfile(file_path):
                # 处理视频文件
                if filename.endswith('.mp4') or filename.endswith('.avi'):
                    #output_path = os.path.join(output_folder, os.path.splitext(filename)[0])
                    future = executor.submit(extract_frames, file_path, output_folder)
                    futures.append(future)

            elif os.path.isdir(file_path):
                # 递归处理子文件夹
                #subfolder_output = os.path.join(output_folder, filename)
                #os.makedirs(subfolder_output, exist_ok=True)
                process_videos2(file_path, output_folder)

            processed_videos += 1
            update_progress(processed_videos / total_videos * 100)

def update_progress(progress):
    # 更新进度条的值
    progress_var.set(progress)

    # 更新标签显示总共处理了多少视频
    progress_label.config(text=f"Processed Videos: {progress}")

def show_help():
    help_text = """这是一个视频分解软件，用于将视频文件分解为帧图像。

使用方法：
1. 在视频文件夹路径和输出文件夹路径的输入框中输入相应的路径。
2. 设置时间间隔（可选），单位为秒，可以是0.5秒等小数。
3. 点击转换按钮开始分解视频。

注意事项：
- 视频文件夹路径应该是包含要处理的视频文件的文件夹路径（只查找mp4和avi文件）。
- 输出文件夹路径用于存储生成的帧图像。
- 输出的文件会在选择的文件夹中创建新文件夹，文件夹名称与视频本身的名称相同，有多少视频文件就会创建多少文件夹。
- 时间间隔表示每个帧图像之间的时间间隔，单位为秒，浮点数。

如有问题，请联系我们的技术支持。"""

    messagebox.showinfo("帮助", help_text)


def set_num_threads():
    global num_threads
    num_threads = int(num_threads_entry.get())
    messagebox.showinfo("成功", f"线程数已设置为 {num_threads}")


# 视频文件夹路径
# Create the main window
window = tk.Tk()
window.title("Video Converter")
progress_var = tk.DoubleVar()

# Video Folder
video_folder_label = tk.Label(window, text="Video Folder:")
video_folder_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

video_folder_entry = tk.Entry(window, width=50)
video_folder_entry.grid(row=0, column=1, padx=10, pady=5)

video_folder_button = tk.Button(window, text="Browse", command=select_video_folder)
video_folder_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")

# Output Folder
output_folder_label = tk.Label(window, text="Output Folder:")
output_folder_label.grid(row=1, column=0,padx=10, pady=5, sticky="e")

output_folder_entry = tk.Entry(window, width=50)
output_folder_entry.grid(row=1, column=1, padx=10, pady=5)

output_folder_button = tk.Button(window, text="Browse", command=select_output_folder)
output_folder_button.grid(row=1, column=2, padx=5, pady=5, sticky="e")

# Time Interval
time_interval_label = tk.Label(window, text="Time Interval (seconds):")
time_interval_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

time_interval_entry = tk.Entry(window, width=10)
time_interval_entry.insert(0, str(time_interval))
time_interval_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

set_interval_button = tk.Button(window, text="Set", command=set_time_interval)
set_interval_button.grid(row=2, column=2, padx=5, pady=5, sticky="e")

# # Time Interval Note
# time_interval_note = tk.Label(window, text="Enter the time interval between frames in seconds.")
# time_interval_note.grid(row=2, column=2, columnspan=1, padx=10, pady=5, sticky="w")

# 线程数输入框
num_threads_label = tk.Label(window, text="线程数:")
num_threads_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")

num_threads_entry = tk.Entry(window, width=10)
num_threads_entry.insert(0, str(num_threads))
num_threads_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

# 设置线程数按钮
set_num_threads_button = tk.Button(window, text="设置", command=set_num_threads)
set_num_threads_button.grid(row=4, column=2, padx=5, pady=5, sticky="e")

# # 线程数说明标签
# num_threads_note = tk.Label(window, text="请输入要使用的线程数。")
# num_threads_note.grid(row=6, column=1, columnspan=2, padx=10, pady=5, sticky="w")


# 创建进度条
progress_bar = ttk.Progressbar(window, variable=progress_var, maximum=100)
progress_bar.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky="we")

# 创建一个标签显示总共处理了多少视频
progress_label = tk.Label(window, text="Processed Videos: 0")
progress_label.grid(row=6, column=0, columnspan=3, padx=10, pady=5)


# 创建帮助按钮
help_button = tk.Button(window, text="帮助", command=show_help)
help_button.grid(row=7, column=0, columnspan=1, padx=10, pady=5)

# Convert Button
convert_button = tk.Button(window, text="Convert", command=process_videos2_wrapper)
convert_button.grid(row=7, column=2, columnspan=1, padx=10, pady=10)



# Start the main loop
window.mainloop()