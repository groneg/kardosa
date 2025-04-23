import cv2
import numpy as np
import os
from flask import current_app

# Default Constants (can be overridden by parameters)
DEFAULT_BLUR_KERNEL = (5, 5)
DEFAULT_CANNY_LOW = 50
DEFAULT_CANNY_HIGH = 150
DEFAULT_MIN_CARD_AREA_RATIO = 0.01
DEFAULT_MAX_CARD_AREA_RATIO = 0.15
DEFAULT_CARD_ASPECT_RATIO_MIN = 0.6
DEFAULT_CARD_ASPECT_RATIO_MAX = 0.85
DEFAULT_APPROX_POLY_EPSILON = 0.02
DEFAULT_ROW_TOLERANCE_RATIO = 0.1 # Ratio of image height

def split_binder_page(image_path, output_dir,
                      blur_kernel=DEFAULT_BLUR_KERNEL,
                      canny_low=DEFAULT_CANNY_LOW, canny_high=DEFAULT_CANNY_HIGH,
                      min_area_ratio=DEFAULT_MIN_CARD_AREA_RATIO, max_area_ratio=DEFAULT_MAX_CARD_AREA_RATIO,
                      aspect_min=DEFAULT_CARD_ASPECT_RATIO_MIN, aspect_max=DEFAULT_CARD_ASPECT_RATIO_MAX,
                      poly_epsilon=DEFAULT_APPROX_POLY_EPSILON,
                      row_tolerance_ratio=DEFAULT_ROW_TOLERANCE_RATIO,
                      save_debug_image=True): # Add flag to save debug image
    """Splits a binder page image into individual card images using configurable parameters.

    Args:
        image_path (str): Path to the input binder page image.
        output_dir (str): Directory to save the extracted card images.
        blur_kernel (tuple): Kernel size for Gaussian Blur (e.g., (5, 5)).
        canny_low (int): Lower threshold for Canny edge detection.
        canny_high (int): Higher threshold for Canny edge detection.
        min_area_ratio (float): Minimum contour area relative to total image area.
        max_area_ratio (float): Maximum contour area relative to total image area.
        aspect_min (float): Minimum width/height aspect ratio for cards.
        aspect_max (float): Maximum width/height aspect ratio for cards.
        poly_epsilon (float): Epsilon factor for cv2.approxPolyDP.
        row_tolerance_ratio (float): Ratio of image height used for sorting tolerance.
        save_debug_image (bool): Whether to save an image with contours drawn.

    Returns:
        list: A list of file paths for the extracted card images.
    """
    extracted_card_paths = []
    debug_img = None # Initialize debug image
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not load image from {image_path}")
            return []
        debug_img = img.copy() # Copy for drawing contours

        img_height, img_width = img.shape[:2]
        total_area = img_width * img_height

        # --- Preprocessing ---
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, blur_kernel, 0)
        edged = cv2.Canny(blurred, canny_low, canny_high)

        # --- Find Contours ---
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        card_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            area_ratio = area / total_area

            # --- Filter by Area ---
            if min_area_ratio < area_ratio < max_area_ratio:
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, poly_epsilon * perimeter, True)

                # --- Filter by Shape ---
                if len(approx) == 4:
                    (x, y, w, h) = cv2.boundingRect(approx)
                    # Avoid division by zero if height is 0
                    aspect_ratio = float(w) / h if h > 0 else 0

                    # --- Filter by Aspect Ratio ---
                    if aspect_min < aspect_ratio < aspect_max:
                        card_contours.append(approx)
                        # Draw accepted contour on debug image
                        cv2.drawContours(debug_img, [approx], -1, (0, 255, 0), 2)
                    # else: # Optional: Draw rejected aspect ratio contours in different color
                    #     cv2.drawContours(debug_img, [approx], -1, (0, 0, 255), 1)
                # else: # Optional: Draw rejected shape contours
                #     cv2.drawContours(debug_img, [approx], -1, (255, 0, 0), 1)
            # else: # Optional: Draw rejected area contours
            #     cv2.drawContours(debug_img, [contour], -1, (0, 255, 255), 1)


        # --- Sort Contours ---
        if len(card_contours) > 0:
            bounding_boxes = [cv2.boundingRect(c) for c in card_contours]
            row_tolerance = img_height * row_tolerance_ratio
            # Sort primarily by y-center, then x-center
            # Use tuple unpacking directly in lambda for clarity
            sorted_contours = sorted(zip(card_contours, bounding_boxes),
                                   key=lambda item: (
                                       round((item[1][1] + item[1][3]/2) / row_tolerance),
                                       item[1][0] + item[1][2]/2
                                   ))

            # Limit to top 9 contours
            print(f"Found {len(sorted_contours)} valid card contours before limiting.")
            sorted_contours = sorted_contours[:9]

            # --- Extract and Save ROIs ---
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            for i, (contour, (x, y, w, h)) in enumerate(sorted_contours):
                padding = 2
                y_start = max(0, y - padding)
                y_end = min(img_height, y + h + padding)
                x_start = max(0, x - padding)
                x_end = min(img_width, x + w + padding)
                card_roi = img[y_start:y_end, x_start:x_end]

                if card_roi.size > 0:
                    # --- Blank Card Detection ---
                    gray_roi = cv2.cvtColor(card_roi, cv2.COLOR_BGR2GRAY)
                    variance = np.var(gray_roi)
                    if variance < 15:  # Threshold for blank slot (tune as needed)
                        print(f"Blank card slot detected for card {i+1} (variance={variance:.2f}), skipping.")
                        continue
                    card_filename = f"card_{i+1}.png"
                    card_save_path = os.path.join(output_dir, card_filename)
                    cv2.imwrite(card_save_path, card_roi)
                    extracted_card_paths.append(card_save_path)
                    # print(f"Saved card {i+1} to {card_save_path}") # Reduce noise
                else:
                    print(f"Warning: Empty ROI detected for card {i+1}")
        else:
            print("No valid card contours found.")

        # Save debugging image
        if save_debug_image and debug_img is not None:
            debug_img_path = os.path.join(output_dir, "_debug_contours.png")
            cv2.imwrite(debug_img_path, debug_img)
            print(f"Saved debug image to {debug_img_path}")

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")

    print(f"Extracted {len(extracted_card_paths)} card images.")
    return extracted_card_paths

