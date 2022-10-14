
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """





# --- Helpers that build all of the responses ---


def elicit_slot(session_attributes, active_contexts, intent, slot_to_elicit, message):
    return {
        'sessionState': {
            'activeContexts':[{
                'name': 'intentContext',
                'contextAttributes': active_contexts,
                'timeToLive': {
                    'timeToLiveInSeconds': 600,
                    'turnsToLive': 1
                }
            }],
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ElicitSlot',
                'slotToElicit': slot_to_elicit
            },
            'intent': intent
        },
        'messages': [{'contentType': 'PlainText', 'content': message}]
    }


def confirm_intent(active_contexts, session_attributes, intent, message):
    return {
        'sessionState': {
            'activeContexts': [active_contexts],
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ConfirmIntent'
            },
            'intent': intent
        },
         'messages': [{'contentType': 'PlainText', 'content': message}]
    }


def close(session_attributes, active_contexts, fulfillment_state, intent, message):
    response = {
        'sessionState': {
            'activeContexts':[{
                'name': 'intentContext',
                'contextAttributes': active_contexts,
                'timeToLive': {
                    'timeToLiveInSeconds': 600,
                    'turnsToLive': 1
                }
            }],
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close',
            },
            'intent': intent
        },
        'messages': [{'contentType': 'PlainText', 'content': message}]
    }

    return response


def delegate(session_attributes, active_contexts, intent, message):
    return {
        'sessionState': {
            'activeContexts':[{
                'name': 'intentContext',
                'contextAttributes': active_contexts,
                'timeToLive': {
                    'timeToLiveInSeconds': 600,
                    'turnsToLive': 1
                }
            }],
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Delegate',
            },
            'intent': intent
        },
        'messages': [{'contentType': 'PlainText', 'content': message}]
    }


def initial_message(intent_name):
    response = {
            'sessionState': {
                'dialogAction': {
                    'type': 'ElicitSlot',
                    'slotToElicit': 'Location'
                },
                'intent': {
                    'confirmationState': 'None',
                    'name': intent_name,
                    'state': 'InProgress'
                }
            }
    }
    
    return response


""" --- Helper Functions --- """
def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(value):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary of the Slots section in the payloads.
    Note that this function would have negative impact on performance.
    """

    try:
        if value is not None:
            return value['value']['interpretedValue']
    except KeyError:
        return None

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    print("message",message_content)
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': message_content
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def validate_dining_request(location, cuisine, numpeople,date,time,email):
    
    location_options = ['nyc', 'dc', 'boston']
    #if location is not None and location.lower() not in location_options:
    if location is not None and location.lower() not in location_options:
        return build_validation_result(False,
                                       'Location',
                                       'We do not support {}, would you like to try a different location?'.format(location))
        
    cuisine_options = ['japanese', 'chinese', 'american','italian','mexican']
    if cuisine is not None and cuisine.lower() not in cuisine_options:
        return build_validation_result(False,
                                       'Cuisine',
                                       'We do not support {}, would you like to try a different cuisine?'.format(cuisine))
    if numpeople is not None and int(numpeople) > 12:
        return build_validation_result(False,
                                       'numPeople',
                                       'We currently do not support {} size of party, would you like to try a different party size?'.format(numpeople))
   
    if date is not None and datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
        return build_validation_result(False, 'Date', 'You can only search from today. What is your option for the date?')
    
    if time is not None:
        hour, minute = time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        print(date)
        print(datetime.date.today())
        if datetime.datetime.strptime(date, '%Y-%m-%d').date() == datetime.date.today():
            print(datetime.datetime.now().hour,hour)
            if hour < datetime.datetime.now().hour:
                return build_validation_result(False, 'Time', "Time has passed for today. Try a later time.")
        
    
    
    
    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """


def dining_suggest(intent_request):
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """
    
    location = try_ex(intent_request['sessionState']['intent']['slots']['Location'])
   
    cuisine = try_ex(intent_request['sessionState']['intent']['slots']["Cuisine"])
    numpeople = try_ex(intent_request['sessionState']['intent']['slots']["numPeople"])
    date = try_ex(intent_request['sessionState']['intent']['slots']["Date"])
    time = try_ex(intent_request['sessionState']['intent']['slots']["Time"])
    email = try_ex(intent_request['sessionState']['intent']['slots']["Email"])
    source = intent_request['invocationSource'] #slots are not fulfilled
    intent = intent_request['sessionState']['intent']
    session_attributes = {}
    session_attributes['sessionId'] = intent_request['sessionId']
    active_contexts = {}
    
    
    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = intent_request['sessionState']['intent']['slots']
        validation_result = validate_dining_request(location, cuisine, numpeople, date, time, email)
        print(validation_result)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(session_attributes,
                               active_contexts,
                               intent,
                               validation_result['violatedSlot'],
                               validation_result['message'])
        elif location is None:
            return elicit_slot(session_attributes,
                               active_contexts,
                               intent,
                               "Location",
                               "What city do you want to look at?")
        elif cuisine is None:
            return elicit_slot(session_attributes,
                               active_contexts,
                               intent,
                               "Cuisine",
                               "What's your cuisine choice?")
        elif numpeople is None:
            return elicit_slot(session_attributes,
                               active_contexts,
                               intent,
                               "numPeople",
                               "What's size of your party?")
        elif date is None:
            return elicit_slot(session_attributes,
                               active_contexts,
                               intent,
                               "Date",
                               "What date?")
        elif time is None:
            return elicit_slot(session_attributes,
                               active_contexts,
                               intent,
                               "Time",
                               "What time?")    
        elif email is None:
            return elicit_slot(session_attributes,
                               active_contexts,
                               intent,
                               "Email",
                               "What's your email?")
        
    # push data into queue
    
    client=boto3.client('sqs')
    response=client.send_message(
        QueueUrl="https://sqs.us-east-1.amazonaws.com/121063675658/DiningInfo",
        MessageBody=json.dumps({
                "location":location,
                "cuisine":cuisine,
                "numpeople":numpeople,
                "date":date,
                "time":time,
                "email":email}
        )
        )
   
    return close(session_attributes,
                 active_contexts,'Fulfilled',intent,
                  "Great! Expect my suggestions!")

""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    #print("intent:", intent_request)
    return dining_suggest(intent_request)

    #raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    #logger.debug('event.bot.name={}'.format(event['bot']['name']))
    #print("event",event)
    return dispatch(event)
    
