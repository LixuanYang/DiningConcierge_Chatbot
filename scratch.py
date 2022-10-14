import requests
import decimal
import csv
import datetime

API_KEY = 'MBtXg8nhbh0al-IAf-qdrKXoKSLkAFL4Jp4SAI-p5cWBvITAvsHpl3zrHDQbSrnhYYGrmlrlc5oAxpd9Im1GliF2bdManptwzfwxfQ91_Xnns9sRiHib9L0l_EZEY3Yx'
ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'bearer %s' % API_KEY}
LIMIT = 50
restaurants = {}

file = open('restaurants_yelp.csv', 'a', encoding = 'utf-8')
writer = csv.writer(file)

def get_restaurants(term, location, offset):

    parameters = {
        'term' : term.replace(' ', '+'),
        'location' : location.replace(' ', '+'),
        'limit' : LIMIT,
        'offset' : offset,
    }

    return requests.get(url = ENDPOINT, params = parameters, headers = HEADERS)

cuisines = ['Italian', 'Chinese', 'Mexican', 'Indian', 'Japanese', 'Thai', 'American']
location = 'New York City'

for cuisine in cuisines:
    for offset in range(0, 999, 50):

        response = get_restaurants(term = cuisine, location = location, offset = offset)
        restaurants = response.json()['businesses']
        for restaurant in restaurants:

            restaurant_id = restaurant['id']
            restaurant_name = restaurant['name']
            cuisine_type = cuisine
            restaurant_address = "'" + (", ").join(restaurant['location']['display_address']) + "'"
            latitude = decimal.Decimal(str(restaurant['coordinates']['latitude']))
            longitude = decimal.Decimal(str(restaurant['coordinates']['longitude']))
            restaurant_rating = decimal.Decimal(str(restaurant['rating']))
            review_count = restaurant['review_count']
            zipcode = restaurant['location']['zip_code']

            writer.writerow([restaurant_id, restaurant_name, cuisine_type, restaurant_address,
                            latitude, longitude, restaurant_rating, review_count, zipcode])

