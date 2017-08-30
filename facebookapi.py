import requests
import facebookads.api as fbapi
from facebookads.adobjects.adaccount import AdAccount
from facebookads.adobjects.adsinsights import AdsInsights
from facebookads.adobjects.adset import AdSet
from facebookads.adobjects import user
from facebookads.adobjects.campaign import Campaign
import os 
import csv
import const
from datetime import datetime
from datetime import timedelta
import pydash

def get_attribtues_in_class(i_object):
    lt_attributes = []
    lt_values  = i_object.__dict__
    for lv_value in lt_values:
        if lv_value[:2] != '__':
            #print(lv_value,'----------',lt_values.get(lv_value))
            lt_attributes.append(lt_values.get(lv_value))
    return lt_attributes
class FbGraph(object):
    def __init__(self,i_access_token,i_api_config):
        #initiate the session and update the headers
        self.client = requests.Session()
        self.client.headers.update({
              "Authorization": "Bearer %s" % i_access_token,
            "Content-Type": "application/json"
          })
        self.access_token = i_access_token
        self.apid = i_api_config.get("client_id")
        self.ap_secret = i_api_config.get("client_secret")
        self.adsapi = fbapi.FacebookAdsApi.init(app_id= self.apid, app_secret = self.ap_secret, api_version='v2.10', access_token = self.access_token)
        
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
    def get_campaign_list(self):
        self.camplist = []
        self.camplist = self.adacc.get_campaigns(fields=['id', 'name'])
    def get_campaigns(self):
        lt_fields = get_attribtues_in_class(Campaign.Field)
        print('Fields for campaign are ------',lt_fields)
        lt_campaign = self.adacc.get_campaigns(fields=lt_fields)
        self.campaigns = {}
        print('result from method ----', lt_campaign)
        #self.campids = []
        #pydash.key_by(lt_campaign, 'id')
        
        for lw_campaign in lt_campaign:
            print('-------',lw_campaign)
            self.campaigns[lw_campaign['id']] = lw_campaign
            #self.campids.append(lw_campaign['id'])
        print('Campaigns are --------------------',self.campaigns)
        
        #print('Camp ids are --------------',self.campids)
    def get_adset_list(self):
        self.adsetlist = []
        self.adsetlist = self.adacc.get_ad_sets(fields=['id','name'])
    def get_adsets(self):
        lt_fields = get_attribtues_in_class(AdSet.Field)
        print('Field for Adsets are ------------------------', lt_fields)
        lt_adsets = self.adacc.get_ad_sets(fields=lt_fields)
        #self.adsetids = []
        self.adsets = {}
        for lw_adset in lt_adsets:
            self.adsets[lw_adset['id']] = lw_adset
            #self.adsetids.append(lw_adset['id'])
        print('Adsets are --------------------------',self.adsets)
        
    def filter_campaign(self,i_objective=None,i_buyingtype=None):
        lt_filtercampobj = []
        lt_filtercamp = []
        for lw_camp in self.campaigns:
            if lw_camp.get('objective') in i_objective:
                lt_filtercampobj.append(lw_camp)
        for lw_camp in lt_filtercamp:
            if lw_camp.get('buying_type') in i_buyingtype:
                lt_filtercamp.append(lw_camp)
        return lt_filtercamp

    
class FbObject(object):
    def __init__(self,i_id,adsapi,i_object):
        self.id = id     
        self.insights = []
        self.obj = i_object
    def get_params(self,i_params):
        #get the breakdown values
        self.lt_breakdown = []
        self.lt_breakdown = i_params.get(const.CONFIG_FIELDS.FBBREAKDOWN)
        self.lt_parameters = {
            #'time_range': {'since':i_params.get('since'),'until':i_params.get('until')},                        
            #'filtering': [
            #              {'field':'objective','operator':'IN','value':i_params.get(const.CONFIG_FIELDS.FBObjective)},
            #              {'field':'buying_type','operator':'IN','value':i_params.get(const.CONFIG_FIELDS.FBBuyingType)},                                                    
            #               ],
            'breakdowns': self.lt_breakdown,
            
             #'action_attribution_windows':['1d_view','7d_view','28d_view','default']
        }
        
    def get_insights(self,i_fields,i_params):
        
        #self.get_params(i_params)
        #self.daterange = get_date_range(i_since=i_params.get('since'), i_until=i_params.get('until'))
        self.daterange = get_date_range(i_since='2017-07-30',i_until='2017-08-01')
        print('Date range is ---------------',self.daterange)
        
        #self.insights = []
        
        #print('Just before getting insights -----------------------------',lt_parameters)      
        #self.insights = self.campaign.get_insights(fields=i_fields, params=lt_parameters)
        #print('Insights for Campaign -------------------------',self.campaignid)
        #print(self.insights)
    
    def get_insight_formatted(self):        
        lt_fields = []
        lt_output = []
        for lw_insights in self.insights:
            #print('FB insights Raw --------------***************',lw_insights)
            lw_row = {}
            for lw_fields, lv_value in lw_insights.iteritems():
                #print('Field ----------',lw_fields,'Value --------------------',lv_value)
                if lw_fields in self.lt_breakdown:
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
                            lv_fieldname = lw_fields + ':' + lw_list.get('action_type')
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
        print('Output insights are ----------------',lt_output)
        return lt_output,lt_fields
                               
