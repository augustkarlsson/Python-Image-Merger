from PIL import Image, ImageOps

import os
import glob

def merge_images_in_folder(input_folder='images', output_folder='merged_images', final_size=(1100, 1700), border_size=59, border_color='white'):
    """
    Fetches all image files from the input_folder, and four at a time, runs the resize_and_merge function.
    If the number of image files isn't evenly divisible by four, the remaining spaces in the last merged image will be left white.

    Parameters:
        input_folder (str): Path to the folder containing the images.
        output_folder (str): Path to the folder where the merged images will be saved.
        final_size (tuple): Size of the final image (width, height). Defaults to (1100, 1700).
        border_size (int, optional): Border size in pixels. Defaults to 59 (roughly 0.5cm at 300DPI).
        border_color (str, optional): Border color. Defaults to 'white'.
    """
    # Get all image files from the directory
    image_paths = glob.glob(os.path.join(input_folder, '*'))

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    for i in range(0, len(image_paths), 4):
        # Get up to four image paths
        paths_slice = image_paths[i:i+4]

        # If there are less than four images, add white images to fill up the spaces
        while len(paths_slice) < 4:
            white_image = Image.new('RGB', final_size, border_color)
            white_image_path = os.path.join(output_folder, 'white_temp.jpg')
            white_image.save(white_image_path)
            paths_slice.append(white_image_path)
        
        # Generate the merged image
        merged_image = resize_and_merge(paths_slice, final_size, border_size, border_color)
        merged_image_path = os.path.join(output_folder, f'merged_{i//4}.jpg')
        merged_image.save(merged_image_path)

        # Remove the white image if it was created
        if len(paths_slice) < 4:
            os.remove(white_image_path)




def resize_and_merge(image_paths, final_size=(1100, 1700), border_size=59, border_color='white'):
    """
    Resize and merge four images into a single image with a border.

    Parameters:
        image_paths (list): List of paths to the images.
        final_size (tuple): Size of the final image (width, height). Defaults to (1100, 1700).
        border_size (int, optional): Border size in pixels. Defaults to 59 (roughly 0.5cm at 300DPI).
        border_color (str, optional): Border color. Defaults to 'white'.

    Returns:
        Image: New image combined from the four input images.
    """
    
    # Calculate quarter size minus the border
    quarter_size_single_border = ((final_size[0] - border_size) // 2, final_size[1] // 2)
    quarter_size_double_border = ((final_size[0] - 2 * border_size) // 2, (final_size[1] - border_size) // 2)
    
    # List to hold the processed images
    images = []
    
    for idx, image_path in enumerate(image_paths):
        with Image.open(image_path) as img:
            # Rotate the image if it's in landscape orientation
            if img.width > img.height:
                img = img.rotate(90, expand=True)

            # Determine appropriate quarter size based on image index
            quarter_size = quarter_size_double_border if idx % 2 else quarter_size_single_border

            # Calculate the factor to resize while maintaining aspect ratio
            width_ratio = quarter_size[0] / img.width
            height_ratio = quarter_size[1] / img.height
            resize_ratio = min(width_ratio, height_ratio)

            new_size = (int(img.width * resize_ratio), int(img.height * resize_ratio))

            # Resize the image and add the border
            img_resized = img.resize(new_size, Image.LANCZOS)
            
            # Determine appropriate border based on image index
            if idx % 2:
                img_with_border = ImageOps.expand(img_resized, border=(0, 0, border_size, border_size), fill=border_color)
            else:
                img_with_border = ImageOps.expand(img_resized, border=(0, 0, border_size, 0), fill=border_color)
            
            images.append(img_with_border)
    
    # Create a new blank image for the merge
    final_image = Image.new('RGB', final_size, border_color)

    # Paste the images into the final image
    final_image.paste(images[0], (0, 0))  # Top-left
    final_image.paste(images[1], (quarter_size_single_border[0] + border_size, 0))  # Top-right
    final_image.paste(images[2], (0, quarter_size_single_border[1]))  # Bottom-left
    final_image.paste(images[3], (quarter_size_single_border[0] + border_size, quarter_size_double_border[1] + border_size))  # Bottom-right

    return final_image



# Usage
merge_images_in_folder()


# # Usage
# image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg', 'image4.jpg']
# final_image = resize_and_merge(image_paths)
# final_image.show()
# final_image.save('merged_image.jpg')
