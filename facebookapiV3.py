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
    def get_campaigns(self):
        lt_fields = get_attribtues_in_class(Campaign.Field)
        print('Fields for campaign are ------',lt_fields)
        self.campaigns = self.adacc.get_campaigns(fields=lt_fields)
        print('Campaigns are --------------------',self.campaigns)
        return self.campaigns
    def get_adsets(self):
        lt_fields = get_attribtues_in_class(AdSet.Field)
        print('Field for Adsets are ------------------------', lt_fields)
        self.adsets = self.adacc.get_ad_sets(fields=lt_fields)
        print('Adsets are --------------------------',self.adsets)
        return self.adsets
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
    def get_insights(self):
        lt_insights = self.adacc.get_insights()
        return lt_insights
    
class FbCampaign(object):
    def __init__(self,adcampaign_id,adsapi):
        self.campaign = Campaign(fbid=adcampaign_id,api=adsapi)
        self.campaignid = adcampaign_id
    def get_insights(self,i_fields,i_params):
        

        #get the breakdown values
        lt_breakdown = []
        lt_breakdown = i_params.get(const.CONFIG_FIELDS.FBBREAKDOWN)
        lt_parameters = {
            'time_range': {'since':i_params.get('since'),'until':i_params.get('until')},                        
            'filtering': [
                          {'field':'objective','operator':'IN','value':i_params.get(const.CONFIG_FIELDS.FBObjective)},
                          {'field':'buying_type','operator':'IN','value':i_params.get(const.CONFIG_FIELDS.FBBuyingType)},                          
                          
                           ],
            'breakdowns': lt_breakdown,
            'level': 'campaign',
             'action_attribution_windows':['1d_view','7d_view','28d_view','default']
        }
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
        
        return lt_output,lt_fields
                               
    
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
