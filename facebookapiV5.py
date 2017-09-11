import requests
import facebookads.api as fbapi
from facebookads.adobjects.adaccount import AdAccount
from facebookads.adobjects.adsinsights import AdsInsights
from facebookads.adobjects.adset import AdSet
from facebookads.adobjects import user
from facebookads.adobjects.campaign import Campaign
from facebookads.adobjects.ad import Ad
import os
import csv
import const
from datetime import datetime
from datetime import timedelta
import pydash


def get_attribtues_in_class(i_object):
    lt_attributes = []
    lt_values = i_object.__dict__
    for lv_value in lt_values:
        if lv_value[:2] != '__':
            # print(lv_value,'----------',lt_values.get(lv_value))
            lt_attributes.append(lt_values.get(lv_value))
    return lt_attributes


class FbGraph(object):
    def __init__(self, i_access_token, i_api_config):
        # initiate the session and update the headers
        self.client = requests.Session()
        self.client.headers.update({
            "Authorization": "Bearer %s" % i_access_token,
            "Content-Type": "application/json"
        })
        self.access_token = i_access_token
        self.apid = i_api_config.get("client_id")
        self.ap_secret = i_api_config.get("client_secret")
        self.adsapi = fbapi.FacebookAdsApi.init(app_id=self.apid,
                                                app_secret=self.ap_secret,
                                                api_version='v2.10',
                                                access_token=self.access_token)

    def get_user_name(self):
        lv_url = 'https://graph.facebook.com/v2.10/me'
        lv_response = self.client.get(lv_url)
        if lv_response.status_code != 200:
            return {
                "status": 1,
                "errmsg": "Did not receive a valid response "}
        else:
            lt_json = lv_response.json()
            return {"status": 0,
                    "user": lt_json.get('name') + '-(' + lt_json.get(
                        'id') + ')'}
    
    def get_client(self):
        return self.client

    def get_adaccount(self):
        self.user = user.User('me', self.adsapi)
        lt_fields = [
            'id',
            'name',
            'account_id']
        
        self.adaccounts = self.user.get_ad_accounts(fields=lt_fields)
        
        return self.adaccounts

    def get_adsapi(self):
        return self.adsapi