def split_binder_page_by_grid(image_path, output_dir, inner_crop_percent=5):
    """Splits a binder page image by dividing it into a 3x3 grid.

    Args:
        image_path (str): Path to the input binder page image.
        output_dir (str): Directory to save the extracted card images.
        inner_crop_percent (int): Percentage to crop inwards from each grid cell border
                                to remove binder edges (e.g., 5 = 5% crop from each side).

    Returns:
        list: A list of file paths for the extracted card images.
    """
    extracted_card_paths = []
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not load image from {image_path}")
            return []

        img_height, img_width = img.shape[:2]

        cell_width = img_width // 3
        cell_height = img_height // 3

        # Calculate inwards crop amount based on percentage
        crop_x = (cell_width * inner_crop_percent) // 100
        crop_y = (cell_height * inner_crop_percent) // 100

        print(f"Image Size: {img_width}x{img_height}, Cell Size: {cell_width}x{cell_height}")
        print(f"Cropping inwards by X:{crop_x}px, Y:{crop_y}px per side ({inner_crop_percent}%)")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        card_index = 0
        for r in range(3): # Rows
            for c in range(3): # Columns
                card_index += 1

                # Define cell boundaries
                y_start = r * cell_height
                y_end = y_start + cell_height
                x_start = c * cell_width
                x_end = x_start + cell_width

                # Apply inner crop
                roi_y_start = y_start + crop_y
                roi_y_end = y_end - crop_y
                roi_x_start = x_start + crop_x
                roi_x_end = x_end - crop_x

                # Ensure coordinates are valid after cropping
                if roi_y_start >= roi_y_end or roi_x_start >= roi_x_end:
                    print(f"Warning: Inner crop too large for card {card_index}, skipping.")
                    continue

                # Extract ROI
                card_roi = img[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

                if card_roi.size > 0:
                    # --- Blank Card Detection ---
                    gray_roi = cv2.cvtColor(card_roi, cv2.COLOR_BGR2GRAY)
                    variance = np.var(gray_roi)
                    if variance < 15:  # Threshold for blank slot (tune as needed)
                        print(f"Blank card slot detected for card {card_index} (variance={variance:.2f}), skipping.")
                        continue
                    card_filename = f"card_{card_index}.png"
                    card_save_path = os.path.join(output_dir, card_filename)
                    cv2.imwrite(card_save_path, card_roi)
                    extracted_card_paths.append(card_save_path)
                    # print(f"Saved card {card_index} to {card_save_path}") # Reduce noise
                else:
                    print(f"Warning: Empty ROI detected for card {card_index}")

    except Exception as e:
        print(f"Error processing image {image_path} with grid method: {e}")

    print(f"Extracted {len(extracted_card_paths)} card images using grid method.")
    return extracted_card_paths

# Example usage (for testing standalone)
# if __name__ == '__main__':
#     test_image = 'path/to/your/test_binder_page.jpg'
#     output = 'path/to/your/output_directory'
#     paths = split_binder_page(test_image, output)
#     print("Extracted paths:", paths) 