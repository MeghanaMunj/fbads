
CONFIG_FILE = "fbads.json"


class IDENTITY_FIELDS:
    auth_code = ""
    NAME = ""
    
    pass


class CONFIG_FIELDS:
    FBACCOUNT = "fbaccount"
    FBOPT = 'fbopt'
    FBCAMPAIGN = 'Campaigns'
    FBCOLUMNGROUP = 'Columngroup'
    FBBREAKDOWN = 'Breakdown'
    FBDeliveryInfo = "DeliveryInfo"
    FBObjective = 'Objective'
    FBBuyingType = 'BuyingType'
    FBPageType = "PageType"
    FBFieldList = "FieldList"
    pass



gt_default = [ 'account_id', 'account_name', 'buying_type', 'campaign_id', 'campaign_name', 'date_start', 'date_stop', 'objective']
gt_infields = { "Performance": { "actions":['post_engagement'] ,
                                 "reach": [],
                                 'cost_per_action_type' : ['post_engagement'],
                                 'spend' : [],
                                 'total_unique_actions' : []
                                 },
                "Delivery" : { 
                    'reach' : [] ,                               
                    'frequency' : [] ,
                    'cpp' : [] ,
                    'impressions' : [] ,
                    'cpm' : [] 
                    },
                "PerformanceandClicks" : {
                    'actions' : ['like','link_click'] ,
                    'reach' : [] ,
                    'frequency' : [] ,
                    'cost_per_action_type' : ['like'] ,
                    'spend' : [] ,
                    'clicks' : [] ,
                    'ctr' : [] ,
                    'cpc' : [] ,
                    'impressions' : [] ,
                    'cpm' : [] ,
                    'cost_per_unique_click' : [] ,
                    'unique_ctr' : [] ,
                    'total_unique_actions' : []                                         
                    },
                "Engagement": {
                    'actions': ['post_reaction', 'comment','post','link_click','like'],
                    'total_unique_actions' : []
                    },
                "VideoEngagement" : {
                    'impressions' : [] ,
                    'reach' : [] ,
                    'actions' : ['video_view'] ,
                    'video_avg_percent_watched_actions' : ['video_view'] ,
                    'video_p100_watched_actions' : ['video_view'] ,
                    'video_p25_watched_actions' : ['video_view'] ,
                    'video_p50_watched_actions' : ['video_view'] ,
                    'video_p75_watched_actions' : ['video_view'] ,
                    'video_p95_watched_actions' : ['video_view'] ,
                    'video_10_sec_watched_actions' : ['video_view'] ,
                    'cost_per_action_type' : ['video_view'] ,
                    'cost_per_10_sec_video_view' : ['video_view'] ,
                    'spend' : []                     
                    },
                "MessengerEngagement": {
                    'impressions' : [] ,
                    'actions' : ['link_click','messenger.reply','onsite_conversion.messaging_block','cnsite_conversion.messaging_first_reply','onsite_conversion.purchase'] ,
                    'cost_per_action_type' : ['onsite_conversion.purchase'] ,
                    'spend' : [] 
                    },
                "AppEngagement": {
                    'actions' : ['app_custom_event','app_install','mobile_app_install','post','comment','post_reaction'],
                    'cost_per_action_type' : [ 'app_custom_event', 'app_engagement','app_install','mobile_app_install']
                    },
                "CarouselEngagement": {
                    'reach' : [] ,
                    'frequency' : [] ,
                    'impressions' : [] ,
                    'clicks' : [] ,
                    'cpc' : [] ,
                    'cpm' : [] ,
                    'cpp' : [] ,
                    'ctr' : [] ,
                    'spend' : [] ,
                    'total_actions' : [] ,
                    'total_unique_actions' : [] ,
                    'unique_clicks' : [] ,
                    'unique_ctr' : [] ,
                    'actions' : ['link_click'] ,
                    'website_ctr' : ['link_click'] ,
                    'cost_per_unique_click' : [] 
                    
                    },
                "CrossDevice": {
                    'actions': ['mobile_app_install']
                    }

                }

gt_fielddesc = {
    'total_unique_actions' :   'People Taking actions',
    'cpp' :   'Cost per 1,000 People Reached',
    'cpm' :   'CPM (Cost per 1,000 Impressions)',
    'actions:video_view' :   '3 second Video Views  ',
    'video_avg_percent_watched_actions:video_view' :   'Video Percentage Watched',
    'video_p100_watched_actions:video_view' :   'Video Watches at 100%',
    'video_p25_watched_actions:video_view' :   'Video Watches at 25%',
    'video_p50_watched_actions:video_view' :   'Video Watches at 50%',
    'video_p75_watched_actions:video_view' :   'Video Watches at 75%',
    'video_p95_watched_actions:video_view' :   'Video Watches at 95%',
    'video_10_sec_watched_actions:video_view' :   'Video 10 sec watched',
    'cost_per_action_type:video_view' :   'Cost per 3 sec Cideo',
    'cost_per_10_sec_video_view:video_view' :   'Cost per 10 sec Video',
    'actions:app_custom_event' :   'Mobile App Actions',
    'actions:app_install' :   'Desktop App Installs',
    'actions:mobile_app_install' :   'Mobile App Installs',
    'actions:post' :   'Post Shares',
    'actions:comment' :   'Post Comment',
    'cost_per_action_type:app_custom_event' :   'Cost per Mobile App Engagement',
    'cost_per_action_type:app_engagement' :   'Cost per Desktop App Engagement',
    'cost_per_action_type:app_install' :   'Cost per Desktop App Install',
    'cost_per_action_type:mobile_app_install' :   'Cost per Mobile App Install',
    'cpc' :   'CPC(All)',
    'cpm' :   'CPM(Cost per 1000 impresssions)',
    'cpp' :   'Cost per 1000 People Reached',
    'ctr' :   'CTR (All)',
    'total_actions' :   'Actions',
    'unique_clicks' :   'Unique Clicks(All)',
    'unique_ctr' :   'Unique CTR(All)',
    'website_ctr_link_click' :   'CTR (Link Click-Through Rate)',
    'actions:like' :   'Results',
    'reach' :   'Reach',
    'frequency' :   'Frequency',
    'cost_per_action_type:like' :   'Cost per result',
    'ctr' :   'CTR All',
    'cpc' :   'CPC All',
    'cpm' :   'CPM (Cost per 1,000 Impressions)',
    'cost_per_unique_click' :   'CPC (Cost per Link Click)',
    'unique_ctr' :   'CTR (Link Click-Through Rate)',
    'actions:mobile_app_install' :   'Mobile App Installs',
    'actions:messenger.reply' :   'Messaging Replies',
    'actions:onsite_conversion.messaging_block' :   'Blocked Messaging Conversations',
    'actions:cnsite_conversion.messaging_first_reply' :   'New Messaging Conversations',
    'actions:onsite_conversion.purchase' :   'On-Facebook Purchases',
    'cost_per_action_type:onsite_conversion.purchase' :   'Cost per On-Facebook Purchase',
    'spend' :   'On-Facebook Purchase Conversion Value',
    'actions:post_engagement' :   'Results',
    'cost_per_action_type:post_engagement' :   'Cost Per Result',
    'actions:comment' :   'Post Comment',
    'actions:post' :   'Post Shares',
    'actions:like' :   'Page Likes',
    'cost_per_unique_click' :   'Cost per Unique Click (All)'
                
                }
