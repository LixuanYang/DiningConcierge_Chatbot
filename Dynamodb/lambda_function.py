import json
import boto3
import datetime
from botocore.vendored import requests
import csv
from decimal import Decimal

def lambda_handler(event,context):
    with open('restaurants_yelp.csv', newline='') as f:
        reader = csv.reader(f)
        restaurants = list(reader)
    # print(type(int(restaurants[1][5][0])))
    restaurants = restaurants[1:]
    #print("leng:",len(restaurants))
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp-restaurants')
    
    for restaurant in restaurants:
        
        tableEntry = {
            'restaurant_id': restaurant[0],
            'name': restaurant[1],
            'address': restaurant[3],
            'cuisine': restaurant[2],
            'coordinates': ((restaurant[4],restaurant[5])),
            'rating': str(restaurant[6]),
            'review_count': int(restaurant[7]),
            'zip_code': restaurant[8]
        }
        
        table.put_item(
            Item={
                'restaurant_id': tableEntry['restaurant_id'],
                'name': tableEntry['name'],
                'address': tableEntry['address'],
                'cuisine': tableEntry['cuisine'],
                'coordinates': tableEntry['coordinates'],
                'review_count': tableEntry['review_count'],
                'rating': tableEntry['rating'],
                'zip_code': tableEntry['zip_code'],
                'insertedAtTimestamp': str(datetime.datetime.now())
               }
            )
        
