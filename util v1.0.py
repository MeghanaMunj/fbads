# encoding: utf-8
import logging
import const
import sdk.const as sdkconst
from threep.base import DataYielder
import facebookapi
log = logging
import csv

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
        print(self.ds_config)
        print(self.identity_config)
        print('Start date ---------',self.start_date)
        print('End date ---------', self.end_date)
        lv_access_token = self.identity_config.get('access_token')
        lv_fbaccount = self.ds_config.get('fbaccount')
        lv_fbopt = self.ds_config.get('fbopt')
        
        lv_apid = const.APP_DETAILS.apid
        lv_fbads = facebookapi.FbGraph(lv_access_token,lv_apid,const.APP_DETAILS.secret)
        self.adsapi = lv_fbads.get_adsapi()
        #get the selected fields 
        i = 1
        lv_flag = True
        lt_fields = []
        while lv_flag == True:
            lv_fieldname = 'selected_field' + str(i)
            if lv_fieldname in self.ds_config:
                lt_fields.append(self.ds_config.get(lv_fieldname))
                i = i + 1
            else:
                lv_flag = False
        lt_insights = []    
        lt_fout = []
        if lv_fbopt == 'Campaign':
            lt_campaignid = self.ds_config.get('Campaigns')  
            for lw_campaignid in lt_campaignid:                            
                lv_campaign = facebookapi.FbCampaign(lw_campaignid,self.adsapi)
                lt_ftemp = []
                lt_ins = []
                lt_ins,lt_ftemp = lv_campaign.get_insights(lt_fields,['gender','days_1'])
                for lw_ins in lt_ins:
                    lt_insights.append(lw_ins)
                for lw_ftemp in lt_ftemp:
                    if not(lw_ftemp in lt_fout):
                        lt_fout.append(lw_ftemp)
            
               
        #open response file for each survey 
        with open(file_path, 'w') as outfile:
            writer = csv.DictWriter(outfile,fieldnames=lt_fout)
            #add the header 
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
        self.identity_config = self.storage_handle.get(sdkconst.NAMESPACES.IDENTITIES,
                                                       identity_key)

        self.ds_config = self.storage_handle.get(identity_key, ds_config_key)

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