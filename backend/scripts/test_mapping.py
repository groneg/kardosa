# backend/scripts/test_mapping.py
import os
import sys
import json
import argparse

# Adjust path to import from app
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

from app import create_app
# Import necessary functions WITHIN app context
# from app.services import map_ebay_result_to_card_data, load_reference_data_cache

# --- Sample eBay Data (from previous logs - replace if needed) ---
# Truncated, just enough for basic testing
SAMPLE_EBAY_RESPONSE = {
    'href': 'https://api.ebay.com/buy/browse/v1/item_summary/search_by_image?limit=2&offset=0',
    'total': 10810404,
    'next': 'https://api.ebay.com/buy/browse/v1/item_summary/search_by_image?limit=2&offset=2',
    'limit': 2,
    'offset': 0,
    'itemSummaries': [
        {
            'itemId': 'v1|256803486693|0',
            'title': 'Jaylen Brown 2024-25 Panini Hoops #122 Boston Celtics',
            'image': {'imageUrl': 'https://i.ebayimg.com/images/g/OAMAAOSwa5pnoFCF/s-l225.jpg'},
            'price': {'value': '1.50', 'currency': 'USD'},
            'condition': 'Ungraded',
            # ... other fields ...
        },
        {
            'itemId': 'v1|135564293091|434931407910',
            'title': '2024-25 Panini Hoops NBA (Base Set) Cards 1-230 - Choose from List',
            'image': {'imageUrl': 'https://i.ebayimg.com/images/g/sF8AAOSwBVpntOcW/s-l225.jpg'},
            'price': {'value': '2.18', 'currency': 'USD'},
            'condition': 'Non gradée',
            # ... other fields ...
        }
    ]
}

def parse_args():
    parser = argparse.ArgumentParser(description="Test mapping eBay API response data.")
    parser.add_argument("-f", "--file", default=None, help="Optional path to a JSON file containing eBay API response.")
    parser.add_argument("--raw_json", default=None, help="Optional raw JSON string of eBay API response (use quotes).")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    ebay_data = None

    if args.file:
        try:
            with open(args.file, 'r') as f:
                ebay_data = json.load(f)
            print(f"Loaded eBay data from file: {args.file}")
        except Exception as e:
            print(f"Error loading JSON from file {args.file}: {e}")
            sys.exit(1)
    elif args.raw_json:
        try:
            ebay_data = json.loads(args.raw_json)
            print("Loaded eBay data from raw JSON string.")
        except Exception as e:
            print(f"Error parsing raw JSON string: {e}")
            sys.exit(1)
    else:
        print("Using sample eBay data hardcoded in script.")
        ebay_data = SAMPLE_EBAY_RESPONSE

    if not ebay_data:
        print("No eBay data provided or loaded.")
        sys.exit(1)

    # Create Flask app and context to access DB and services
    app = create_app()
    with app.app_context():
        # Import here to ensure app context is active
        from app.services import map_ebay_result_to_card_data, load_reference_data_cache
        # Ensure cache is loaded (might have loaded on app creation already)
        load_reference_data_cache()
        print("\n--- Testing map_ebay_result_to_card_data ---")
        mapped_result = map_ebay_result_to_card_data(ebay_data)
        print("\n--- Mapping Result ---")
        if mapped_result:
            print(json.dumps(mapped_result, indent=2))
        else:
            print("Mapping failed or returned None.") 