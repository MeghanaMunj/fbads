from __future__ import print_function

__author__ = ''

import os
import const
import json
import logging as log
import simplestorage.keystorage as simp
import sdk.const as sdkconst
from sdk.const import COMMON_CONFIG_FIELDS, \
    COMMON_IDENTITY_FIELDS, NAME, VALUE
from const import CONFIG_FIELDS, IDENTITY_FIELDS
from threep.base import ThreePBase
from sdk.utils import get_key_value_label, make_kv_list
# Insert your import statements here
from runtime_import.libs.fbads.util import fbadsDataYielder
import facebookads.api as fbapi
import urllib2
import urllib
import requests
from facebookads.adobjects.adaccount import AdAccount
from facebookads.adobjects.adsinsights import AdsInsights
from facebookads.adobjects import user
import facebookapi
import pydash


# End of import statements


class fbadsManager(ThreePBase):
    """
    This is main class using which Mammoth framework interacts with third party API
    plugin (referred as API hereinafter). Various responsibilities of this class
    is to manage/update identities, ds_configs and few more interfaces to handle API logic

    """

    def __init__(self, storage_handle, api_config):
        
        self.config_file = "/".join(
            [os.path.dirname(__file__), const.CONFIG_FILE])
        super(fbadsManager, self).__init__(storage_handle, api_config)

        self.adsapi = None

    def get_identity_spec(self, auth_spec):
        """
           This function is called to render the form on the authentication screen. It provides the render specification to
        the frontend.

        In the simplest case just return the provided auth_spec parameter.
        """
        
        """ Construct the oauth_dialog_url.
        """
        lv_redirect = 'https://redirect.mammoth.io/redirect/oauth2'
        # oauth_save_url = "http://localhost:6346/sandbox?integration_key=fbads"
        oauth_save_url = self.api_config.get("oauth_save_url")
        print("Oauth save url is --------", oauth_save_url)
        url_params = urllib.urlencode({
            'redirect_uri': lv_redirect,
            'client_id': self.api_config.get("client_id"),
            'cient_secret': self.api_config.get("client_secret"),
            'scope': 'ads_read',
            'response_type': 'code'})

        oauth_url = 'https://www.facebook.com/v2.10/dialog/oauth?' + "&state=" + urllib2.quote(
            oauth_save_url)
        
        oauth_url = oauth_url + "&" + url_params
        auth_spec["AUTH_URL"] = oauth_url
        print("\nThe auth dialog url was " + oauth_url + "\n")

        return auth_spec

    def get_identity_config_for_storage(self, params=None):
        """
        :param params: dict, required to generate identity_config dict object for storage
        :return: newly created identity_config. The value obtained in params is
        a dictionary that should contain following keys:
        
        """
        # create an identity dictionary and store this with the storage handle.
        config = {
            const.IDENTITY_FIELDS.NAME: params.get(const.IDENTITY_FIELDS.NAME),
            # sdkconst.COMMON_IDENTITY_FIELDS.NAME: params.get(const.IDENTITY_FIELDS.NAME, 'untitled'),
        }
        lv_redirect = "https://redirect.mammoth.io/redirect/oauth2"
        print ("Params are ---------------------", params)
        """ Construct the oauth_dialog_url.
            """
        lv_auth_code = params.get("code")
        print("Auth code --------------------", lv_auth_code)
        url_params = urllib.urlencode({
            'redirect_uri': lv_redirect,
            "code": lv_auth_code,
            'client_id': self.api_config.get("client_id"),
            'client_secret': self.api_config.get("client_secret")})

        oauth_url = 'https://graph.facebook.com/v2.10/oauth/access_token?' + url_params

        print("\nThe auth dialog url was " + oauth_url + "\n")
        
        access_token_response = requests.post(oauth_url)
        print(
        'Response **********************************', access_token_response)
        access_json = access_token_response.json()
        print('Json ************************************', access_json)
        lv_access_token = access_json.get('access_token')
        print("Access token is ---------------------", lv_access_token)
        # create an identity dictionary and store this with the storage handle.
        identity_config = {"auth_code": lv_auth_code,
                           "access_token": lv_access_token
                           }
        
        if params.get(COMMON_IDENTITY_FIELDS.NAME):
            identity_config[COMMON_IDENTITY_FIELDS.NAME] = params.get(
                COMMON_IDENTITY_FIELDS.NAME)
        else:
            lv_fbapi = facebookapi.FbGraph(lv_access_token, self.api_config)
            lt_result = lv_fbapi.get_user_name()
            if lt_result.get('status') != 1:
                identity_config[
                    sdkconst.COMMON_IDENTITY_FIELDS.NAME] = lt_result.get(
                    'user')
            else:
                identity_config[
                    sdkconst.COMMON_IDENTITY_FIELDS.NAME] = "unspecified_name"
        
        return identity_config

    def validate_identity_config(self, identity_config):
        """
            :param identity_config:
            :return: True/False: whether the given identity_config is valid or not
        """
        return True

    def format_identities_list(self, identity_list):
        """
        :param identity_list: all the existing identities, in the
        following format:
            {
                IDENTITY_KEY_1: identity_config_1,
                IDENTITY_KEY_2: identity_config_2,
                ...
            }
        :return:Returns extracted list of  all identities, in the following format:
          [
            {
                name: DISPLAY_NAME_FOR_IDENTITY_1
                value: IDENTITY_KEY_1
            },
            {
                name: DISPLAY_NAME_FOR_IDENTITY_2
                value: IDENTITY_KEY_2
            },
            ...

          ]
        """
        # using make_kv_list method here, You can use your own logic.

        formatted_list = make_kv_list(identity_list, sdkconst.FIELD_IDS.VALUE,
                                      sdkconst.FIELD_IDS.NAME)
        return formatted_list

    def delete_identity(self, identity_config):
        """
            put all the logic here you need before identity deletion and
            if identity can be deleted, return True else False
            returning true will delete the identity from the system.

            :param identity_config: identity
            :return:
        """
        return True

    def get_ds_config_spec(self, ds_config_spec,
                           identity_config, params=None):
        """
            :param ds_config_spec: ds_config_spec from json spec.
            :param identity_config: corresponding identity object for which
                ds_config_spec are being returned
            :param params: additional parameters if any
            :return:  ds_config_spec.
            Any dynamic changes to ds_config_spec, if required, should be made here.
        """
        print('DS Config specs ----------------------------')
        
        # print('nIdenfity config ----------------------------',identity_config)
        # print('Params ---------------------------------',params)
        
        items = []
        lv_adaccountid = params.get('profile')
        lv_adaccount = facebookapi.FbAdaccount(self.adsapi, lv_adaccountid)
        lv_adaccount.get_campaign_list()
        
        for lw_camp in lv_adaccount.camplist:
            items.append({"selectable": False,
                          'selected': True,
                          "name": lw_camp.get('name') + ' - ' + lw_camp.get(
                              'id'),
                          'value': lw_camp.get('id')
                          })
        ds_config_spec['ux']['attributes'][const.CONFIG_FIELDS.FBCAMPAIGN][
            'items'] = items
        
        # do get and check if its existing, if yes update
        # else create using store_json
        # self.storage_handle.store_json(lt_campaign,'FBCampaigns','FBCampaign' + lv_adaccountid)
        
        
        
        items = []
        lv_adaccount.get_adset_list()
        for lw_adset in lv_adaccount.adsetlist:
            items.append({"selectable": False,
                          'selected': True,
                          "name": lw_adset.get('name') + ' - ' + lw_adset.get(
                              'id'),
                          'value': lw_adset.get('id')
                          })
        ds_config_spec['ux']['attributes'][const.CONFIG_FIELDS.FBAdset][
            'items'] = items

        # get the column group to be displayed
        # lv_columngroup = params.get(const.CONFIG_FIELDS.FBCOLUMNGROUP)
        lv_columgroup = ds_config_spec.get('fields').get(
            const.CONFIG_FIELDS.FBCOLUMNGROUP).get('default_value')
        # get the fields list attached to it.
        lt_groupfields = facebookapi.get_fields(lv_columgroup)
        items = []
        for lv_key, lw_field in const.gt_fielddesc.iteritems():
            lv_selected = False
            if lv_key in lt_groupfields:
                lv_selected = True
            items.append({"selectable": False,
                          'selected': lv_selected,
                          "name": lw_field,
                          'value': lv_key
                          })

        ds_config_spec['ux']['attributes'][const.CONFIG_FIELDS.FBFieldList][
            'items'] = items
        return ds_config_spec

    def get_ds_config_for_storage(self, params=None):
        """
        :param params: dict, required to generate ds_config dict object for storage
        :return: newly created ds_config. The value obtained in params is
        a dictionary that should contain following keys:
             fbaccount,
        
        """
        # print('Params are ***********************************************************',params)
        # print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        lv_fbopt = params.get('fbopt')
        ds_config = {CONFIG_FIELDS.FBOPT: lv_fbopt,
                     CONFIG_FIELDS.FBACCOUNT: params.get('profile'),
                     CONFIG_FIELDS.FBCOLUMNGROUP: params.get('Columngroup'),
                     CONFIG_FIELDS.FBCAMPAIGN: params.get('Campaigns'),
                     CONFIG_FIELDS.FBBREAKDOWN: params.get('Breakdown'),
                     CONFIG_FIELDS.FBDeliveryInfo: params.get(
                         CONFIG_FIELDS.FBDeliveryInfo),
                     CONFIG_FIELDS.FBObjective: params.get(
                         CONFIG_FIELDS.FBObjective),
                     CONFIG_FIELDS.FBBuyingType: params.get(
                         CONFIG_FIELDS.FBBuyingType),
                     CONFIG_FIELDS.FBPageType: params.get(
                         CONFIG_FIELDS.FBPageType),
                     CONFIG_FIELDS.FBFieldList: params.get(
                         CONFIG_FIELDS.FBFieldList),
                     CONFIG_FIELDS.FBAdset: params.get(CONFIG_FIELDS.FBAdset)}

        # print('DS Config values is ---------------', ds_config)
        return ds_config

    def format_ds_configs_list(self, ds_config_list, params=None):
        """
            :param ds_config_list: all the existing ds_configs, in the
            following format:
                {
                    CONFIG_KEY_1: ds_config_1,
                    CONFIG_KEY_2: ds_config_2,
                    ...
                }
            :param params: Additional parameters, if any.
            :return:Returns extracted list of  all ds_configs, in the following format:
              [
                {
                    name: DISPLAY_NAME_FOR_CONFIG_1
                    value: CONFIG_KEY_1
                },
                {
                    name: DISPLAY_NAME_FOR_CONFIG_2
                    value: CONFIG_KEY_2
                },
                ...
        """

        formatted_list = make_kv_list(ds_config_list, sdkconst.VALUE,
                                      sdkconst.NAME)
        return formatted_list

    def is_connection_valid(self, identity_config, ds_config=None):
        """
            :param identity_key:
            :param ds_config_key:
            :return: Checks weather the connection specified by provided identity_key and ds_config_key is valid or not. Returns True if valid,
                     False if invalid
        """
        return True

    def sanitize_identity(self, identity):
        """
            update identity object with some dynamic information you need to fetch
            everytime from server. for e.g. access_token in case of OAUTH
            :param identity:
            :return:
        """
        return identity

    def validate_ds_config(self, identity_config, ds_config):
        """
            :param identity_config: identity object
            :param ds_config: ds_config object
            :return: dict object with a mandatory key "is_valid",
            whether the given ds_config is valid or not
        """
        return {'is_valid': True}

    def get_data(self, identity_key, config_key, start_date=None,
                 end_date=None,
                 batch_id=None, storage_handle=None, api_config=None):
        """

        :param self:
        :param identity_key:
        :param config_key:
        :param start_date:
        :param end_date:
        :param batch_id: TODO - replace it with a dict
        :param storage_handle:
        :param api_config:
        :return: instance of DataYielder class defined in util.py
        """
        return fbadsDataYielder(storage_handle,
                                api_config,
                                identity_key,
                                config_key,
                                start_date, end_date, batch_id=batch_id)

    def get_display_info(self, identity_config, ds_config):
        """
            :param self:
            :param identity_config:
            :param ds_config:
            :return: dict object containing user facing information extracted from
             the given identity_config and ds_config.
        """
        pass

    def sanitize_ds_config(self, ds_config):
        """
            :param ds_config:
            :return:

            update ds_config object with some dynamic information you need to update
            every time from server.
        """
        return ds_config

    def augment_ds_config_spec(self, identity_config, params):
        """
            :param params: dict object containing subset ds_config parameters
            :param identity_config:
            :return: dict in the form : {field_key:{property_key:property_value}}
            this method is used to update/augment ds_config_spec with some dynamic
            information based on inputs received
        """
        '''
        augmented_params = {}        
        if "tables" in params.keys():            
            params[const.CONFIG_FIELDS.QUERY_STRING] = QUERY_STATEMENTS.DESCRIBE_TABLE.format(params.get("tables"))
            description = self.get_data_sample(identity_config, params)            
            params[const.CONFIG_FIELDS.QUERY_STRING] = QUERY_STATEMENTS.TABLE_PREVIEW.format(params.get("tables"))
            table_preview = self.get_data_sample(identity_config, params)            
            col_name_type_map = {}            
            for row in description['rows']:                
                col_name_type_map[row[0]] = row[1]            
                if table_preview and 'metadata' in table_preview:                
                    for col in table_preview['metadata']:                    
                        col['display_name'] += " (" + col_name_type_map[col['display_name']] + ")"            
                        augmented_params["ux"] = {"attributes": {"table_preview": table_preview}}            
                        augmented_params["fields"] = {"table_description": {"label": "Table description ({0}):".format(params.get("tables"))}
                                                      }
        '''
        # ds_config_spec['ux']['attributes']['Campaignfields']['items'] = items
        print(
        '\n\n\n\n\nAugmented parameters ---------------------------------',
        params)
        print('Identity config ------------------------------', identity_config)
        lv_fbopt = params.get('fbopt')
        # if lv_fbopt == 'Campaign':

        
        return {}

    def update_ds_config(self, ds_config, params):
        """
            :param ds_config:
            :param params: dict object containing information required to update ds_config object
            :return: updated ds_config dict
        """
        return ds_config

    def if_identity_exists(self, existing_identities, new_identity):
        """
            :param existing_identities: dict of existing identities
            :param new_identity: new identity dict
            :return: True/False if the new_identity exists already
            in  existing_identities

        """
        return False

    def get_data_sample(self, identity_config, ds_config):
        """
            :param identity_config:
            :param ds_config:
            :return: data sample in the following format:
            {
                "metadata": [],
                "rows": []
            }

            metadata : metadata as a list of dictionaries in the following format
                {
                    'internal_name': UNIQUE COLUMN IDENTIFIER,
                    'display_name': COLUMN HEADER,
                    'type': COLUMN DATATYPE -  TEXT/DATE/NUMERIC
               }

        """
        return {}

    def list_profiles(self, identity_config):
        """
            :param identity_config: for which profiles have to be returned

            :return:Returns list of  all profiles for a given identity_config,
            in the following format:"""
        items = []
        lv_access_token = identity_config.get("access_token")
        lv_fbads = facebookapi.FbGraph(lv_access_token, self.api_config)
        self.adsapi = lv_fbads.get_adsapi()
        lt_adaccount = lv_fbads.get_adaccount()
        
        for lw_adaccount in lt_adaccount:
            items.append({"selectable": False,
                          'selected': True,
                          "name": lw_adaccount.get(
                              'name') + ' - ' + lw_adaccount.get('account_id'),
                          'value': lw_adaccount.get('id')
                          })
        
        return items

    def delete_ds_config(self, identity_config, ds_config):
        """
            :param identity_config:
            :param ds_config:
            :return: delete status

            put all the pre deletion logic here for ds_config and
            if ds_config can be deleted, return True else False
            returning true will delete the ds_config from the system
        """
        return True