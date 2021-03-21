# Importing libraries
import requests
from requests import get, post
import json
from requests import get, post
from dateutil import parser
import datetime
import re
import lxml
import bs4
from bs4 import BeautifulSoup
import os

# Module variables to connect to moodle api:
## Insert token and URL for your site here. 
## Mind that the endpoint can start with "/moodle" depending on your installation.
KEY = "bc7ad59923ad95f17dd955868790ccb5" 
URL = "http://f0ae7213ef73.eu.ngrok.io"
ENDPOINT="/webservice/rest/server.php"

def rest_api_parameters(in_args, prefix='', out_dict=None):
    """Transform dictionary/array structure to a flat dictionary, with key names
    defining the structure.
    Example usage:
    >>> rest_api_parameters({'courses':[{'id':1,'name': 'course1'}]})
    {'courses[0][id]':1,
     'courses[0][name]':'course1'}
    """
    if out_dict==None:
        out_dict = {}
    if not type(in_args) in (list,dict):
        out_dict[prefix] = in_args
        return out_dict
    if prefix == '':
        prefix = prefix + '{0}'
    else:
        prefix = prefix + '[{0}]'
    if type(in_args)==list:
        for idx, item in enumerate(in_args):
            rest_api_parameters(item, prefix.format(idx), out_dict)
    elif type(in_args)==dict:
        for key, item in in_args.items():
            rest_api_parameters(item, prefix.format(key), out_dict)
    return out_dict

def call(fname, **kwargs):
    """Calls moodle API function with function name fname and keyword arguments.
    Example:
    >>> call_mdl_function('core_course_update_courses',
                           courses = [{'id': 1, 'fullname': 'My favorite course'}])
    """
    parameters = rest_api_parameters(kwargs)
    parameters.update({"wstoken": KEY, 'moodlewsrestformat': 'json', "wsfunction": fname})
    #print(parameters)
    response = post(URL+ENDPOINT, data=parameters).json()
    if type(response) == dict and response.get('exception'):
        raise SystemError("Error calling Moodle API\n", response)
    return response
    
def find_resource_links():
    '''Finds relevent resource links to views for resources on 
	given moodle course source code coming in through url.'''

    res = requests.get("http://f0ae7213ef73.eu.ngrok.io")
    soup=BeautifulSoup(res.text, "lxml")
    resource_links=[]
    for li in soup.findAll('li', class_=re.compile('no-overflow')):
        for a in li.findAll('a'):
            resource_links.append(a.get('href'))
    return resource_links

################################################
# Rest-Api classes
################################################

class LocalGetSections(object):
    """Get settings of sections. Requires courseid. Optional you can specify sections via number or id."""
    def __init__(self, cid, secnums = [], secids = []):
        self.getsections = call('local_wsmanagesections_get_sections', courseid = cid, sectionnumbers = secnums, sectionids = secids)

class LocalUpdateSections(object):
    """Updates sectionnames. Requires: courseid and an array with sectionnumbers and sectionnames"""
    def __init__(self, cid, sectionsdata):
        self.updatesections = call('local_wsmanagesections_update_sections', courseid = cid, sections = sectionsdata)

       
# Scanning the existing folders
os.getcwd()
os.listdir()
for folder, sub_folders, files in os.walk("Sem1"):
    print("currently looking at folder:"+ folder)
    print('\n')
    print("The subfolders are: ")
    for sub_fold in sub_folders:
        print("\t Subfolder: "+sub_fold)

    print('\n')
    print("THE FILES ARE : ")
    for f in files:
        print("\t Files: "+f)
    print('\n')
    
courseid = "10" # Exchange with valid id.
# Get all sections of the course.
sec = LocalGetSections(courseid)

# Get sections ids of the course with the given numbers.
sec = LocalGetSections(courseid, [0,1,2,3,4,5,6])
# Output readable JSON, but print only summary
print(json.dumps(sec.getsections[1]['summary'], indent=4, sort_keys=True))

# Split the section name by dash and convert the date into the timestamp, it takes the current year, so think of a way for making sure it has the correct year!
month = parser.parse(list(sec.getsections)[1]['name'].split('-')[-1])
# Show the resulting timestamp
print(month)
# Extract the week number from the start of the calendar year
print(month.strftime("%V"))

#  Assemble the payload
data = [{'type': 'num', 'section': 0, 'summary': '', 'summaryformat': 1, 'visible': 1 , 'highlight': 0, 'sectionformatoptions': [{'name': 'level', 'value': '1'}]}]

# Assemble the correct summary
summary = '<a href="https://neelimatadisetti.github.io/ca3-proj/wk1/">Week1</a><br> <a href="https://neelimatadisetti.github.io/ca3-proj/wk1/wk1.pdf" <="" a="">PDF</a><br> <a href="https://drive.google.com/drive/folders/1pFHUrmpLv9gEJsvJYKxMdISuQuQsd_qX">Class Recording</a><br>'

# Assign the correct summary
data[0]['summary'] = summary

# Set the correct section number
data[0]['section'] = 1

# Write the data back to Moodle
sec_write = LocalUpdateSections(courseid, data)

sec = LocalGetSections(courseid)
# Output readable JSON.
print(json.dumps(sec.getsections[1]['summary'], indent=4, sort_keys=True))

