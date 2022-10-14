import json
import boto3
import requests
import csv
import requests_aws4auth


url = "https://search-restaurants-3apwbxvtu2ezv5mzy5jmomaw2e.us-east-1.es.amazonaws.com/restaurants/Restaurants"
headers = {"Content-Type": "application/json"}

def lambda_handler(event, context):
    with open('restaurants_yelp.csv', newline='') as f:
        reader = csv.reader(f)
        restaurants = list(reader)
    
    restaurants = restaurants[1:]
    print("leng:", len(restaurants))
    for restaurant in restaurants:
        body = {
            'business_id': restaurant[0],
            'cuisine': restaurant[2]
        }
        #r = requests.post(url, data=json.dumps(body), headers=headers)
        es_response = requests.post(url, headers=headers, data=json.dumps(body),auth=("opensearch6998","52Lxj1314&"))
        #print(json.dumps(body))
        #print(json.loads(es_response.content))
        
        
        


