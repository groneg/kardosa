# backend/app/ebay_client.py
import requests
import base64 # Import base64
import os
from flask import current_app

# Correct Production Endpoint for searchByImage
EBAY_API_ENDPOINT_PROD = "https://api.ebay.com/buy/browse/v1/item_summary/search_by_image"
# Sandbox not supported for this endpoint
# EBAY_API_ENDPOINT_SANDBOX = "..."

# Marketplace ID (Example: US)
EBAY_MARKETPLACE_ID = "EBAY_US"

def get_oauth_token():
    """Gets an OAuth token for eBay API access (if required).
       Requires client ID and client secret (Cert ID).
       This is a basic Client Credentials Grant flow example.
       Specific flow might differ based on API requirements.
    """
    app_id = current_app.config.get('EBAY_APP_ID')
    cert_id = current_app.config.get('EBAY_CERT_ID')
    env = current_app.config.get('EBAY_ENV')

    if not app_id or not cert_id:
        print("Error: eBay App ID or Cert ID not configured.")
        return None

    # Use Production token URL since Sandbox isn't supported for searchByImage
    token_url = "https://api.ebay.com/identity/v1/oauth2/token"

    # --- Correct Basic Auth Header Encoding ---
    credentials = f"{app_id}:{cert_id}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encoded_credentials}'
    }
    body = {
        'grant_type': 'client_credentials',
        # Scope required for Buy APIs
        'scope': 'https://api.ebay.com/oauth/api_scope'
    }

    try:
        response = requests.post(token_url, headers=headers, data=body)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        token_data = response.json()
        print(f"DEBUG: Successfully obtained OAuth token expiring in {token_data.get('expires_in')}s")
        return token_data.get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Error getting eBay OAuth token: {e}")
        print(f"Response Status: {e.response.status_code if e.response else 'N/A'}")
        print(f"Response Body: {e.response.text if e.response else 'N/A'}")
        return None
    except Exception as e:
        print(f"Unexpected error getting eBay OAuth token: {e}")
        return None

def find_card_on_ebay(image_path):
    """Calls the eBay API to find listings matching the given image.

    Args:
        image_path (str): Path to the individual card image file.

    Returns:
        dict or None: Parsed API response data, or None if an error occurs.
    """
    print(f"DEBUG: Attempting eBay lookup for image: {image_path}")
    app_id = current_app.config.get('EBAY_APP_ID')
    env = current_app.config.get('EBAY_ENV')

    if not app_id:
        print("Error: eBay App ID not configured.")
        return None

    # --- Use Production Endpoint Only ---
    api_endpoint = EBAY_API_ENDPOINT_PROD
    print(f"DEBUG: Using eBay API Endpoint: {api_endpoint}")

    # --- Obtain OAuth Token ---
    access_token = get_oauth_token()
    if not access_token:
        print("Error: Could not obtain eBay OAuth token.")
        return None

    # --- Read and Base64 Encode Image ---
    try:
        # If image_path is a URL path (starts with '/uploads/'), convert to real file path
        if image_path.startswith('/uploads/'):
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path.replace('/uploads/', '', 1))
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error reading or encoding image file {image_path}: {e}")
        return None

    # --- Construct API Request --- 
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-EBAY-C-MARKETPLACE-ID': EBAY_MARKETPLACE_ID
    }
    request_body = {
        "image": encoded_string
    }

    # Add limit query parameter to the endpoint URL
    request_url = f"{api_endpoint}?limit=2"

    # --- Make API Call ---
    try:
        print(f"DEBUG: Making POST request to {request_url} for image {os.path.basename(image_path)}")
        response = requests.post(request_url, headers=headers, json=request_body)

        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        api_response_data = response.json()
        print(f"DEBUG: Received eBay API response (first 500 chars): {str(api_response_data)[:500]}")
        return api_response_data

    except requests.exceptions.RequestException as e:
        print(f"Error calling eBay API: {e}")
        print(f"Response Status: {e.response.status_code if e.response else 'N/A'}")
        print(f"Response Body: {e.response.text if e.response else 'N/A'}")
        return None
    except Exception as e:
        print(f"Unexpected error calling eBay API: {e}")
        return None

# Example standalone test (requires Flask app context for config)
# if __name__ == '__main__':
#     app = create_app()
#     with app.app_context():
#         test_image = 'path/to/your/test_card.png'
#         results = find_card_on_ebay(test_image)
#         print("API Results:", results) 