import facebookads.api as fbapi
from furl import furl
import furl
import facebookads
import requests
import urllib
import os
import webbrowser
from selenium import webdriver
import time
from facebookads.adobjects.adaccount import AdAccount
from facebookads.adobjects.adsinsights import AdsInsights
from facebookads.adobjects.adset import AdSet
from facebookads.adobjects import user
import pydash
import urlparse
import facebookapiv1 as facebookapi
def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + ':')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + ':')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def get_value(i_fname,i_input):
    print('Input is --------------------------',i_input)
    for lw_fname in i_input:
        print('Field name is -------',lw_fname)
        lv_fvalue = i_input.get(lw_fname)
        if type(lv_fvalue) is dict:
            print('This field -----',lw_fname,'-----is the dictionary-----',lv_fvalue)
            lw_fname = i_fname + ":" + lw_fname + ":"
            lt_output.update(get_value(lw_fname,lv_fvalue))
        elif type(lv_fvalue) is list:
            print('This field -----',lw_fname,'----is a list ------',lv_fvalue)
            for lw_list in lv_fvalue:
                if not (type(lw_list) is dir or type(lw_list) is list):
                    lt_output[lw_fname] = lw_list 
                else:
                    lw_fname = i_fname + ":" + lw_fname
                    lt_output.update(get_value(lw_fname,lw_list))
        else:
            lw_fname = i_fname  + lw_fname
            print('Concatenate field --------------', lw_fname)
            lt_output[lw_fname] = lv_fvalue
            print('Updated output is --------------',lt_output)
    return lt_output        


def oauth_dialog(client_id, redirect_uri,client_secret):
    """ Construct the oauth_dialog_url.
    """
    url_params = urllib.urlencode({
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        #'client_secret':client_secret,
        'scope': 'ads_read',
        'response_type' : 'code token'})

    auth_dialog_url = 'https://www.facebook.com/v2.10/dialog/oauth?' + url_params
    print "\nThe auth dialog url was " + auth_dialog_url + "\n"
    return auth_dialog_url

lv_file = open("c:\\output\\fbads.txt",'r')
lv_pwd = lv_file.read()

lv_apid = '126100771370994'
lv_secret = 'dd64127d716d805ca3d203b99ec4762c'
#lv_redirect = "http://127.0.0.1"
lv_redirect =  'https://www.facebook.com/connect/login_success.html'
lv_path = "C:\\output\\chromedriver.exe"
os.environ["webdriver.chrome.driver"] = lv_path

lv_redirecturl = oauth_dialog(lv_apid,lv_redirect,lv_secret)
                     
time.sleep(1)
browser = webdriver.Chrome(lv_path)
browser.get(lv_redirecturl)
browser.implicitly_wait(30000000)
browser.maximize_window()

browser.implicitly_wait(30000000)
browser.maximize_window()
for lw_username in browser.find_elements_by_id('email'):
    lw_username.send_keys('megmunj@rediffmail.com')
for lw_pass in browser.find_elements_by_id('pass'):
    lw_pass.send_keys(lv_pwd)
for lw_button in browser.find_elements_by_id('loginbutton'):
    lw_button.click()     

browser.implicitly_wait(300000000)

browser.implicitly_wait(30000000)
print('Current URL ---------', browser.current_url)
browser.implicitly_wait(300000000)

lv_url = browser.current_url
browser.implicitly_wait(300000000)
browser.implicitly_wait(300000000)
browser.implicitly_wait(300000000)
browser.implicitly_wait(300000000)
browser.implicitly_wait(300000000)

lv_url,lv_defrag = urlparse.urldefrag(lv_url)
lt_split = lv_defrag.split('=')
lv_token = lt_split[1]
lt_split = lv_token.split('&')
lv_token = lt_split[0]
#print('Access Token -----', lv_token)
lv_adsapi = fbapi.FacebookAdsApi.init(app_id= lv_apid, app_secret = lv_secret, api_version='v2.10', access_token= lv_token)