class FbCampaign(FbObject):
    def __init__(self,i_id,adsapi,i_object):
        FbObject.__init__(self,i_id,adsapi,i_object)
        self.campaign = Campaign(fbid=i_id,api=adsapi)
    def get_params(self,i_params):
        FbObject.get_params(self,i_params)
        self.lt_parameters['filtering'] = [
                      {'field':'objective','operator':'IN','value':i_params.get(const.CONFIG_FIELDS.FBObjective)},
                      {'field':'buying_type','operator':'IN','value':i_params.get(const.CONFIG_FIELDS.FBBuyingType)},                                                    
                       ]
        
    def get_insights(self,i_fields,i_params):
        self.get_params(i_params)
        FbObject.get_insights(self,i_fields,i_params)
        for lw_daterange in self.daterange:
            self.lt_parameters['time_range'] = { 'since': lw_daterange,'until': lw_daterange}
            lt_insight = []            
            lt_insight = self.campaign.get_insights(fields=i_fields, params=self.lt_parameters)
            #print('Day wise insights are ---------------------------', lw_daterange,'------', lt_insight)
            for lw_insight in lt_insight:
                lw_insight['Day'] = lw_daterange
                lw_insight.update(self.obj)
                self.insights.append(lw_insight)                
class FBAdset(FbObject):
    def __init__(self,i_id,adsapi,i_object):
        FbObject.__init__(self,i_id,adsapi,i_object)
        self.Adset = AdSet(fbid=i_id,api=adsapi)
    def get_params(self,i_params):
        FbObject.get_params(self,i_params)
        self.lt_parameters['filtering'] = [ 
            {'field':'adset.placement.page_types','operator':'ANY','value': i_params.get(const.CONFIG_FIELDS.FBPageType)}
            ]
    def get_insights(self,i_fields,i_params):
        self.get_params(i_params)
        FbObject.get_insights(self,i_fields,i_params)
        #self.insights = self.Adset.get_insights(fields=i_fields, params=self.lt_parameters)
        #print('Insights for the Adset are --------------',self.insights)
        
        for lw_daterange in self.daterange:
            self.lt_parameters['time_range'] = { 'since': lw_daterange,'until': lw_daterange}
            print('Parameters just before calling the method ----------------',self.lt_parameters)            
            lt_insight = []            
            lt_insight = self.Adset.get_insights(fields=i_fields, params=self.lt_parameters)
            print('Adsets Insights for day ----', lw_daterange, '--------')
            print(lt_insight)
            for lw_insight in lt_insight:
                lw_insight['Day'] = lw_daterange
                lw_insight.update(self.obj)
                self.insights.append(lw_insight)       
                
def get_fields(i_group):
    print('Group --------------------------------',i_group)
    print('Infields -------------------------', const.gt_infields)
    lt_outdisplay = []
    lt_fields = const.gt_infields.get(i_group)
    for lv_key,lw_infields in lt_fields.iteritems():
        if len(lw_infields) == 0:      
            
            lt_outdisplay.append(lv_key)
        else:
            for lw_row in lw_infields:
                lt_outdisplay.append(lv_key + ':' + lw_row)
    
    return lt_outdisplay
def get_field_description(i_fname):    

    return const.gt_fielddesc.get(i_fname)

def get_date_range(i_since,i_until):
    lv_sincedate = datetime.strptime(i_since,'%Y-%m-%d')
    print('Since date - ', lv_sincedate)
    
    lv_untildate = datetime.strptime(i_until,'%Y-%m-%d')
    print('Until Date - ', lv_untildate)
    lt_dates = []
    while lv_sincedate <= lv_untildate:
        lt_dates.append(lv_sincedate.date().strftime('%Y-%m-%d'))
        lv_sincedate = lv_sincedate + timedelta(days = 1)
        #print('After adding a day ----', lv_sincedate)
        
    #print('List of dates is as follows -------------------', lt_dates)
    
    return lt_dates
    '''
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
