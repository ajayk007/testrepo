import json
import yaml
from yaml.loader import SafeLoader
import requests
from jira import JIRA
from datetime import datetime
import sys
# INSERT ALL YOUR AUTH VARIABLES HERE

username="ajay.kamath@amagi.com"

password=sys.argv[1]

release_date=datetime.today().strftime('%Y-%m-%d')

#READ FROM RELEASE YAML

with open('release.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    print(data)

keys=data['Amaginow_release']
discription=""
for key,value in keys.items() :
	discription=discription+key+":"+value+".\n"
discription=discription+"\n"
if(data['Breaking_changes'][0] == "None"):
  print("no breaking change")
else:
  discription=discription+"Breaking changes"+"\n"
  for change in data['Breaking_changes']:
    discription=discription+change+".\n"
  discription=discription+"\n"
if(data['Features'][0] == "None"):
  print("no features release")
else:
  discription=discription+"Features"+"\n"
  for feature in data['Features']:
    discription=discription+feature+".\n"
  discription=discription+"\n"
if(data['Env_variables'][0] == "None"):
  print("no new variable")
else:
  discription=discription+"ENV Variables"+"\n"
  for variable in data['Env_variables']:
    discription=discription+variable+".\n"
  discription=discription+"\n"

if(data['Improvements'][0] == "None"):
  print("no improvemnets")
else:
  discription=discription+"Improvements"+"\n"
  for improve in data['Improvements']:
    discription=discription+improve+".\n"
  discription=discription+"\n"
#INSERT ALL URL PATH AND BASE URL HERE
tickets=data['Tickets']

TICKETS_URL="/unreleasedIssues/add"

ISSUE="/issue"

VERSION="/version"

GET_VERSION="/project/AN/versions"

base_url="https://amagiengg.atlassian.net/rest/api/3"

#AUTHORIZATION TO JIRA 
auth = (username, password)

# HEADERS GOES HERE

headers = {'Content-type': 'application/json'}

#GET RELEASE IN JIRA
URL=base_url+GET_VERSION
RELEASE=requests.get(url=URL,auth=auth,headers=headers)
data1=RELEASE.json()
print(data1)

for item in data1:
  print(item['name'])
  current_version=item['name']
version=current_version.split('.')
if(data["Type"] == "patch"):
  version[2]=str(int(version[2])+1)
elif(data['Type'] == "minor"):
  version[1]=str(int(version[1])+1)
  version[2]='0'
elif(data['Type'] == "major"):
  version[0]='v'+str(int(version[0][1])+1)
  version[1]='0'
  version[2]='0'
NEW_RELEASE=".".join(version)
print(NEW_RELEASE)

# INSERT YOUR PAYLOADS HERE
PAYLOAD_QA_TEST= {
    'transition': {'id': '101'}
}

PAYLOAD_CREATE_RELEASE={
    "name": NEW_RELEASE,
    "description": discription,
    "project": "AN",
    "released": True,
    "releaseDate": release_date,
    "projectId": 10288
    
}
payload = {
    "update": {
        "fixVersions": [
            {
                "add": {"name": NEW_RELEASE}
            }
        ]
    }
}
#CREATE NEW RELEASE
data_version=json.dumps(PAYLOAD_CREATE_RELEASE)
CREATE_RELEASE_URL=base_url+VERSION
CREATE_RELEASE_RESPONSE=requests.post(url=CREATE_RELEASE_URL,headers=headers,auth=auth,data=data_version)
RELEASE_ID=json.loads(CREATE_RELEASE_RESPONSE.text)["id"]
print(RELEASE_ID)

ATTACH_ISSUES_URL=base_url+ISSUE
for ticket in data['Tickets']:
  url=ATTACH_ISSUES_URL+"/"+ticket
  data2=json.dumps(payload)
  CREATE_RELEASE_RESPONSE=requests.put(url=url,headers=headers,auth=auth,data=data2)
  print(CREATE_RELEASE_RESPONSE.content)


# MOVE ISSUES TO QA TESTING and Assign issue
jira=JIRA('https://amagiengg.atlassian.net',basic_auth=auth)
for item in data['Tickets']:
	URL_QA_TESTING=base_url+ISSUE+"/"+item+"/transitions"
	data_qa=json.dumps(PAYLOAD_QA_TEST)
	MOVE_TO_QA=requests.post(url=URL_QA_TESTING,headers=headers,auth=auth,data=data_qa)
	issue=jira.issue(item)
	jira.assign_issue(issue, 'Ravikiran Muniraj')