lt_fields = [
    'name',
    
    'id',
    'email'
]

lt_params = {
    'time_range': {'since':'2017-06-28','until':'2017-07-28'},
    'filtering': [],
    'level': 'account',
    'breakdowns': ['age','gender'],
}

lv_user = user.User('me',lv_adsapi)



lt_accounts = lv_user.get_ad_accounts(fields=lt_fields)

i = 1
for lw_account in lt_accounts:
    print('LW_ACCOUNT = ', lw_account)
    lv_accountid = lw_account.get('id')
    i = i + 1
    lv_adacc = AdAccount(fbid=lv_accountid,api=lv_adsapi)
    if lv_accountid == 'act_102055410480984':
        #lt_ads = lv_adacc.get_ads(fields=['id','name'])
        #print('Ads by labels -------',lt_ads,'End of ads ------------------')
    #lt_insights = lv_adacc.get_insights()
    #print('Insights are -------------------',lt_insights)
        lt_campaigns = lv_adacc.get_campaigns(fields=['id','name','objective','buying_type'])
        #lt_emptylist = []
        #print('Campaign ----', lt_campaigns)
        
        lt_fields = facebookapi.get_attribtues_in_class(AdSet.Field)
        lt_adsets = lv_adacc.get_ad_sets(fields=lt_fields)
        for lw_adsets in lt_adsets:
            lt_adout = lw_adsets.export_all_data()
            print('Adset out put -----------------',lt_adout)
            
            lt_output = flatten_json(lt_adout)
            print('output is ----------------', lt_output)
        '''
        for lw_adsets in lt_adsets:
            lv_adset = AdSet(fbid=lw_adsets.get('id'), api=lv_adsapi)
            lt_fields = facebookapi.get_fields('campaignfields.txt')
            lt_insights = lv_adset.get_insights(fields=lt_fields)
            print('Insights for Adset ---',lw_adsets.get('id'),'are -------')
            print(lt_insights)
            for lw_insights in lt_insights:
                lt_actions = lw_insights.get("actions")
                print("actions are -----------------------", lt_actions)
                lv_index = pydash.find_index(lt_actions,['action_type','like'])
                print('Index for like is ------', lv_index)
                if lv_index >= 0:
                    print('Field value for action:like' , lt_actions[lv_index].get("value"))
        '''
        '''
        for lw_campaign in lt_campaigns:
            lv_campid = lw_campaign.get('id')
            lv_camp = facebookapi.FbCampaign(adcampaign_id=lv_campid,adsapi=lv_adsapi)
            #lv_camp = facebookads.adobjects.campaign.Campaign(fbid = lv_campid,api=lv_adsapi)
            lt_fields = facebookapi.get_fields('campaignfields.txt')
            lt_output, lt_header = lv_camp.get_insights(i_fields=lt_fields,i_breakdown=['gender'])
            #print('Insights for campaign are -------------', lv_camp.insights)
            for lw_insights in lv_camp.insights:
                lt_actions = lw_insights.get("actions")
                print("actions are -----------------------", lt_actions)
                lv_index = pydash.find_index(lt_actions,['action_type','like'])
                print('Index for like is ------', lv_index)
        
            
            print('Output ---------')
            for lw_output in lt_output:
                print('Line of Output ------',lw_output)
            for lw_header in lt_header:
                print('Line in header ------',lw_header)
            print('Fields --------',lt_header)'''
        
        '''
        lt_campinsights = lv_camp.get_insights(lt_fields)
        for lw_campinsight in lt_campinsights:
            print('Insight -------',lw_campinsight)
            for lw_fields in lt_fields:
                if type(lw_campinsight.get(lw_fields)) == type(lt_emptylist):
                   print('field -----',lw_fields,' ------------------',lw_campinsight.get(lw_fields))
                   #print('Find -----',type(lw_campinsight.get(lw_fields)).find('list'))
                   print('Type ----', type(lw_campinsight.get(lw_fields)))
        
        
        '''
