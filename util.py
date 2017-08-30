# encoding: utf-8
import logging
import const
import sdk.const as sdkconst
from threep.base import DataYielder
import facebookapi
import csv
import datetime

log = logging


class fbadsDataYielder(DataYielder):
    def __init__(self, *args, **kwargs):
        self.knowledge = None
        self.batchId = kwargs.get(sdkconst.KEYWORDS.BATCH_ID)
        del kwargs[sdkconst.KEYWORDS.BATCH_ID]
        super(fbadsDataYielder, self).__init__(*args, **kwargs)
        self.adsapi = None

    def get_format_spec(self):
        """
            :return: format spec as a dictionary in the following format:
                {
                    UNIQUE_COLUMN_IDENTIFIER_1: FORMAT_SPEC for column1,
                    UNIQUE_COLUMN_IDENTIFIER_2: FORMAT_SPEC for column2
                    ...
                }
                FORMAT_SPEC examples:
                 for a DATE type column format could be : '%d-%b-%Y', so, it's entry
                 in the spec would look like:
                        COLUMN_IDENTIFIER: '%d-%b-%Y'

            """
        return {}

    def get_data_as_csv(self, file_path):
        """
            :param file_path: file path where csv results has to be saved
            :return: dict object mentioning csv download status, success/failure
            TODO: return dict format to be standardized
        """
        # get the feilds from identity config and ds config 
        lv_access_token = self.identity_config.get('access_token')
        lv_fbaccount = self.ds_config.get(const.CONFIG_FIELDS.FBACCOUNT)
        lv_fbopt = self.ds_config.get(const.CONFIG_FIELDS.FBOPT)
        lv_fbgroup = self.ds_config.get(const.CONFIG_FIELDS.FBCOLUMNGROUP)        
        lt_fields = self.get_selected_fields(const.CONFIG_FIELDS.FBFieldList)
        lv_adaccountid = self.ds_config.get(const.CONFIG_FIELDS.FBACCOUNT)
        
        #initialize the parameters to call the get_insights method 
        lt_params = {}
        lt_params[const.CONFIG_FIELDS.FBBREAKDOWN] = self.get_param(
            const.CONFIG_FIELDS.FBBREAKDOWN)
        lt_params['since'] = datetime.datetime.fromtimestamp(
            self.start_date[0]).date().strftime('%Y-%m-%d')
        lt_params['until'] = datetime.datetime.fromtimestamp(
            self.end_date).date().strftime('%Y-%m-%d')
        
        #initialize the adsapi and get instance of the FBAccount 
        lv_fbads = facebookapi.FbGraph(lv_access_token, self.api_config)
        self.adsapi = lv_fbads.get_adsapi()
        lv_adaccount = facebookapi.FbAdaccount(self.adsapi, lv_adaccountid)
        
        #initialize the common objects array 
        lt_object = []
        
        #if Ads options is selected 
        if lv_fbopt == 'Ads':
            #Ads specific parameter 
            #Page Type 
            lt_params[const.CONFIG_FIELDS.FBPageType] = self.ds_config.get(
                const.CONFIG_FIELDS.FBPageType)
            #get the ads selected on the screen 
            lt_adsid = self.ds_config.get(const.CONFIG_FIELDS.FBAds)
            
            #get all the ads details  in the selected FBAccount 
            lv_adaccount.get_ads()
            
            # for each ads id selected on the screen 
            for lw_adsid in lt_adsid:
                #get the ad details for that specific id 
                lw_ads = lv_adaccount.ads.get(lw_adsid)
                #instanitate the Ads object and append in the object list 
                lt_object.append(facebookapi.FBAds(lw_adsid,self.adsapi,lw_ads))
        # if Adset Option is selected 
        if lv_fbopt == 'AdSet':
            #ad set specific parameter 
            lt_params[const.CONFIG_FIELDS.FBPageType] = self.ds_config.get(
                const.CONFIG_FIELDS.FBPageType)
            #get the adsets selected on the screen 
            lt_adsetid = self.ds_config.get(const.CONFIG_FIELDS.FBAdset)

            #get all the adsets details in the selected FBAccount 
            lv_adaccount.get_adsets()
            
            #for each adsetid selected on the screen
            for lw_adsetid in lt_adsetid:
                #get the adset details for that specific id
                lw_adset = lv_adaccount.adsets.get(lw_adsetid)
                #instantiate the adset object and append in the object list 
                lt_object.append(facebookapi.FBAdset(lw_adsetid, self.adsapi,
                                               lw_adset))
                '''
                lv_adset.get_insights(i_fields=lt_fields, i_params=lt_params)
                
                lt_ins, lt_ftemp = lv_adset.get_insight_formatted()
                #collect insights in one final table 
                for lw_ins in lt_ins:
                    lt_insights.append(lw_ins)
                #field names should be collected for each call as the fields list might differ in insights fetched.
                for lw_ftemp in lt_ftemp:
                    if not(lw_ftemp in lt_fout):
                        lt_fout.append(lw_ftemp)'''
        #if campaign option is selected 
        if lv_fbopt == 'Campaign':
            #get the campaign specific filters 
            lt_params[const.CONFIG_FIELDS.FBObjective] = self.get_param(
                const.CONFIG_FIELDS.FBObjective)
            lt_params[const.CONFIG_FIELDS.FBBuyingType] = self.get_param(
                const.CONFIG_FIELDS.FBBuyingType)
            
            #get the campaign ids selected on the screen 
            lt_campaignid = self.ds_config.get('Campaigns')
            #get all the campaings attached to the FB Account 
            lv_adaccount.get_campaigns()
            
            for lw_campaignid in lt_campaignid:
                lw_campaign = lv_adaccount.campaigns.get(lw_campaignid)
                # get instance of the campaign and append it in the list 
                lt_object.append(facebookapi.FbCampaign(lw_campaignid, self.adsapi,
                                                     lw_campaign))
                '''
                lt_ftemp = []
                lt_ins = []
                # get insights for the campaign
                # this method returns the insights and the list of fields fetched for that call 
                lv_campaign.get_insights(i_fields=lt_fields, i_params=lt_params)
                lt_ins, lt_ftemp = lv_campaign.get_insight_formatted()
                # collect insights in one final table
                for lw_ins in lt_ins:
                    lt_insights.append(lw_ins)
                # field names should be collected for each call as the fields list might differ in insights fetched.
                for lw_ftemp in lt_ftemp:
                    if not (lw_ftemp in lt_fout):
                        lt_fout.append(lw_ftemp)
                '''
        #initialize the insights and the fields list 
        lt_insights = []
        lt_fout = []
        #For each object (this code is common for Ads, Adsets and Campaigns )
        for lw_object in lt_object:
            lt_ftemp = []
            lt_ins = []
            # get insights for the campaign
            # this method returns the insights and the list of fields fetched for that call 
            lw_object.get_insights(i_fields=lt_fields, i_params=lt_params)
            lt_ins, lt_ftemp = lw_object.get_insight_formatted()
            # collect insights in one final table
            for lw_ins in lt_ins:
                lt_insights.append(lw_ins)
            # field names should be collected for each call as the fields list might differ in insights fetched.
            for lw_ftemp in lt_ftemp:
                if not (lw_ftemp in lt_fout):
                    lt_fout.append(lw_ftemp)
            
        # open response file for each survey
        with open(file_path, 'w') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=lt_fout)
            # add the header
            writer.writeheader()
            for lw_insights in lt_insights:
                writer.writerow(lw_insights)
        
        return {}

    def _setup(self):
        """
            one time computations required to pull data from third party service.
            Apart from basic variable initialization done in __init__ method of
            same class, all other datapull readiness logic should be here
       """
        ds_config_key = self.config_key
        identity_key = self.identity_key
        self.identity_config = self.storage_handle.get(
            sdkconst.NAMESPACES.IDENTITIES,
            identity_key)

        self.ds_config = self.storage_handle.get(identity_key, ds_config_key)
        # self.campaign = self.storage_handle.get('FBCampaigns','FBCampaign' + self.ds_config.get(const.CONFIG_FIELDS.FBACCOUNT))
        lv_since = datetime.datetime.fromtimestamp(
            self.start_date[0]).date().strftime('%Y-%m-%d')
        lv_until = datetime.datetime.fromtimestamp(
            self.end_date).date().strftime('%Y-%m-%d')
        print('Since ------------------------------', lv_since)
        print('Until ---------------------------------', lv_until)

    def reset(self):
        """
            use this method to reset parameters, if needed, before pulling data.
            For e.g., in case, you are using cursors to pull, you may need to reset
            cursor object after sampling rows for metadata computation
            """
        pass

    def describe(self):
        """
            :return: metadata as a list of dictionaries in the following format
                {
                    'internal_name': UNIQUE COLUMN IDENTIFIER,
                    'display_name': COLUMN HEADER,
                    'type': COLUMN DATATYPE -  TEXT/DATE/NUMERIC
               }
        """
        return {}

    def get_param(self, i_name):
        lt_output = []
        lt_output = self.ds_config.get(i_name)
        return lt_output

    def get_selected_fields(self, i_name):
        # get the selecte feilds from ds config 
        lt_screenfield = self.get_param(i_name)
        lt_fields = []
        # add the default fields 
        lt_fields = lt_fields + const.gt_default
        # for each selected field 
        for lw_screenfield in lt_screenfield:
            lv_pos = lw_screenfield.find(':')
            # if colon is there then get the value before colon eg actions or cost_per_action_type 
            if lv_pos != -1:
                lt_fields.append(lw_screenfield[:lv_pos])
            else:
                lt_fields.append(lw_screenfield)
        return lt_fields