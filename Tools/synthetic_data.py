# Import necessary libraries
from PIL import Image
import pyvista as pv
import numpy as np
import os
import argparse

import psutil
import csv
import time

# Initialize global lists for memory usage and timestamps
memory_usage_stats = []
timestamps = []

def start_memory_monitoring(interval=1):
    """
    Starts monitoring memory usage of the current process at regular intervals in a separate thread.

    Parameters
    ----------
    interval : int, optional
        The time interval, in seconds, between recordings of memory usage. Default is 1 second.
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
    Records the duration of an event, appending the result to a global list.

    Parameters
    ----------
    label : str
        A descriptive name for the event being timed.
    start_time : float
        The start time of the event, typically obtained via `time.time()`.
    """
    duration = time.time() - start_time
    timestamps.append((label, duration))

def write_to_csv(file_name, header, data):
    """
    Writes specified data to a CSV file.

    Parameters
    ----------
    file_name : str
        The path where the CSV file will be created.
    header : list of str
        The headers for the CSV file.
    data : list of tuples
        The data to be written into the CSV file, where each tuple represents a row.
    """
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)


def generate_random_rotation_matrix():
    """
    Generate a random 3D rotation matrix.

    Returns
    -------
    np.ndarray
        A 4x4 ndarray representing a random rotation matrix.

    Notes
    -----
    This function generates random rotation angles for the x, y, and z axes within specified ranges
    and computes the corresponding rotation matrices for each axis. These matrices are then
    multiplied together to form a final rotation matrix which represents a composite rotation
    about all three axes. The function also records the duration of the matrix generation process.
    """
    start_time_matrix = time.time()

    # Define the maximum rotation angle for x and y axes
    i = np.pi / 4
    angle_x = np.random.uniform(-i, i)
    angle_y = np.random.uniform(-i, i)
    angle_z = np.random.uniform(0, 2 * np.pi)  # Full rotation range for z-axis

    # Rotation matrix along x-axis
    rotation_matrix_x = np.array([
        [1, 0, 0, 0],
        [0, np.cos(angle_x), -np.sin(angle_x), 0],
        [0, np.sin(angle_x), np.cos(angle_x), 0],
        [0, 0, 0, 1]
    ])

    # Rotation matrix along y-axis
    rotation_matrix_y = np.array([
        [np.cos(angle_y), 0, np.sin(angle_y), 0],
        [0, 1, 0, 0],
        [-np.sin(angle_y), 0, np.cos(angle_y), 0],
        [0, 0, 0, 1]
    ])

    # Rotation matrix along z-axis
    rotation_matrix_z = np.array([
        [np.cos(angle_z), -np.sin(angle_z), 0, 0],
        [np.sin(angle_z), np.cos(angle_z), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    # Combine the rotation matrices to get the final rotation matrix
    final_rotation_matrix = np.dot(rotation_matrix_z, np.dot(rotation_matrix_y, rotation_matrix_x))

    record_event_duration("Generate_Matrix", start_time_matrix)
    return final_rotation_matrix


# Function to create a label file with bounding box information
def create_label_file(label_path, class_id, x_center, y_center, width, height, bg_width, bg_height):
    """
    Create a label file with bounding box information.

    Args:
        label_path (str): Path to the label file.
        class_id (int): Class ID.
        x_center (float): X-coordinate of the bounding box center.
        y_center (float): Y-coordinate of the bounding box center.
        width (float): Width of the bounding box.
        height (float): Height of the bounding box.
        bg_width (int): Width of the background image.
        bg_height (int): Height of the background image.
    """
    start_time_label = time.time()
    # Normalize coordinates and dimensions
    x_min_normalized = x_center / bg_width
    y_min_normalized = y_center / bg_height
    width_normalized = width / bg_width
    height_normalized = height / bg_height

    # Write the normalized bounding box information to the label file
    with open(label_path, 'a') as f:
        f.write(f"{class_id} {x_min_normalized} {y_min_normalized} {width_normalized} {height_normalized}\n")

    record_event_duration("Create_Labelfile", start_time_label)



# Main function to generate synthetic images with labeled bounding boxes
def synthetic_data_generator(stl_path, images_folder, final_image_path, final_label_path):
    """
    Generates synthetic images with labeled bounding boxes from STL files.

    Parameters
    ----------
    stl_path : str
        Path to the directory containing STL files.
    images_folder : str
        Path to the directory containing background images.
    final_image_path : str
        Path to the directory where synthetic images will be saved.
    final_label_path : str
        Path to the directory where label files will be saved.

    Notes
    -----
    This function processes each STL file by applying a random rotation, rendering the model,
    and then compositing it onto a background image from `images_folder`. Labels for bounding
    boxes are saved in `final_label_path`. Memory usage and event durations are recorded and
    can be written to CSV files.
    """

    temp_folder = "temp"
    os.makedirs(temp_folder)

    stl_files = []

    for stl_file in os.listdir(stl_path):
        if stl_file.endswith('.stl'):
            path = os.path.join(stl_path, stl_file)
            stl_files.append(path)

    print(stl_files)

    # Iterate over images in the specified folder
    for i, image_file in enumerate(os.listdir(images_folder)):  # Hintergrundbilder
        try:
            start_time_main = time.time()
            start_memory_monitoring()  # Start memory monitoring
            # Check if the file is an image (PNG or JPG)
            if image_file.endswith(".png") or image_file.endswith(".jpg"):
                image_path = os.path.join(images_folder, image_file)
                ##P
                # Open the background image and get width and height of it
                background_image = Image.open(image_path)
                bg_width, bg_height = background_image.size

                avg_width = 0
                avg_height = 0
                ##
                # Iterate over STL files
                start_time_rend = time.time()
                for j, your_stl_file in enumerate(stl_files):

                    try:
                        # Read STL file and apply a random rotation
                        mesh = pv.read(os.path.join(your_stl_file))
                        rotation_matrix = generate_random_rotation_matrix()
                        mesh.transform(rotation_matrix)

                        # Create a PyVista plotter for visualization
                        if j == 2:
                            plotter = pv.Plotter(off_screen=True)
                            plotter.add_mesh(mesh, color='#343430', show_edges=False)
                        else:
                            plotter = pv.Plotter(off_screen=True)
                            plotter.add_mesh(mesh, color='white', show_edges=False)

                        # Set the camera position for the plotter
                        plotter.camera_position = [(0, 0, -2 * mesh.length), (0, 0, 0), (0, 1, 0)]

                        ##Papa geändert
                        if "lid" in your_stl_file:
                            scaling_factor = np.random.uniform(0.22, 0.3)
                        else:
                            scaling_factor = np.random.uniform(0.05, 0.22)

                        scaled_width = int(plotter.window_size[0] * scaling_factor)
                        scaled_height = int(plotter.window_size[1] * scaling_factor)
                        avg_width += scaled_width
                        avg_height += scaled_height
                        ##

                        # Save a screenshot of the scene
                        screenshot_path = f'{temp_folder}/{j}.png'
                        plotter.screenshot(screenshot_path, transparent_background=True,
                                           window_size=(scaled_width, scaled_height))
                        plotter.close()
                    except Exception as e:
                        print(f"Fehler beim Verarbeiten der STL-Datei {your_stl_file}: {e}")
                        continue
                record_event_duration("Rend_Obj", start_time_rend)

                ##P, geteilt durch 2 wegen leerem Bereich im Screenshot
                avg_width = int(avg_width / (j + 1) / 2)
                avg_height = int(avg_height / (j + 1) / 2)
                grid_horisontal = int(bg_width / avg_width)
                grid_vertical = int(bg_height / avg_height)
                matrix = []
                start_time_get_positions = time.time()
                for v in range(grid_vertical):
                    row = []
                    for h in range(grid_horisontal):
                        x = int(avg_width / 2) + h * avg_width
                        y = int(avg_height / 2) + v * avg_height
                        matrix.append((x, y))

                record_event_duration("Get_Positions", start_time_get_positions)

                # Iterate over generated screenshots
                for x, screenshot_path in enumerate(os.listdir(temp_folder)):
                    start_time_place = time.time()
                    print("- - - - -")
                    try:
                        rotated_image_path = screenshot_path
                        rotated_image = Image.open(f'{temp_folder}/{rotated_image_path}')
                        file_name = os.path.basename(rotated_image_path)

                        # Randomly choose a position to paste the rotated image
                        # on the background
                        random_index = np.random.randint(0, len(matrix))
                        # center point
                        random_position = matrix[random_index]
                        paste_position = int(random_position[0] - rotated_image.size[0] / 2), int(
                            random_position[1] - rotated_image.size[1] / 2)

                        # Paste the rotated image onto the background
                        background_image.paste(rotated_image, paste_position, rotated_image)

                        # Save the final image
                        background_image.save(f'{final_image_path}/{i}.jpg')

                        # Create label file path and determine class ID based
                        # on the filename
                        output_dir = final_label_path
                        label_path = os.path.join(output_dir, f"{i}.txt")
                        class_id = file_name.replace(".png", "")

                        # Calculate the center coordinates and dimensions of
                        # the bounding box
                        x_center, y_center = random_position
                        width, height = rotated_image.size[0] / 2, rotated_image.size[0] / 2

                        # Create the label file with bounding box information
                        create_label_file(label_path, class_id, x_center, y_center, width, height, bg_width, bg_height)

                        # Remove the temporary rotated image file
                        os.remove(f'{temp_folder}/{rotated_image_path}')
                        del matrix[random_index]
                    except Exception as e:
                        # Remove the temporary rotated image file in case of an
                        # error
                        os.remove(f'{temp_folder}/{rotated_image_path}')
                        print(f"Fehler beim Verarbeiten des Bildes {image_file}: {e}")
                        continue
                    record_event_duration("Place_Objects", start_time_place)

                ##
                ## Open the background image and resize it
                # background_image = Image.open(image_path)
                # bg_width, bg_height = background_image.size
                # target_size = (1920, 1080)
                # background_image = background_image.resize(target_size)

                print(f"Verarbeite Bild {i + 1}: {image_path}")
        except Exception as e:
            print(f"Fehler beim Verarbeiten des Bildes {image_file}: {e}")
            continue

        record_event_duration("Main", start_time_main)

        time_intervals = list(range(len(memory_usage_stats)))
        memory_data = list(zip(time_intervals, memory_usage_stats))
        write_to_csv('memory_usage.csv', ['Time (s)', 'Memory Usage (MB)'], memory_data)
        write_to_csv('timestamps.csv', ['Label', 'Duration (s)'], timestamps)

synthetic_data_generator(r"C:\GitHub\BA_Repo\data\stl_files",
                         r"C:\Users\mikra\OneDrive\Desktop\Foto",
                         r"C:\Users\mikra\OneDrive\Desktop\Foto\syn_data",
                         r"C:\Users\mikra\OneDrive\Desktop\Foto\syn_data\labels")


# python synthetic_data.py --stl_files /Users/michaelkravt/PycharmProjects/BA_Repo/resources/stl_files/sun_c.stl /Users/michaelkravt/PycharmProjects/BA_Repo/resources/stl_files/planet_c.stl /Users/michaelkravt/PycharmProjects/BA_Repo/resources/stl_files/planet_c.stl /Users/michaelkravt/PycharmProjects/BA_Repo/resources/stl_files/lid_c.stl --output /Users/michaelkravt/PycharmProjects/BA_Repo/Tools/MainDir/TestDir/images --label /Users/michaelkravt/PycharmProjects/BA_Repo/Tools/MainDir/TestDir/labels --temp /Users/michaelkravt/PycharmProjects/BA_Repo/Tools/MainDir/TestDir/temp --images_folder /Users/michaelkravt/PycharmProjects/BA_Repo/Tools/MainDir/TestDir
