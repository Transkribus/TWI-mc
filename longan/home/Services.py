'''
Created on Aug 20, 2017

@author: albert
'''

import requests
#workaround for insecure platform warnings...
#http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package
#import requests.packages.urllib3 
#requests.packages.urllib3.disable_warnings()

from transkribus import services

import xmltodict


# class TranskribusUser:
#     def __init__(self, xmlStr):
#         dic = xmltodict.parse(xmlStr)
#         self.user = dic.get('trpUserLogin')
#         self.isAdmin = dic.get('isAdmin')

        
class Services:
    
    BASE_URL = "https://transkribus.eu/TrpServer/rest"
    
    def __init__(self):
        self.s = requests.Session()
     
     
    def Logout(self):
        url = self.BASE_URL +'/auth/logout'
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        self.s.post(url, verify=False, headers=headers)
        try: self.cleanPersistentSession()
        except: pass
    
    def Login(self, user, pw):
        api = services.TranskribusAPI()
        r = api.login(username=user, password=pw)
        #print(xmltodict.parse(r.text))
        
#         doc = api.get_doc_by_id(COLL_ID, DOC_ID)
# 
#         for page in doc.pages:
# 
#             most_recent_transcript = page.most_recent_transcript
# 
#             for transcript in page.transcripts:
#                 if transcript.id != most_recent_transcript.id:
#                     print("Not the most recent transcript:", transkript.url)
    
        if r.status_code != 200: #ok
            raise Exception("NO 200")
        
        return xmltodict.parse(r.text)
        