import os
import random
import shutil
import argparse

import psutil
import csv
import time

# Initialize global lists for memory usage and timestamps
memory_usage_stats = []
timestamps = []

def start_memory_monitoring(interval=1):
    """Starts monitoring memory usage in a separate thread."""
    def monitor():
        while True:
            memory_usage_stats.append(psutil.Process().memory_info().rss / 1024 ** 2)
            time.sleep(interval)
    import threading
    t = threading.Thread(target=monitor)
    t.daemon = True
    t.start()

def start_memory_monitoring(interval=1):
    """
    Starts monitoring the memory usage of the current process at specified intervals in a separate thread.

    Parameters
    ----------
    interval : int, optional
        The time interval, in seconds, between memory usage recordings. Default is 1 second.

    Notes
    -----
    This function initiates a background thread that continuously records the memory usage
    of the current process into the global list `memory_usage_stats`.
    """
    def monitor():
        while True:
            memory_usage_stats.append(psutil.Process().memory_info().rss / 1024 ** 2)
            time.sleep(interval)
    import threading
    t = threading.Thread(target=monitor)
    t.daemon = True
    t.start()

def record_event_duration(label, start_time):
    """
    Records the duration of an event by calculating the time elapsed since the start_time and
    appending the result to a global list `timestamps`.

    Parameters
    ----------
    label : str
        A label for the event whose duration is being recorded.
    start_time : float
        The timestamp (as returned by `time.time()`) at the beginning of the event.

    Notes
    -----
    This function calculates the duration of an event and appends a tuple containing the label and
    duration to the global list `timestamps`.
    """
    duration = time.time() - start_time
    timestamps.append((label, duration))

def write_to_csv(file_name, header, data):
    """
    Writes given data to a CSV file.

    Parameters
    ----------
    file_name : str
        Path to the CSV file where data will be written.
    header : list of str
        Column headers to be written in the CSV file.
    data : list of tuples
        Data rows, where each tuple corresponds to a row in the CSV.

    Notes
    -----
    This function creates (or overwrites) a CSV file and writes the headers and provided data rows to it.
    """
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)

def split_data(root_folder, train_ratio, val_ratio):
    """
    Splits image and label data into training, validation, and testing datasets based on provided ratios.

    Parameters
    ----------
    root_folder : str
        The root directory that contains the 'images' and 'labels' subdirectories.
    train_ratio : float
        The fraction of data to be used as the training set.
    val_ratio : float
        The fraction of data to be used as the validation set.

    Notes
    -----
    This function distributes image and label files from the 'images' and 'labels' directories
    into 'train', 'valid', and 'test' directories according to the specified ratios. It also
    starts memory monitoring and records the duration of the data splitting process.
    """
    start_memory_monitoring()
    start_time_main = time.time()
    # Paths to folders
    images_folder = os.path.join(root_folder, "images")
    labels_folder = os.path.join(root_folder, "labels")

    # Create new folders
    train_folder = os.path.join(root_folder, "train")
    val_folder = os.path.join(root_folder, "valid")
    test_folder = os.path.join(root_folder, "test")

    for folder in [train_folder, val_folder, test_folder]:
        os.makedirs(os.path.join(folder, "images"), exist_ok=True)
        os.makedirs(os.path.join(folder, "labels"), exist_ok=True)

    # Get filenames from "images" and "labels" folders
    image_files = os.listdir(images_folder)
    label_files = os.listdir(labels_folder)

    # Ensure there is a corresponding text file for each image file
    image_files = [file for file in image_files if file.replace(".jpg", ".txt") in label_files]

    # Random order of files
    random.shuffle(image_files)

    # Data split
    total_files = len(image_files)
    train_split = int(train_ratio * total_files)
    val_split = int(val_ratio * total_files)

    # Distribute files into corresponding folders
    for i, file in enumerate(image_files):
        source_img = os.path.join(images_folder, file)
        source_txt = os.path.join(labels_folder, file.replace(".jpg", ".txt"))

        if i < train_split:
            destination_folder = train_folder
        elif i < train_split + val_split:
            destination_folder = val_folder
        else:
            destination_folder = test_folder

        dest_img = os.path.join(destination_folder, "images", file)
        dest_txt = os.path.join(destination_folder, "labels", file.replace(".jpg", ".txt"))

        shutil.copyfile(source_img, dest_img)
        shutil.copyfile(source_txt, dest_txt)

    record_event_duration("Main", start_time_main)

    time_intervals = list(range(len(memory_usage_stats)))
    memory_data = list(zip(time_intervals, memory_usage_stats))
    #write_to_csv('memory_usage.csv', ['Time (s)', 'Memory Usage (MB)'], memory_data)
    #write_to_csv('timestamps.csv', ['Label', 'Duration (s)'], timestamps)