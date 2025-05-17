import json
import requests
from bs4 import BeautifulSoup
import re

# URL of the Bikroy ad page
url = 'https://bikroy.com/en/ad/toyota-harrier-promet-octane-black-2020-for-sale-dhaka'

def clean_description(text):
    if not text:
        return None
    # Fix broken encoding
    try:
        text = text.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def get_ad_details(url):
    car_details = {
        'url': url,
        'year_of_production': None,
        'version': None,
        'price': None,
        'images': [],
        'title': None,
        'trim': None,
        'transmission': None,
        'registration_year': None,
        'fuel_type': None,
        'kilometers_driven': None,
        'model': None,
        'condition': None,
        'body_type': None,
        'engine_capacity': None,
        'posted_on': None,
        'seller_name': None,
        'contact': None,
        'description': None,
        'category': "Vehicles - Cars",
        'price_status': None,
        'seller_address': None,
        'location': None,
        'tags': []
    }

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find('script', text=lambda t: t and 'window.initialData' in t)

    if not script_tag:
        print("No script tag with 'window.initialData' found.")
        return car_details

    start_index = script_tag.text.find('window.initialData = ') + len('window.initialData = ')
    end_index = script_tag.text.find(';</script>') if script_tag.text.find(';</script>') != -1 else len(script_tag.text)
    json_data = script_tag.text[start_index:end_index].strip()

    try:
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        print(f"JSON decoding failed: {e}")
        return car_details

    ad = data.get('adDetail', {}).get('data', {}).get('ad', {})

    car_details['title'] = ad.get('title')
    car_details['description'] = clean_description(ad.get('description'))
    car_details['price'] = ad.get('money', {}).get('amount')
    car_details['seller_name'] = ad.get('shop', {}).get('name')
    car_details['posted_on'] = ad.get('adDate')
    car_details['contact'] = ad.get('contactCard', {}).get('phoneNumbers', [])
    car_details['seller_address'] = ad.get('contactCard', {}).get('address')
    car_details['location'] = ad.get('contactCard', {}).get('location', {}).get('name')

    # Extract up to 5 image URLs
    media_items = ad.get('media', {}).get('items', [])
    for item in media_items:
        image_url = item.get('urlOriginal') or item.get('url')
        if image_url:
            car_details['images'].append(image_url)
        if len(car_details['images']) >= 5:
            break

    # Get price_status from priceType or default
    car_details['price_status'] = ad.get('priceType') or 'Negotiable'

    # Parse detailed properties
    for item in ad.get('properties', []):
        label = item.get('label')
        value = item.get('value')
        if label == 'Year of Manufacture':
            car_details['year_of_production'] = value
        elif label == 'Trim / Edition':
            car_details['version'] = value
        elif label == 'Fuel type':
            car_details['fuel_type'] = value
        elif label == 'Kilometers run':
            car_details['kilometers_driven'] = value
        elif label == 'Model':
            car_details['model'] = value
        elif label == 'Condition':
            car_details['condition'] = value
        elif label == 'Transmission':
            car_details['transmission'] = value
        elif label == 'Body type':
            car_details['body_type'] = value
        elif label == 'Engine capacity':
            car_details['engine_capacity'] = value
        elif label == 'Price Type' and not car_details['price_status']:
            car_details['price_status'] = value

    return car_details

# Print the final structured ad details
print(get_ad_details(url))
