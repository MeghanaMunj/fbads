import requests
import facebookads.api as fbapi
from facebookads.adobjects.adaccount import AdAccount
from facebookads.adobjects.adsinsights import AdsInsights
from facebookads.adobjects import user
class FbGraph(object):
    def __init__(self,access_token,apid,ap_secret):
        #initiate the session and update the headers
        self.client = requests.Session()
        self.client.headers.update({
              "Authorization": "Bearer %s" % access_token,
            "Content-Type": "application/json"
          })
        self.access_token = access_token
        self.apid = apid
        self.ap_secret = ap_secret
        self.adsapi = fbapi.FacebookAdsApi.init(app_id= apid, app_secret = ap_secret, api_version='v2.10', access_token= self.access_token)
        
    def get_user_name(self):
        lv_url = 'https://graph.facebook.com/v2.10/me'
        lv_response = self.client.get(lv_url)
        if lv_response.status_code <> 200:
            return {
                 "status": 1,
                     "errmsg": "Did not receive a valid response "}
        else:
            lt_json = lv_response.json()
            return { "status":0, 
                      "user": lt_json.get('name') + '-(' + lt_json.get('id') + ')' }
    
    def get_client(self):
        return self.client
    def get_adaccount(self):
        self.user = user.User('me',self.adsapi)
        lt_fields = [
        'id',
        'name',
        'account_id']
        
        self.adaccounts = self.user.get_ad_accounts(fields=lt_fields)  
        
        return self.adaccounts
    def get_adsapi(self):
        return self.adsapi
        
class FbAdaccount(object):
    def __init__(self,adsapi,adaccount_id):
        self.adacc = AdAccount(fbid=adaccount_id,api=adsapi)
    def get_campaigns(self):
        lt_fields = ['id','name']
        self.campaigns = self.adacc.get_campaigns(fields=lt_fields)
        print('Campaigns are -------------------------------------------',self.campaigns)
        return self.campaigns

    
    
                               
        
        
   