class FbAdaccount(object):
    def __init__(self, adsapi, adaccount_id):
        self.adacc = AdAccount(fbid=adaccount_id, api=adsapi)

    def get_campaign_list(self):
        self.camplist = []
        self.camplist = self.adacc.get_campaigns(fields=['id', 'name'])
        for lw_camp in self.camplist:
            print('campaing ------',lw_camp)
            print('Type of camp -------' ,type(lw_camp))
    def get_campaigns(self):
        lt_fields = get_attribtues_in_class(Campaign.Field)
        #print('Fields for campaign are ------', lt_fields)
        lt_campaign = self.adacc.get_campaigns(fields=lt_fields)
        self.campaigns = {}
        #print('result from method ----', lt_campaign)
        for lw_campaign in lt_campaign:
            print('-------', lw_campaign)
            print('Type of campaign is ---------', type(lw_campaign))
            self.campaigns[lw_campaign['id']] = lw_campaign
        print('Campaigns are --------------------', self.campaigns)


    def get_adset_list(self):
        self.adsetlist = []
        self.adsetlist = self.adacc.get_ad_sets(fields=['id', 'name'])

    def get_adsets(self):
        lt_fields = get_attribtues_in_class(AdSet.Field)
        #print('Field for Adsets are ------------------------', lt_fields)
        lt_adsets = self.adacc.get_ad_sets(fields=lt_fields)
        self.adsets = {}
        for lw_adset in lt_adsets:
            self.adsets[lw_adset['id']] = lw_adset
        #print('Adsets are --------------------------', self.adsets)

    def get_ads_list(self):
        self.adslist = []
        self.adslist = self.adacc.get_ads(fields=['id','name'])

    def get_ads(self):
        lt_fields = get_attribtues_in_class(Ad.Field)
        lt_ads = self.adacc.get_ads(fields=lt_fields)
        self.ads = {}
        for lw_ads in lt_ads:
            self.ads[lw_ads['id']] = lw_ads

    def filter_campaign(self, i_objective=None, i_buyingtype=None):
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
    def __init__(self, i_id, adsapi, i_object):
        self.id = id
        self.insights = []
        self.obj = i_object

    def get_params(self, i_params):
        # get the breakdown values
        self.lt_breakdown = []        
        lv_breakdown = i_params.get(const.CONFIG_FIELDS.FBBREAKDOWN)
        if lv_breakdown in const.gt_breakdown:
            self.lt_breakdown = const.gt_breakdown.get(lv_breakdown)
        elif lv_breakdown == None:
            self.lt_breakdown = []
        else:
            self.lt_breakdown = [ lv_breakdown]
        print('Breakdown value ----------------------------',self.lt_breakdown)
        self.lt_parameters = {
            # 'time_range': {'since':i_params.get('since'),'until':i_params.get('until')},
            # 'filtering': [
            #              {'field':'objective','operator':'IN','value':i_params.get(const.CONFIG_FIELDS.FBObjective)},
            #              {'field':'buying_type','operator':'IN','value':i_params.get(const.CONFIG_FIELDS.FBBuyingType)},                                                    
            #               ],
            'breakdowns': self.lt_breakdown,
            
            # 'action_attribution_windows':['1d_view','7d_view','28d_view','default']
        }

    def get_insights(self, i_fields, i_params):
        
        # self.get_params(i_params)
        # self.daterange = get_date_range(i_since=i_params.get('since'), i_until=i_params.get('until'))
        self.daterange = get_date_range(i_since='2017-07-30',
                                        i_until='2017-08-01')
        print('Date range is ---------------', self.daterange)

        # self.insights = []

        # print('Just before getting insights -----------------------------',lt_parameters)
        # self.insights = self.campaign.get_insights(fields=i_fields, params=lt_parameters)
        # print('Insights for Campaign -------------------------',self.campaignid)
        # print(self.insights)
    
    def get_insight_formatted(self,i_screenfield):
        lt_fields = []
        lt_output = []
        for lw_insights in self.insights:
            #print('FB insights Raw --------------***************',lw_insights)
            #print('Raw Object -------------------------------',self.obj)
            lw_row = {}
            
            for lv_fname in self.obj:
                lv_fvalue = self.obj.get(lv_fname)
                lw_row[lv_fname] = lv_fvalue
                print('Field name ------',lv_fname,'------value ------',lv_fvalue)
                if not (lv_fname in lt_fields):
                    lt_fields.append(lv_fname)
            for lw_screenfield in i_screenfield:
                lv_pos = lw_screenfield.find(":")
                if lv_pos > 0:
                    lv_pre = lw_screenfield[:lv_pos]
                    lv_post = lw_screenfield[lv_pos+1:]
                    #print('Screen feild is -------------------',lw_screenfield)
                    #if the pre field is action field then get the action value 
                    if lv_pre in const.gt_actionfields:
                        lt_actions = []
                        lt_actions = lw_insights.get(lv_pre)
                        #print('Actions are --------', lt_actions)
                        lv_index = pydash.find_index(lt_actions,['action_type',lv_post])
                        if lv_index >= 0 :
                            lw_row[lw_screenfield] = lt_actions[lv_index].get("value")
                        if not (lw_screenfield in lt_fields):
                            lt_fields.append(lw_screenfield)
                else:
                    lv_pre = lw_screenfield
                    lv_post = ""
                    lw_row[lw_screenfield] = lw_insights.get(lw_screenfield)
                    if not (lw_screenfield in lt_fields): 
                        lt_fields.append(lw_screenfield)
            if self.lt_breakdown != None:
                for lw_breakdown in self.lt_breakdown:
                    print('Break down ------>', lw_breakdown,'----value-----',lw_insights.get(lw_breakdown))
                    lw_row[lw_breakdown] = lw_insights.get(lw_breakdown)
                    if not (lw_breakdown in lt_fields):
                        lt_fields.append(lw_breakdown)
                        print("fields after addition of breakdown ------------",lt_fields)
            
                
            

            lt_output.append(lw_row)
            # print('Row ------------------',lw_row)
        #print('Output insights are ----------------', lt_output)
        return lt_output, lt_fields


class FbCampaign(FbObject):
    def __init__(self, i_id, adsapi, i_object):
        FbObject.__init__(self, i_id, adsapi, i_object)
        self.campaign = Campaign(fbid=i_id, api=adsapi)

    def get_params(self, i_params):
        #get the super params 
        FbObject.get_params(self, i_params)
        #campaign specific parameters 
        self.lt_parameters['filtering'] = [
            {'field': 'objective', 'operator': 'IN',
             'value': i_params.get(const.CONFIG_FIELDS.FBObjective)},
            {'field': 'buying_type', 'operator': 'IN',
             'value': i_params.get(const.CONFIG_FIELDS.FBBuyingType)},
        ]

    def get_insights(self, i_fields, i_params):
        #get the parameters initialized 
        self.get_params(i_params)
        #call the super insights method 
        FbObject.get_insights(self, i_fields, i_params)
        #for selected date range loop for each day
        for lw_daterange in self.daterange:
            # set the time range as specific day 
            self.lt_parameters['time_range'] = {'since': lw_daterange,
                                                'until': lw_daterange}
            lt_insight = []
            #get the insights for that specific day
            lt_insight = self.campaign.get_insights(fields=i_fields,
                                                    params=self.lt_parameters)
            #print('Day wise insights are ---------------------------', lw_daterange,'------', lt_insight)
            #for each date wise insights append the date with field "Day"
            for lw_insight in lt_insight:
                lw_insight['Day'] = lw_daterange
                #add the Object details to dictionary --- in this case it will be the feilds specific to the campaign 
                lw_insight.update(self.obj)
                self.insights.append(lw_insight)


