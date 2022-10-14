import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
import requests
from botocore.exceptions import ClientError
import random

def getsuggest():
    # create a boto3 client
    sqsclient = boto3.client('sqs')

    response = sqsclient.receive_message(
        QueueUrl="https://sqs.us-east-1.amazonaws.com/121063675658/DiningInfo",
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        WaitTimeSeconds=0
    )
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelp-restaurants')
    message = json.loads(response['Messages'][0]["Body"])
    #message = json.loads(response['Messages']["Body"])
    print("message:",message)
    location = message["location"]
    cuisine = message['cuisine']
    numpeople = message["numpeople"]
    date = message['date']
    time = message["time"]
    email = message['email']
    print("location:",location)
    #delete the message after polling
    
    sqsclient.delete_message(
            QueueUrl="https://sqs.us-east-1.amazonaws.com/121063675658/DiningInfo",
            ReceiptHandle=response['Messages'][0]['ReceiptHandle'])
            #ReceiptHandle=response['Messages']['ReceiptHandle'])


    headers = {"Content-Type": "application/json"}
    url = "https://search-restaurants-3apwbxvtu2ezv5mzy5jmomaw2e.us-east-1.es.amazonaws.com/restaurants/_search"
    query = {
        "query": {
            "multi_match": {
                "query": cuisine
            }
        }
    }
    
    resp = requests.get(url, headers=headers,auth=("opensearch6998","52Lxj1314&"),data=json.dumps(query))
    numhits = (resp.json())['hits']["total"]["value"]
    
    #get 3 random hits
    idx_lst = random.sample(range(1, numhits - 1), 3)
    idx1=idx_lst[0]
    idx2=idx_lst[1]
    idx3=idx_lst[2]
    url1 = "https://search-restaurants-3apwbxvtu2ezv5mzy5jmomaw2e.us-east-1.es.amazonaws.com/_search?from=" + str(idx1) + "&&size=1&&q=cuisine:" + cuisine
    url2 = "https://search-restaurants-3apwbxvtu2ezv5mzy5jmomaw2e.us-east-1.es.amazonaws.com/_search?from=" + str(idx2) + "&&size=1&&q=cuisine:" + cuisine
    url3 = "https://search-restaurants-3apwbxvtu2ezv5mzy5jmomaw2e.us-east-1.es.amazonaws.com/_search?from=" + str(idx3) + "&&size=1&&q=cuisine:" + cuisine
    rest1 = requests.get(url1, headers=headers,auth=("opensearch6998","52Lxj1314&"))
    rest2 = requests.get(url2, headers=headers,auth=("opensearch6998","52Lxj1314&"))
    rest3 = requests.get(url3, headers=headers,auth=("opensearch6998","52Lxj1314&"))
    
    rand1_restaurantID = (rest1.json())['hits']['hits'][0]['_source']["business_id"]
    suggest1_restaurant = table.scan(FilterExpression=Attr("restaurant_id").eq(rand1_restaurantID))['Items'][0]
    rand2_restaurantID = (rest2.json())['hits']['hits'][0]['_source']["business_id"]
    suggest2_restaurant = table.scan(FilterExpression=Attr("restaurant_id").eq(rand2_restaurantID))['Items'][0]
    rand3_restaurantID = (rest3.json())['hits']['hits'][0]['_source']["business_id"]
    suggest3_restaurant = table.scan(FilterExpression=Attr("restaurant_id").eq(rand3_restaurantID))['Items'][0]
    print("suggest1_restaurant:",suggest1_restaurant)
    print("suggest2_restaurant:",suggest2_restaurant)
    print("suggest3_restaurant:",suggest3_restaurant)
    
    #send email
    SENDER = "ly2555@columbia.edu"

    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = email
    
    
    
    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"
    
    # The subject line for the email.
    SUBJECT = "Restaurant Suggestion"
    
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = "Your Restaurant Suggestion:\r\n"+"Hello! Here is my "+cuisine+" restaurants suggestion for "+numpeople+" people, for "+date+" at "+time+": 1. "+suggest1_restaurant["name"]+", located at "+suggest1_restaurant["address"]+" with rating of "+suggest1_restaurant['rating']+". 2. "+suggest2_restaurant["name"]+", located at "+suggest2_restaurant["address"]+" with rating of "+suggest2_restaurant['rating']+". 3. "+suggest3_restaurant["name"]+", located at "+suggest3_restaurant["address"]+" with rating of "+suggest3_restaurant['rating']+". Enjoy your meal!"         
    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)
    
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    

    
    
def lambda_handler(event, context):
    getsuggest()


