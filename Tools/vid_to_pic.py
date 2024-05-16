from moviepy.editor import VideoFileClip
from moviepy.video.VideoClip import ImageClip
import os
from PIL import Image
import random
import time
import psutil
import csv

def monitor_memory(process, memory_usage):
    """
    Records the memory usage of the given process.

    Parameters
    ----------
    process : psutil.Process
        The process for which memory usage is to be monitored.
    memory_usage : list
        A list to which the memory usage data will be appended in megabytes.

    Notes
    -----
    The function appends the memory usage of the process in megabytes to the provided list.
    """
    memory_usage.append(process.memory_info().rss / 1024 ** 2)  # Memory usage in MB

def convert_video_to_images(input_source, output_folder, image_size):
    """
    Converts all video files from a directory to a sequence of images and records processing
    and memory usage statistics.

    Parameters
    ----------
    input_source : str
        The path to the directory containing video files or a single video file.
    output_folder : str
        The path to the directory where the output images and CSV files will be saved.
    image_size : str
        The size to which each image frame will be resized, specified as 'widthxheight'.

    Notes
    -----
    This function handles both directories and single video files. It extracts frames from
    each video file, processes them into images, resizes them if necessary, and saves them
    to the specified output directory. It also monitors memory usage and records processing
    times which are saved in CSV files in the output directory.
    """
    start_time = time.time()
    process = psutil.Process()
    memory_usage = []
    video_processing_stats = []

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if os.path.isdir(input_source):
        video_files = [f for f in os.listdir(input_source) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        for video_file in video_files:
            video_path = os.path.join(input_source, video_file)
            video_duration, processing_time = process_single_video(video_path, output_folder, image_size, process, memory_usage)
            video_processing_stats.append([video_file, video_duration, processing_time])
    else:
        video_duration, processing_time = process_single_video(input_source, output_folder, image_size, process, memory_usage)
        video_processing_stats.append(['Single Video', video_duration, processing_time])

    with open(os.path.join(output_folder, 'memory_usage.csv'), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time (s)', 'Memory Usage (MB)'])
        for i, usage in enumerate(memory_usage):
            writer.writerow([i, usage])

    with open(os.path.join(output_folder, 'video_processing_stats.csv'), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Video Name', 'Video Duration (s)', 'Processing Time (s)'])
        writer.writerows(video_processing_stats)

    end_time = time.time()
    print(f"Total processing completed in: {end_time - start_time} seconds.")

def process_single_video(input_video, output_folder, image_size, process, memory_usage):
    """
    Processes a single video file into images.

    Parameters
    ----------
    input_video : str
        The path to the video file.
    output_folder : str
        The directory where the output images will be stored.
    image_size : str
        The size to which each image frame will be resized, specified as 'widthxheight'.
    process : psutil.Process
        The process whose memory usage is to be monitored.
    memory_usage : list
        A list where the memory usage during video processing will be recorded.

    Returns
    -------
    tuple
        A tuple containing the video's duration in seconds and the time taken to process the video.

    Notes
    -----
    This function reads a video file, extracts frames at one frame per second, and saves each frame as an image.
    It also optionally resizes images, tracks memory usage, and measures processing time.
    """
    video_clip = VideoFileClip(input_video)
    video_start_time = time.time()
    video_duration = video_clip.duration

    for i, frame in enumerate(video_clip.iter_frames(fps=1, dtype='uint8')):
        monitor_memory(process, memory_usage)
        image_file = os.path.join(output_folder, f'{os.path.splitext(os.path.basename(input_video))[0]}_frame_{i + 1}.jpg')
        img_clip = ImageClip(frame)
        #if image_size:
            #img_clip = img_clip.resize(image_size)
        img_clip.save_frame(image_file, withmask=False)
        #create_random_cuts_and_scale(image_file, 2)

    video_clip.close()
    processing_time = time.time() - video_start_time
    return video_duration, processing_time

def create_random_cuts_and_scale(image_path, cuts):
    """
    Creates random crops from an image and scales them to a fixed size, saving the processed images.

    Parameters
    ----------
    image_path : str
        The path to the original image.
    cuts : int
        The number of random crops to create from the image.

    Notes
    -----
    This function opens an image, performs specified number of random cuts, resizes them, and saves them.
    The original image is then deleted.
    """
    with Image.open(image_path) as img:
        for _ in range(cuts):
            width, height = img.size
            x = random.randint(0, width - 300)
            y = random.randint(0, height - 300)
            cut = img.crop((x, y, x + 300, y + 300))
            cut = cut.resize((300, 300))
            cut_file_name = f'{os.path.splitext(image_path)[0]}_cut_scaled_{x}_{y}.jpg'
            cut.save(cut_file_name)
    os.remove(image_path)

convert_video_to_images(r"C:\Users\mikra\OneDrive\Desktop\Foto\labor.mp4", r"C:\Users\mikra\OneDrive\Desktop\Foto", "848x480")
