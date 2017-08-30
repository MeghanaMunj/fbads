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
        print('*****************DS config data *******************')
        # print(self.ds_config)
        # print(self.identity_config)
        print('Start date ---------', self.start_date)
        print('End date ---------', self.end_date)
        
        lv_access_token = self.identity_config.get('access_token')
        lv_fbaccount = self.ds_config.get(const.CONFIG_FIELDS.FBACCOUNT)
        lv_fbopt = self.ds_config.get('fbopt')
        lv_fbgroup = self.ds_config.get(const.CONFIG_FIELDS.FBCOLUMNGROUP)
        
        lv_fbads = facebookapi.FbGraph(lv_access_token, self.api_config)
        self.adsapi = lv_fbads.get_adsapi()
        # get the fields for selecteg group + type of object(campaign,Adset,Ad) + settings (default fields)
        lt_fields = self.get_selected_fields(const.CONFIG_FIELDS.FBFieldList)
        
        lt_insights = []
        lt_fout = []
        lt_params = {}
        lt_params[const.CONFIG_FIELDS.FBBREAKDOWN] = self.get_param(
            const.CONFIG_FIELDS.FBBREAKDOWN)
        lt_params[const.CONFIG_FIELDS.FBObjective] = self.get_param(
            const.CONFIG_FIELDS.FBObjective)
        lt_params[const.CONFIG_FIELDS.FBBuyingType] = self.get_param(
            const.CONFIG_FIELDS.FBBuyingType)
        lt_params['since'] = datetime.datetime.fromtimestamp(
            self.start_date[0]).date().strftime('%Y-%m-%d')
        lt_params['until'] = datetime.datetime.fromtimestamp(
            self.end_date).date().strftime('%Y-%m-%d')
        lv_adaccountid = self.ds_config.get(const.CONFIG_FIELDS.FBACCOUNT)
        print(
        'Until Date is --------------------------------------------------------',
        lt_params['until'])
        print('Since date is ---------------------------', lt_params['since'])
        lv_adaccount = facebookapi.FbAdaccount(self.adsapi, lv_adaccountid)
        print(lv_fbopt, '------------------------')
        if lv_fbopt == 'AdSet':
            lt_params[const.CONFIG_FIELDS.FBPageType] = self.ds_config.get(
                const.CONFIG_FIELDS.FBPageType)
            lt_adsetid = self.ds_config.get(const.CONFIG_FIELDS.FBAdset)
            # print("Adset ids are ------------------",lt_adsetid)
            lv_adaccount.get_adsets()
            for lw_adsetid in lt_adsetid:
                lv_adaccount.adsets.get
                lw_adset = lv_adaccount.adsets.get(lw_adsetid)
                lv_adset = facebookapi.FBAdset(lw_adsetid, self.adsapi,
                                               lw_adset)
                lv_adset.get_insights(i_fields=lt_fields, i_params=lt_params)
                '''
                lt_ins, lt_ftemp = lv_adset.get_insight_formatted()
                #collect insights in one final table 
                for lw_ins in lt_ins:
                    lt_insights.append(lw_ins)
                #field names should be collected for each call as the fields list might differ in insights fetched.
                for lw_ftemp in lt_ftemp:
                    if not(lw_ftemp in lt_fout):
                        lt_fout.append(lw_ftemp)'''
        if lv_fbopt == 'Campaign':
            lt_campaignid = self.ds_config.get('Campaigns')
            lv_adaccount.get_campaigns()
            
            print('Campaigns are ------------------------', lt_campaignid)
            for lw_campaignid in lt_campaignid:
                lw_campaign = lv_adaccount.campaigns.get(lw_campaignid)
                # get instance of the campaign
                lv_campaign = facebookapi.FbCampaign(lw_campaignid, self.adsapi,
                                                     lw_campaign)
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