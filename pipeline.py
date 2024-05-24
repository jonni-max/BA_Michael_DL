from tools.vid_to_pic import convert_video_to_images
from tools.synthetic_data import synthetic_data_generator
from tools.split_data import split_data
import argparse
import os

def main():
    # Parse arguments for the integrated script
    parser = argparse.ArgumentParser(description='Process videos into synthetic data and split the data.')
    parser.add_argument('--video_source', required=True, help='Path to the input video file or folder.')
    parser.add_argument('--stl_files', nargs="+", help='List of STL files for synthetic data generation.')
    parser.add_argument('--temp_folder', help='Path to the temporary folder for intermediate data.')
    parser.add_argument('--output', required=True, help='Path to the final output folder.')
    parser.add_argument('--train_ratio', type=float, default=0.7, help='Percentage of data for the training set.')
    parser.add_argument('--val_ratio', type=float, default=0.25, help='Percentage of data for the validation set.')
    args = parser.parse_args()

    # Video to Image conversion
    images_folder = os.path.join(args.temp_folder, 'images')
    convert_video_to_images(args.video_source, images_folder, image_size=None)  # Image size can be added as an argument if needed

    # Synthetic Data Generation
    synthetic_data_args = argparse.Namespace(
        stl_files=args.stl_files,
        images_folder=images_folder,
        output=args.output,
        label=os.path.join(args.output, 'labels'),
        temp_folder=args.temp_folder
    )
    synthetic_data_generator(synthetic_data_args)

    split_data(args.output, args.train_ratio, args.val_ratio)

if __name__ == "__main__":
    main()
