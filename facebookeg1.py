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
from facebookads.adobjects import user

import urlparse
import facebookapiv1 as facebookapi




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

lv_apid = '1843616625966235'
lv_secret = '91966604942d8a082dc23e2b82d310c6'
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
    lw_pass.send_keys('meghanam104')
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
    #lt_insights = lv_adacc.get_insights()
    #print('Insights are -------------------',lt_insights)
    lt_campaigns = lv_adacc.get_campaigns(fields=['id','name','objective','buying_type'])
    lt_emptylist = []
    print('Campaign ----', lt_campaigns)
    '''
    for lw_campaign in lt_campaigns:
        lv_campid = lw_campaign.get('id')
        lv_camp = facebookapi.FbCampaign(adcampaign_id=lv_campid,adsapi=lv_adsapi)
        #lv_camp = facebookads.adobjects.campaign.Campaign(fbid = lv_campid,api=lv_adsapi)
        lt_fields = facebookapi.get_fields('campaignfields.txt')
        lt_output, lt_header = lv_camp.get_insights(i_fields=lt_fields,i_breakdown=['gender'])
        print('Output ---------')
        for lw_output in lt_output:
            print('Line of Output ------',lw_output)
        for lw_header in lt_header:
            print('Line in header ------',lw_header)
        print('Fields --------',lt_header)
        '''
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
        
