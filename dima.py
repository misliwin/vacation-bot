import urllib2
#Importing main Smartsheet SDK
import smartsheet
#datetime for dates
import datetime
#for posting Spark messages
import requests
#for parsing json data
import json
#For checking weather
import forecastio
import time


#Access token for the Spark
bearer = "ZGRmMjc5NmEtMGYyOC00ZGEwLWFmMWItNmJlZjA1ZjBhZThiOTFmMDEyMDItYjEx"
accesstoken="Bearer "+bearer
#Spark room ID
#roomID='Here is the needed roomID' - roomID is taked from webhook
bot_email = "BotVacation@sparkbot.io"
bot_name = "BotVacation"
smartsheet_token = '4oytkbafdbftmjq60sytnlb432'


HELLO_WORLD = """<html>
<head>
    <title>Python Anywhere hosted web application</title>
</head>
<body>
<h1>This is webpage with python code of sparkbot</h1>
<h2>All rights reserved. Copying is prohibited</h2>
</body>
</html>"""

def sendSparkGET(url):
    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents

def sendSparkPOST(url, data, type):
    contentType = type
    headers={"Accept" : "application/json",
                                         "Content-Type":contentType}
    request = urllib2.Request(url, json.dumps(data),
                                headers)
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents

def sendMessage(text, webhook):
    if webhook['data']['personEmail'] != bot_email:
        contents = sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "markdown": text,"text": "cos"}, "application/json")
    contents = ''
    return contents

def _url(path):
    return 'https://api.ciscospark.com/v1' + path
def get_rooms(at):
    headers = {'Authorization':at}
    resp = requests.get(_url('/rooms'),headers=headers)
    dict = json.loads(resp.text)
    dict['statuscode']=str(resp.status_code)
    return dict
def post_message(at,roomId,text):
    headers = {'Authorization':at, 'content-type':'application/json'}
    payload = {'roomId':roomId, 'text':text}
    resp = requests.post(url=_url('/messages'),json=payload, headers=headers)
    dict = json.loads(resp.text)
    dict['statuscode']=str(resp.status_code)
    return dict
def del_message(at,messageId):
    headers = {'Authorization':at, 'content-type':'application/json'}
    resp = requests.delete(url=_url('/messages/{:s}'.format(messageId)), headers=headers)
    dict = {}
    dict['statuscode']=str(resp.status_code)
    return dict
def get_weather():
    #Key for the darksky.net account
    api_key = "api-key for darksky.net"
    #Krakow city
    lat = 50.0647
    lng = 19.9450
    #Getting info
    forecast = forecastio.load_forecast(api_key, lat, lng)
    #Some words description of the weather
    byHour = forecast.hourly()
    text = 'Currently in Krakow ' + byHour.summary
    text = text + '\n Temperature is: {}'.format(forecast.currently().d['temperature']) + ' celsius'
    return text

def action(webhook):
    i=0
    n=0
    #empty lists
    #people=[]
    start=[]
    start_date=[]
    end=[]
    end_date=[]
    parentID = []
    parentID_absent= []
    name=[]
    roomID = webhook['data']['roomId']
    #Main part of the search function
    #Access to the Smartsheet Cloud by using a unique user token, should be changed for other applications
    smartsheet_var = smartsheet.Smartsheet(smartsheet_token)
    sendMessage(smartsheet_token, webhook)
    #Get all the values for one particular column, in my case it is From Date. In order to get the ID we can use the function described in pySmartsheetFunc
    columns = smartsheet_var.Sheets.get_sheet(4099678120765316, page_size=1000,column_ids=(4738953166251908))
        #url = 'https://api.smartsheet.com/2.0/sheets/4099678120765316?pageSize=1000&page=1&columnIds=4738953166251908'
        #columns = requests.get(url).json()
    #403 forbidden erorr
    #Looping through all the records in that returned column(rows)
    while i < int(columns.total_row_count):
    #while i < 17:
    #Excuding the rows without dates as values (it will be None, something eles couldn't be there because of type of the column)
        if str(columns.rows[i].cells[0].value) != 'None':
            #If we have a match, then add it to the start list
            start.append(columns.rows[i].cells[0].value)
            #with the same i (iterator) we need to check end dates as well, because later on it will be checked with the today date
            columns_end = smartsheet_var.Sheets.get_sheet(4099678120765316, page_size=1000,column_ids=(2487153352566660))
            #If we have a match, it applies that the End date value also will be populated
            end.append(columns_end.rows[i].cells[0].value)
            #If we have a match, we are adding this record to a parent id list (which is used for searching for a person's name)
            parentID.append(columns.rows[i].parent_id)
            #Counter
            i+=1
        else:
            i+=1
    #print(parentID)
    #Iterating through newly created list with actual dates and modifying it into date format for further comparison
    for i in start:
        #Spliting and assigning to the variables
        a1,a2,a3=i.split('-')
        #Creating a datetima variable
        start_date.append(datetime.date(int(a1),int(a2),int(a3)))
    #print(start_date)
    #THe same iteration as before
    for i in end:
        e1,e2,e3=i.split('-')
        end_date.append(datetime.date(int(e1),int(e2),int(e3)))
    #print(end_date)

    #Comparison and checking the actual parentID of persons who are absent
    while n < len(start_date)-1:
        #if it is TRUE (today is between a time range)
        if start_date[n] <= datetime.date.today() <= end_date[n]:
            #creating a list of parentIDs with people who are absent
            parentID_absent.append(parentID[n])
            n+=1
        else:
            n+=1
    #Querying the "employee" column by parentID and returning the actual name
    colmn_names = smartsheet.Sheets.get_sheet(4099678120765316, column_ids=8820340328556420)
    for i in parentID_absent:
        name.append(colmn_names.get_row(i).cells[0].value)
    #creating a set from a list in order to eliminate redundant records
    setname=set(name)
    #Checking if we have any entries in the vacation list
    #now = time.strftime("%c")
    #getting current date
    curdate="Today is "  + time.strftime("%x") + "\n"
    #Checking if there are no records, then just post weather
    if len(setname)==0:
       pass
    #If we have only one record, then adjust message accordingly
    elif len(setname)==1:
        text = json.dumps(list(setname))
        text = text[1:-1]
        text1 = get_weather()
        text1 = "This is an automated message.\n" + curdate + text1
        text = text1 + '\n Today the following person is absent:\n' + text
        messid2 = post_message(accesstoken,roomID,text)
        #sleep for 23 hours and then delete a message
        time.sleep(82800)
        #delete a message
        del_message(accesstoken,messid2['id'])
    #If we have more, then adjust accordingly
    else:
       text = json.dumps(list(setname))
       text = text[1:-1]
       text1 = get_weather()
       text = text1 + '\n Today the following people are absent:\n' + text
       text = "This is an automated message.\n" + curdate + text
       #post a message
       messid2 = post_message(accesstoken,roomID,text)
       #sleep for 23 hours and then delete a message
       time.sleep(82800)
       #delete a message
       del_message(accesstoken,messid2['id'])

def application(environ, start_response):
    if environ.get('PATH_INFO') == '/':
        status = '200 OK'
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
        if request_body_size > 0:
            request_body = environ['wsgi.input'].read(request_body_size)
            webhook = json.loads(request_body)
            result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
            result = json.loads(result)
            if webhook['data']['personEmail'] != bot_email:
                action(webhook)
            content = ''
        else:
            content = HELLO_WORLD
    else:
        status = '404 NOT FOUND'
        content = 'Page not found.'
    response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(content)))]
    start_response(status, response_headers)
    yield content.encode('utf8')



