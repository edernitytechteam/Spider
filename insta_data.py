from datetime import datetime
from dateutil import parser
import json
import multiprocessing
import urllib.request
import time
start_time = time.time()

def main():
    BASE_URL = "https://graph.facebook.com/v2.10/"
    USER_ACCESS_TOKEN = "EAAZAeUFmgV58BAJLrlCiOZANqqCB5bppK4N82QDIZClxhBAnqGtCOvCkBX8X3g30WGRvZC4PNAECL1k443gnoFeTqF4cQyj0eMZBORjmSzEb5fyE5c2TJlrjGuQ4sCVc6TjZCPOaYMDKwoHU5nF8aVHsUBHztVxb69s2N4JNSZA3timUUKGE8MLvh01m8HFHRHgL0KUKbDJmAZDZD"
    MEDIA_ID = "17882286643077424"
    ADVERT_ID = "23842634590670312"

    i_data = get_insta_post_details(USER_ACCESS_TOKEN, MEDIA_ID, BASE_URL)
    m_type = i_data["media_type"]
    q = multiprocessing.Queue()
    i_insights = multiprocessing.Process(target=get_insta_post_insights, args=(USER_ACCESS_TOKEN, MEDIA_ID, BASE_URL, m_type,q,))
    i_ads_data = multiprocessing.Process(target=get_insta_ad_data, args=(USER_ACCESS_TOKEN, ADVERT_ID, BASE_URL,q,))
    i_insights.start()
    i_ads_data.start()
    i_insights.join()
    i_ads_data.join()
    data = i_data
    while q.empty() is False:
        data = dict(data.items() | q.get().items())
    
    
    print(data)
    print("--- %s seconds -----" %(time.time()-start_time))
    

def get_insta_post_details(token, m_id, base):
    m_uri = "?fields=caption,comments_count,like_count,media_type,permalink,timestamp&access_token="
    url = base + m_id + m_uri + token
    data = to_json(url)
    m_created_date = str(parser.parse(data["timestamp"]).date())
    m_created_time = str(parser.parse(data["timestamp"]).time())
    data = {'caption' : data["caption"], 'comments' : data["comments_count"], 'likes' : data["like_count"],
            'media_type' : data["media_type"], 'permalink' : data["permalink"], 'm_time' : m_created_time, "m_date" : m_created_date }
    print("--- %s seconds to get_insta_post_details -----" %(time.time()-start_time))
    return data

def get_insta_post_insights(token, m_id, base, m_type, q):
    m_uri = "/insights?metric=engagement,impressions,reach,saved&access_token="
    m_vuri = "/insights?metric=engagement,impressions,reach,saved,video_views&access_token="
    if m_type == "IMAGE":
        url = base + m_id + m_uri + token
        data = to_json(url)
        param = ["egagement", "impressions", "reach","saved"]
        val = {}
        counter = 0
        for e in param:
            val[e] = data["data"][counter]["values"][0]["value"]
            counter+=1
        print("--- %s seconds insights_post-----" %(time.time()-start_time))
        q.put(val)
    else:
        url = base + m_id + m_vuri + token
        data = to_json(url)
        param = ["egagement", "impressions", "reach", "saved", "views"]
        val = {}
        counter = 0
        for e in param:
            val[e] = data["data"][counter]["values"][0]["value"]
            counter+=1
        print("--- %s seconds insights_post-----" %(time.time()-start_time))
        q.put(val)

def get_insta_ad_data(token, ad_id, base,q):
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
    for a in data["data"]:
        if (ad_impression <= int(a["impressions"])):
            ad_impression = int(a["impressions"])
            top_audience = a["gender"]
    adset_id = data["data"][0]["adset_id"]
    ad_impression = 0
    spend = 0
    for a in data["data"]:
        ad_impression = ad_impression + int(a["impressions"])
        spend = spend + float(a["spend"])
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
    tar = {}
    for a in tar_data["targetingsentencelines"]["targetingsentencelines"]:
        if (a["content"] == "Location - Living In:"):
            tar["ad_tar_location"] = a["children"][0]
        if (a["content"] == "Age:"):
            tar["ad_tar_age"] = a["children"][0]
    data = {'top_location' : top_loaction,'top_audience' : top_audience, 'ad_impressions' : ad_impression, 'spend' : spend,
              'ad_start_date' : ad_start_date,
             'ad_start_time' : ad_start_time, 'ad_end_date' : ad_end_date, 'ad_end_time' : ad_end_time, 'ad_run_time' : ad_run_time}
    val = dict(data.items()| tar.items())
    q.put(val)
    print("--- %s seconds ads insights_post-----" %(time.time()-start_time))

def to_json(url):
    try:
        respose = urllib.request.urlopen(url)
        data = respose.read()
        data = json.loads(data)
        return data
    except:
        print("Error getting object with URL : ",  url)


main()