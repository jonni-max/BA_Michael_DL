import cv2


def draw_boxes(image_path, label_path, output_path):
    """
    Draws bounding boxes on an image based on label information and saves the modified image.

    This function reads an image from a specified path, processes bounding box coordinates
    and class identifiers from a label file, and draws these boxes on the image. Each box
    is labeled with a class identifier. The resulting image is saved to a new file.

    Parameters
    ----------
    image_path : str
        The file path of the image on which bounding boxes will be drawn.
    label_path : str
        The file path of the text file containing labels and bounding box coordinates. Each
        line in the file should contain five space-separated values: class_id, x_center,
        y_center, width, and height (all normalized to [0, 1]).
    output_path : str
        The file path where the image with drawn bounding boxes will be saved.

    Raises
    ------
    Exception
        If an error occurs during file handling or during the processing of the image or labels.

    """

    try:
        # Read the image
        image = cv2.imread(image_path)

        # Get the dimensions of the image
        img_height, img_width, _ = image.shape

        # Read the label file
        with open(label_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            try:
                # Split values in the line
                class_id, x, y, width, height = map(float, line.strip().split())

                # Convert normalized coordinates to pixel coordinates
                x_pixel = int(x * img_width)
                y_pixel = int(y * img_height)
                width_pixel = int(width * img_width)
                height_pixel = int(height * img_height)

                # Draw the bounding box on the image
                cv2.rectangle(image, (x_pixel - width_pixel // 2, y_pixel - height_pixel // 2),
                              (x_pixel + width_pixel // 2, y_pixel + height_pixel // 2),
                              color=(0, 255, 0), thickness=2)

                # Optionally add the class name
                class_name = f"Class {int(class_id)}"
                cv2.putText(image, class_name, (x_pixel, y_pixel - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            except Exception as e:
                print(f"Error processing the line: {e}")
                continue

        # Save the output image
        print("Saving")
        print("test")
        cv2.imwrite(output_path, image)

    except Exception as e:
        print(f"Error processing files: {e}")



files = '/Users/michaelkravt/PycharmProjects/BA_Repo/Tools/MainDir/TestDir/images'

for i in range(len(files)):
    # Beispielaufruf
    image_path = f'C:/Users/mikra/OneDrive/Desktop/Foto/syn_data/{i}.jpg'
    label_path = f'C:/Users/mikra/OneDrive/Desktop/Foto/syn_data/labels/{i}.txt'
    output_path = f'C:/Users/mikra/OneDrive/Desktop/Foto/syn_data/outputoutput_{i}.jpg'

    draw_boxes(image_path, label_path, output_path)
