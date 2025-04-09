import cv2
import numpy as np
import os
from flask import current_app

# Constants for contour filtering (these may need tuning)
MIN_CARD_AREA_RATIO = 0.01 # Minimum area of a card relative to total image area
MAX_CARD_AREA_RATIO = 0.15 # Maximum area (prevents finding the whole page)
CARD_ASPECT_RATIO_MIN = 0.6  # width/height (typical card is ~2.5/3.5 = 0.71)
CARD_ASPECT_RATIO_MAX = 0.85
APPROX_POLY_EPSILON = 0.02 # Epsilon factor for polygon approximation

def split_binder_page(image_path, output_dir):
    """Splits a binder page image into individual card images.

    Args:
        image_path (str): Path to the input binder page image.
        output_dir (str): Directory to save the extracted card images.

    Returns:
        list: A list of file paths for the extracted card images.
              Returns empty list if image loading or processing fails.
    """
    extracted_card_paths = []
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not load image from {image_path}")
            return []

        img_height, img_width = img.shape[:2]
        total_area = img_width * img_height

        # --- Preprocessing ---
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Apply Gaussian blur to reduce noise and improve contour detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Use Canny edge detection
        edged = cv2.Canny(blurred, 50, 150)
        # Optionally dilate edges to close gaps
        # kernel = np.ones((3,3),np.uint8)
        # edged = cv2.dilate(edged, kernel, iterations = 1)

        # --- Find Contours ---
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        card_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            area_ratio = area / total_area

            # --- Filter by Area ---
            if MIN_CARD_AREA_RATIO < area_ratio < MAX_CARD_AREA_RATIO:
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, APPROX_POLY_EPSILON * perimeter, True)

                # --- Filter by Shape (expecting rectangles, so 4 vertices) ---
                if len(approx) == 4:
                    (x, y, w, h) = cv2.boundingRect(approx)
                    aspect_ratio = float(w) / h

                    # --- Filter by Aspect Ratio ---
                    if CARD_ASPECT_RATIO_MIN < aspect_ratio < CARD_ASPECT_RATIO_MAX:
                        card_contours.append(approx)
                        # Optional: Draw contour for debugging
                        # cv2.drawContours(img, [approx], -1, (0, 255, 0), 2)

        # --- Sort Contours (Top-to-bottom, Left-to-right) ---
        # Assuming a standard 3x3 grid
        if len(card_contours) > 0:
            # Get bounding boxes and calculate center y for row sorting
            bounding_boxes = [cv2.boundingRect(c) for c in card_contours]
            # Sort primarily by y-coordinate (top to bottom)
            # Add a tolerance for rows - cards whose y centers are close are in same row
            row_tolerance = img_height * 0.1 # Adjust tolerance as needed
            sorted_contours = sorted(zip(card_contours, bounding_boxes),
                                   key=lambda item: (round((item[1][1] + item[1][3]/2) / row_tolerance),
                                                    item[1][0] + item[1][2]/2) # Then sort by x center within row
                                  )

            # Limit to top 9 contours if more are found (can happen with noise)
            sorted_contours = sorted_contours[:9]

            # --- Extract and Save ROIs ---
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            for i, (contour, (x, y, w, h)) in enumerate(sorted_contours):
                # Add a small padding if desired
                padding = 2
                y_start = max(0, y - padding)
                y_end = min(img_height, y + h + padding)
                x_start = max(0, x - padding)
                x_end = min(img_width, x + w + padding)

                card_roi = img[y_start:y_end, x_start:x_end]

                if card_roi.size > 0:
                    card_filename = f"card_{i+1}.png" # Simple naming for now
                    card_save_path = os.path.join(output_dir, card_filename)
                    cv2.imwrite(card_save_path, card_roi)
                    extracted_card_paths.append(card_save_path)
                    print(f"Saved card {i+1} to {card_save_path}")
                else:
                    print(f"Warning: Empty ROI detected for card {i+1}")

            # Optional: Save debugging image with contours drawn
            # debug_img_path = os.path.join(output_dir, "_debug_contours.png")
            # cv2.imwrite(debug_img_path, img)

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        # Optionally re-raise or handle differently

    print(f"Extracted {len(extracted_card_paths)} card images.")
    return extracted_card_paths

# Example usage (for testing standalone)
# if __name__ == '__main__':
#     test_image = 'path/to/your/test_binder_page.jpg'
#     output = 'path/to/your/output_directory'
#     paths = split_binder_page(test_image, output)
#     print("Extracted paths:", paths) 