class FBAdset(FbObject):
    def __init__(self, i_id, adsapi, i_object):
        FbObject.__init__(self, i_id, adsapi, i_object)
        self.Adset = AdSet(fbid=i_id, api=adsapi)

    def get_params(self, i_params):
        #super parameters initialize 
        FbObject.get_params(self, i_params)
        #parameter specific to the Adset 
        self.lt_parameters['filtering'] = [
            {'field': 'adset.placement.page_types', 'operator': 'ANY',
             'value': i_params.get(const.CONFIG_FIELDS.FBPageType)}
        ]

    def get_insights(self, i_fields, i_params):
        #intialize the parameters before calling the get_insights
        self.get_params(i_params)
        #call super get_insights
        FbObject.get_insights(self, i_fields, i_params)
        # self.insights = self.Adset.get_insights(fields=i_fields, params=self.lt_parameters)
        # print('Insights for the Adset are --------------',self.insights)
        
        #for each day in selected date range 
        for lw_daterange in self.daterange:
            #set the time_range parameter
            self.lt_parameters['time_range'] = {'since': lw_daterange,
                                                'until': lw_daterange}
            lt_insight = []
            #get the insights for that day
            lt_insight = self.Adset.get_insights(fields=i_fields,
                                                 params=self.lt_parameters)
            #print('Adsets Insights for day ----', lw_daterange, '--------')
            #print(lt_insight)
             
            for lw_insight in lt_insight:
                #add the day field in the output since its fetched daywise 
                lw_insight['Day'] = lw_daterange
                #add the Object details to dictionary --- in this case it will be the feilds specific to the Adset 
                lw_insight.update(self.obj)
                self.insights.append(lw_insight)


class FBAds(FbObject):
   def __init__(self, i_id, adsapi, i_object):
        FbObject.__init__(self, i_id, adsapi, i_object)
        self.Ads = Ad(fbid=i_id, api=adsapi)
    
   def get_params(self, i_params):
       #get the super parameter
       FbObject.get_params(self, i_params)
       #Ad specific parameter 
       self.lt_parameters['filtering'] = [
           {'field': 'adset.placement.page_types', 'operator': 'ANY',
            'value': i_params.get(const.CONFIG_FIELDS.FBPageType)}
       ]
   def get_insights(self, i_fields, i_params):
       #get the parameter set before calling the insights
       self.get_params(i_params)
       #get the super insights 
       FbObject.get_insights(self, i_fields, i_params)
       #for each day in selected date range 
       for lw_daterange in self.daterange:
           #set the time_range parameter 
           self.lt_parameters['time_range'] = {'since': lw_daterange,
                                               'until': lw_daterange}
           print('Parameters just before calling the method ----------------',
                 self.lt_parameters)
           lt_insight = []
           #get the insights
           lt_insight = self.Ads.get_insights(fields=i_fields,
                                                params=self.lt_parameters)
           print('Ads Insights for day ----', lw_daterange, '--------')
           print(lt_insight)
           #for each insights add the date field since its fetched date wise 
           for lw_insight in lt_insight:
               #Day field is added 
               lw_insight['Day'] = lw_daterange
               #add the Object details to dictionary --- in this case it will be the feilds specific to the Ads
               lw_insight.update(self.obj)
               self.insights.append(lw_insight)
    
def get_fields(i_group):
    print('Group --------------------------------', i_group)
    print('Infields -------------------------', const.gt_infields)
    lt_outdisplay = []
    lt_fields = const.gt_infields.get(i_group)
    for lv_key, lw_infields in lt_fields.iteritems():
        if len(lw_infields) == 0:
            
            lt_outdisplay.append(lv_key)
        else:
            for lw_row in lw_infields:
                lt_outdisplay.append(lv_key + ':' + lw_row)
    
    return lt_outdisplay


def get_field_description(i_fname):
    return const.gt_fielddesc.get(i_fname)


def get_date_range(i_since, i_until):
    lv_sincedate = datetime.strptime(i_since, '%Y-%m-%d')
    print('Since date - ', lv_sincedate)
    
    lv_untildate = datetime.strptime(i_until, '%Y-%m-%d')
    print('Until Date - ', lv_untildate)
    lt_dates = []
    while lv_sincedate <= lv_untildate:
        lt_dates.append(lv_sincedate.date().strftime('%Y-%m-%d'))
        lv_sincedate = lv_sincedate + timedelta(days=1)
        # print('After adding a day ----', lv_sincedate)

    # print('List of dates is as follows -------------------', lt_dates)
    
    return lt_dates
