import json
import boto3
from boto3.dynamodb.conditions import Key
import logging

#set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


#create the database resource pointing to a table
db = boto3.resource('dynamodb')
table = db.Table('Employee')


def lambda_handler(event, context):
    
    # grab variables passed in through the event construct
    print(event['Details'])
    PhoneNumber = event['Details']['Parameters'].get('PhoneNumber','')
    EmployeeID = event['Details']['Parameters'].get('EmployeeID', '')
    EmployeePIN = event['Details']['Parameters'].get('EmployeePIN', '')
    
    # create an empty dict
    ReturnResult = {};
    
    # do search
    ReturnResult = EmployeeSearch(PhoneNumber, EmployeeID)
    logger.info(ReturnResult)
    
    if len(ReturnResult['EmployeeID']) == 0:
        # if we dont have employee id we have nothing
        ReturnResult['EmployeePIN'] = ''
        ReturnResult['EmployeeName'] = ''
        ReturnResult['EmployeeType'] = 0 # we dont know who this is
    else:
        # We have data from the database
        if len(ReturnResult['EmployeePIN']) != 0 and ReturnResult['EmployeePIN'] == EmployeePIN:
            #we have PIP and it is the same as the entered PIP
            ReturnResult['EmployeeType'] = 1 # Horray
        else:
            if(len(ReturnResult['EmployeePIN']) != 0):
                ReturnResult['EmployeeType'] = 3 # PIN is wrong
            else:
                ReturnResult['EmployeeType'] = 2 # Flag to ask for PIN
    
    ReturnResult['EmployeePIN'] = '' # Dont want to reveal PIN
    logger.info('##ReturnDict')
    logger.info(ReturnResult)
    return ReturnResult  
    
    
def EmployeeSearch(PhoneNumber, EmployeeID):
    res = {}
    if len(PhoneNumber) > 0:
        # do the search using the index
        # this should be in a try except block
        data = table.query(IndexName= 'PhoneNumber-index',
                   KeyConditionExpression = Key('PhoneNumber').eq(PhoneNumber))
        
    elif len(EmployeeID) > 0:
        # do the search using the main partition key
        #use Employee ID as a search parameter 
        # this should be in a try except block
        data = table.query(KeyConditionExpression = Key('EmployeeID').eq(EmployeeID))
        #print(data['Items'])
    
    logger.info(data['Items'])    
    # at this stage data may or may not contain data
    if len(data['Items']) == 1:
        # we have data. Collect them into a dict
        res['EmployeeID'] = data['Items'][0]['EmployeeID']
        res['EmployeeName'] = data['Items'][0]['EmployeeName']
        res['EmployeePIN'] = data['Items'][0]['EmployeePIN']
    else:
        res['EmployeeID'] = ''
        res['EmployeeName'] = ''
        res['EmployeePIN'] = ''
    return res
