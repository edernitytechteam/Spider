from datetime import datetime
from dateutil import parser
import json
import urllib.request

def main():
    BASE_URL="https://graph.facebook.com/v2.10/"
    USER_ACCESS_TOKEN=""
    APP_ACCESS_TOKEN=""
    ADVERT_ID=""
    POST_ID="" 
    #In the above block initialize the access key and Advert id for which the data to be extracted  

    if POST_ID == "" and ADVERT_ID!="":
        POST_ID = get_post_id(USER_ACCESS_TOKEN, ADVERT_ID, BASE_URL)
    

    if ADVERT_ID!="":
        ad_data = get_post_ad_data(USER_ACCESS_TOKEN, ADVERT_ID, BASE_URL)


    p_type = get_post_type(USER_ACCESS_TOKEN, POST_ID, BASE_URL)
    p_data = get_post_data(USER_ACCESS_TOKEN, POST_ID, BASE_URL)
    p_data['type'] = p_type
    p_insights = get_post_insights(USER_ACCESS_TOKEN, POST_ID, BASE_URL, p_type)
    f_data = dict(p_data.items() | p_insights.items() | ad_data.items())
    f_data = json.loads(json.dumps(f_data))
    print(f_data)
    


    
    

def get_post_id(token, ad_id, base):
    """Function get_post_id() return Post ID, you need to pass User Access Token, Advert ID
     and Graph Api base URL with requied API version"""
    id_uri = "?fields=creative{effective_object_story_id}&access_token="
    url = base + ad_id + id_uri + token
    data = to_json(url)
    p_id = data["creative"]["effective_object_story_id"]
    return p_id


def get_post_type(token, post_id, base):
    """Function get_post_type() return Post Type(it can be Status, Photos, Videos),you need
     to pass User Access Token, Post ID and Graph Api base URL with requied API version"""
    id_uri = "?fields=type&access_token="
    url = base + post_id + id_uri + token
    data = to_json(url)
    p_type = data["type"]
    return p_type

def get_post_data(token, post_id, base):
    id_uri = "?fields=shares,likes.limit(0).summary(true),comments.limit(0).summary(true),"\
            "permalink_url,from,is_instagram_eligible,created_time&access_token="
    url = base + post_id + id_uri + token
    data = to_json(url)
    likes = data["likes"]["summary"]["total_count"]
    comments = data["comments"]["summary"]["total_count"]
    if data["shares"]["count"]:
        shares = data["shares"]["count"]
    else:
        shares = 0
    link = data["permalink_url"]
    p_from = data["from"]["name"]
    is_insta = data["is_instagram_eligible"]
    p_create_time = str(parser.parse(data["created_time"]).time())
    p_create_date = str(parser.parse(data["created_time"]).date())
    p_id = data["id"]
    data = {'likes' : likes, 'comments' : comments, 'shares' : shares, 'link' : link, 
            'post_from' : p_from, 'post_created_time' : p_create_time,'post_created_date' : p_create_date, 'post_id' : p_id,
            'is_insta' : is_insta}
    return data
def get_post_insights(token, post_id, base, p_type):
    if p_type=="video":
        id_uri = "/insights?metric=post_video_avg_time_watched,post_video_views,post_impressions,post_impressions_unique,"\
        "post_impressions_organic_unique,post_impressions_paid_unique,"\
        "post_engaged_users,post_negative_feedback&access_token="
        url = base + post_id + id_uri + token
        data = to_json(url)
        param = ["average_watch_time","total_video_views","impressions", "reach", "organic_reach", "paid_reach", "engagement", "negative_feedback"]
        val = {}
        counter = 0
        for e in param:
            val[e] = data["data"][counter]["values"][0]["value"]
            counter+=1
        return val
    else:
        id_uri = "/insights?metric=post_impressions,post_impressions_unique,"\
        "post_impressions_organic_unique,post_impressions_paid_unique,"\
        "post_engaged_users,post_negative_feedback&access_token="
        url = base + post_id + id_uri + token
        data = to_json(url)
        param = ["impressions", "reach", "organic_reach", "paid_reach", "engagement", "negative_feedback"]
        val = {}
        counter = 0
        for e in param:
            val[e] = data["data"][counter]["values"][0]["value"]
            counter+=1
        return val

def get_post_ad_data(token, ad_id, base):
    id_uri = "/insights?metric=impressions,spend,start_time,stop_time&breakdowns=gender&access_token="
    loc_uri = "/insights?metric=impressions,spend&breakdowns=region&access_token="
    target_uri = "?fields=targetingsentencelines&access_token="
    url = base + ad_id + id_uri + token
    tar_url = base + ad_id + target_uri + token
    loc_url = base + ad_id + loc_uri + token
    tar_data = to_json(tar_url)
    loc_data = to_json(loc_url)
    data = to_json(url)
    ad_impression = 0
    for a in range(3):
        if (ad_impression <= int(data["data"][a]["impressions"])):
            ad_impression = int(data["data"][0]["impressions"])
            top_audience = data["data"][a]["gender"]
    adset_id = data["data"][0]["adset_id"]
    ad_impression = 0
    spend = 0
    for a in range(3):
        ad_impression = ad_impression + int(data["data"][a]["impressions"])
        spend = spend + float(data["data"][a]["spend"])
    impre = 0
    for a in loc_data["data"]:
        if (impre <= int(a["impressions"])):
            impre = int(a["impressions"])
            top_loaction = a["region"]
    time_uri = "?fields=start_time,end_time&access_token="
    time_url = base + adset_id + time_uri + token
    time_data = to_json(time_url)
    ad_start = parser.parse(time_data["start_time"])
    ad_end = parser.parse(time_data["end_time"])
    ad_start_date = str(ad_start.date())
    ad_start_time = str(ad_start.time())
    ad_end_date = str(ad_end.date())
    ad_end_time = str(ad_end.time())
    ad_run_time = str(ad_end - ad_start)
    ad_target_location = tar_data["targetingsentencelines"]["targetingsentencelines"][0]["children"][0]
    ad_target_age = tar_data["targetingsentencelines"]["targetingsentencelines"][1]["children"][0]
    data = {'top_location' : top_loaction,'top_audience' : top_audience, 'ad_impressions' : ad_impression, 'spend' : spend,
             'ad_target_location' : ad_target_location, 'ad_target_age' : ad_target_age, 'ad_start_date' : ad_start_date,
             'ad_start_time' : ad_start_time, 'ad_end_date' : ad_end_date, 'ad_end_time' : ad_end_time, 'ad_run_time' : ad_run_time}
    return data


def to_json(url):
    try:
        respose = urllib.request.urlopen(url)
        data = respose.read()
        data = json.loads(data)
        return data
    except:
        print("Error getting object with URL : ",  url)

main()