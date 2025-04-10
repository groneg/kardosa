# backend/scripts/test_image_split.py
import os
import sys
import argparse
from datetime import datetime

# Adjust path to import from app
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

from app.image_utils import split_binder_page, split_binder_page_by_grid, \
    DEFAULT_BLUR_KERNEL, DEFAULT_CANNY_LOW, DEFAULT_CANNY_HIGH, \
    DEFAULT_MIN_CARD_AREA_RATIO, DEFAULT_MAX_CARD_AREA_RATIO, \
    DEFAULT_CARD_ASPECT_RATIO_MIN, DEFAULT_CARD_ASPECT_RATIO_MAX, \
    DEFAULT_APPROX_POLY_EPSILON, DEFAULT_ROW_TOLERANCE_RATIO

# --- Argument Parsing ---
def parse_args():
    parser = argparse.ArgumentParser(description="Test binder page splitting with different parameters.")
    parser.add_argument("image_path", help="Path to the input binder page image.")
    parser.add_argument("-o", "--output_base", default="../CV_testing",
                        help="Base directory for output subfolders (relative to script location). Default: ../CV_testing")
    parser.add_argument("--run_name", default=None, help="Optional custom name for the output subfolder.")
    parser.add_argument("--method", choices=['contour', 'grid'], default='contour',
                        help="Splitting method: 'contour' (default) or 'grid'.")

    # Contour Method Parameters
    contour_group = parser.add_argument_group('Contour Method Parameters')
    contour_group.add_argument("--blur", type=int, nargs=2, default=DEFAULT_BLUR_KERNEL, metavar=('W', 'H'), help=f"Gaussian blur kernel size. Default: {DEFAULT_BLUR_KERNEL}")
    contour_group.add_argument("--canny_low", type=int, default=DEFAULT_CANNY_LOW, help=f"Canny low threshold. Default: {DEFAULT_CANNY_LOW}")
    contour_group.add_argument("--canny_high", type=int, default=DEFAULT_CANNY_HIGH, help=f"Canny high threshold. Default: {DEFAULT_CANNY_HIGH}")
    contour_group.add_argument("--min_area", type=float, default=DEFAULT_MIN_CARD_AREA_RATIO, help=f"Min card area ratio. Default: {DEFAULT_MIN_CARD_AREA_RATIO}")
    contour_group.add_argument("--max_area", type=float, default=DEFAULT_MAX_CARD_AREA_RATIO, help=f"Max card area ratio. Default: {DEFAULT_MAX_CARD_AREA_RATIO}")
    contour_group.add_argument("--min_aspect", type=float, default=DEFAULT_CARD_ASPECT_RATIO_MIN, help=f"Min card aspect ratio (W/H). Default: {DEFAULT_CARD_ASPECT_RATIO_MIN}")
    contour_group.add_argument("--max_aspect", type=float, default=DEFAULT_CARD_ASPECT_RATIO_MAX, help=f"Max card aspect ratio (W/H). Default: {DEFAULT_CARD_ASPECT_RATIO_MAX}")
    contour_group.add_argument("--poly_eps", type=float, default=DEFAULT_APPROX_POLY_EPSILON, help=f"Polygon approximation epsilon factor. Default: {DEFAULT_APPROX_POLY_EPSILON}")
    contour_group.add_argument("--row_tol", type=float, default=DEFAULT_ROW_TOLERANCE_RATIO, help=f"Row sorting tolerance ratio. Default: {DEFAULT_ROW_TOLERANCE_RATIO}")
    contour_group.add_argument("--no_debug_img", action="store_true", help="Do not save the debug image with contours.")

    # Grid Method Parameters
    grid_group = parser.add_argument_group('Grid Method Parameters')
    grid_group.add_argument("--crop_percent", type=int, default=5,
                           help="Inner crop percentage for grid method. Default: 5")

    return parser.parse_args()

# --- Main Execution ---
if __name__ == "__main__":
    args = parse_args()

    # Ensure input image exists
    if not os.path.isfile(args.image_path):
        print(f"Error: Input image not found at {args.image_path}")
        sys.exit(1)

    # Create base output directory if it doesn't exist
    base_output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), args.output_base))
    if not os.path.exists(base_output_path):
        os.makedirs(base_output_path)
        print(f"Created base output directory: {base_output_path}")

    # Create unique subfolder for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.run_name:
        run_folder_name = f"{args.run_name}_{timestamp}"
    else:
        # Add method and relevant params to folder name
        if args.method == 'grid':
            run_folder_name = f"run_{timestamp}_grid_crop{args.crop_percent}"
        else: # contour
            run_folder_name = f"run_{timestamp}_contour_blur{args.blur[0]}x{args.blur[1]}_canny{args.canny_low}-{args.canny_high}"
    run_output_dir = os.path.join(base_output_path, run_folder_name)

    print(f"\n--- Starting Test Run --- ")
    print(f"Input Image: {args.image_path}")
    print(f"Output Directory: {run_output_dir}")
    print(f"Method: {args.method}")

    extracted_paths = []
    if args.method == 'grid':
        print(f"Parameters:")
        print(f"  Crop Percent: {args.crop_percent}")
        print("---")
        extracted_paths = split_binder_page_by_grid(
            image_path=args.image_path,
            output_dir=run_output_dir,
            inner_crop_percent=args.crop_percent
        )
    else: # contour
        print(f"Parameters:")
        print(f"  Blur Kernel: {tuple(args.blur)}")
        print(f"  Canny Thresholds: {args.canny_low}, {args.canny_high}")
        print(f"  Area Ratio Filter: {args.min_area} - {args.max_area}")
        print(f"  Aspect Ratio Filter: {args.min_aspect} - {args.max_aspect}")
        print(f"  Polygon Epsilon: {args.poly_eps}")
        print(f"  Row Tolerance Ratio: {args.row_tol}")
        print(f"  Save Debug Image: {not args.no_debug_img}")
        print("---")
        extracted_paths = split_binder_page(
            image_path=args.image_path,
            output_dir=run_output_dir,
            blur_kernel=tuple(args.blur),
            canny_low=args.canny_low,
            canny_high=args.canny_high,
            min_area_ratio=args.min_area,
            max_area_ratio=args.max_area,
            aspect_min=args.min_aspect,
            aspect_max=args.max_aspect,
            poly_epsilon=args.poly_eps,
            row_tolerance_ratio=args.row_tol,
            save_debug_image=not args.no_debug_img
        )

    print(f"\n--- Test Run Complete --- ")
    print(f"Results saved in: {run_output_dir}")
    print(f"Number of cards extracted: {len(extracted_paths)}") 