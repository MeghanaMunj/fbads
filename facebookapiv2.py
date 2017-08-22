import requests
import facebookads.api as fbapi
from facebookads.adobjects.adaccount import AdAccount
from facebookads.adobjects.adsinsights import AdsInsights
from facebookads.adobjects import user
from facebookads.adobjects.campaign import Campaign
import os 
import csv
import const
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
        return self.campaigns

    def get_insights(self):
        lt_insights = self.adacc.get_insights()
        return lt_insights
    
class FbCampaign(object):
    def __init__(self,adcampaign_id,adsapi):
        self.campaign = Campaign(fbid=adcampaign_id,api=adsapi)
        self.campaignid = adcampaign_id
    def get_insights(self,i_fields,i_params):
        
        #print('Inside the method just before calling---------',i_pagetype)
        #{'field':'adset.placement.page_types','operator':'ANY','value': i_pagetype}
        #{'field':'updated_time','operator':'GREATER_THAN','value':1501266600000}
        #get the breakdown values
        lt_breakdown = []
        lt_breakdown = i_params.get(const.CONFIG_FIELDS.FBBREAKDOWN)
        # get the hourly breakdown values separately and then add it.
        # need to confirm if the breakdown and hourly breakdown is not possible togther ?????????????????
        lt_brkhour = []
        lt_brkhour = i_params.get(const.CONFIG_FIELDS.FBBREAKDOWNHR)
        lt_breakdown = lt_breakdown + lt_brkhour
        lt_parameters = {
            'time_range': {'since':i_params.get('since'),'until':i_params.get('until')},                        
            'filtering': [
                          {'field':'objective','operator':'IN','value':i_params.get(const.CONFIG_FIELDS.FBObjective)},
                          {'field':'buying_type','operator':'IN','value':i_params.get(const.CONFIG_FIELDS.FBBuyingType)},                          
                          
                           ],
            'breakdowns': lt_breakdown}
        #print('Just before getting insights -----------------------------',lt_parameters)      
        self.insights = self.campaign.get_insights(fields=i_fields, params=lt_parameters)
        print('Insights for Campaign -------------------------',self.campaignid)
        print(self.insights)
        lt_fields = []
        lt_output = []
        for lw_insights in self.insights:
            #print('FB insights Raw --------------***************',lw_insights)
            lw_row = {}
            for lw_fields, lv_value in lw_insights.iteritems():
                #print('Field ----------',lw_fields,'Value --------------------',lv_value)
                if lw_fields in lt_breakdown:
                    lw_row[lw_fields] = lv_value
                    if not(lw_fields in lt_fields):
                        lt_fields.append(lw_fields)
                else:
                    # if Type is list then get each field in the list
                    if type(lv_value) == type(lt_fields):
                        #print('Fields are -------',lw_fields)                    
                        lt_list = lv_value
                        #print('List entries are ----------',lt_list)
                        for lw_list in lt_list:
                            #print('List entry-----------', lw_list)
                            lv_fieldname = lw_fields + '_' + lw_list.get('action_type')
                            #print(lw_fields,'--------Field name in list -----------',lv_fieldname)
                            lv_fieldvalue = lw_list.get('value')
                            lw_row[lv_fieldname] = lv_fieldvalue
                            if not (lv_fieldname in lt_fields):
                                lt_fields.append(lv_fieldname)                  
                    else:
                        lw_row[lw_fields] = lv_value
                        if not(lw_fields in lt_fields):
                            lt_fields.append(lw_fields)
                    
            lt_output.append(lw_row)
            #print('Row ------------------',lw_row)
        
        return lt_output,lt_fields
                               
    
def get_fields(i_group):
    cwd = os.path.dirname(os.path.realpath(__file__))
    lv_filepath = os.path.join(cwd, 'fieldgroups.csv')
    print('File to be opened is -----------------------',lv_filepath)
    print('Group to be checked is ------',i_group)
    lt_group = []
    if i_group == 'CampaignPerformance':
        lt_group = ['Campaign','setting','Performance']
    elif i_group == 'CampaignEngagement-PagePost':
        lt_group = ['Campaign','setting','Engagement-PagePost']
    elif i_group == 'CampaignDelivery':
        lt_group = ['Campaign','setting','Delivery']
    elif i_group == 'CampaignVideoEngagement':
        lt_group = ['Campaign','setting','VideoEngagement']
    elif i_group == 'CampaingAppEngagement':
        lt_group = ['Campaign','setting','AppEngagement']
    elif i_group == 'CampaignCarouselEngagement':
        lt_group = ['Campaign','setting','CarouselEngagement']
    elif i_group == 'CampaignPerformanceandClicks':
        lt_group = ['Campaign','setting','PerformanceandClicks']
    elif i_group == 'CampaignCrossDevice':
        lt_group = ['Campaign','setting','CrossDevice']
    elif i_group == 'CampaignMessengerEngagement':
        lt_group = ['Campaign','setting','MessengerEngagement']
    elif i_group == 'All':
        lt_group = ['Campaign','setting','MessengerEngagement','Performance','Engagement-PagePost','Delivery','VideoEngagement','AppEngagement','CarouselEngagement','PerformanceandClicks','CrossDevice']
    lt_fields = []
    lv_file = open(lv_filepath, 'rb')
    lt_flds = csv.DictReader(lv_file)
    for lw_flds in lt_flds:
        if lw_flds.get('group') in lt_group:
            lv_fname = lw_flds.get('fname')
            if not lv_fname in lt_fields:
                lt_fields.append(lv_fname)            
    
    return lt_fields

'''        
def get_formattedfields(i_file):
    cwd = os.path.dirname(os.path.realpath(__file__))
    lv_file = os.path.join(cwd, i_file)
    lt_fields = [lw_fields.strip() for lw_fields in open(lv_file).read().split('\n')]
    items = []
    for lw_fields in lt_fields:
         items.append({"selectable": False,
                          'selected': True,
                              "name": lw_fields,
                              'value': lw_fields
                              })      
    
    return items
    
'''
