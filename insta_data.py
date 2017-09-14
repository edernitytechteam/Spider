from datetime import datetime
from dateutil import parser
import json
import urllib.request

def main():
    BASE_URL = "https://graph.facebook.com/v2.10/"
    USER_ACCESS_TOKEN = "EAAZAeUFmgV58BAEkNZAsxKT6uPf5QFQW4ZBL0xPLxRAZAAb0oZAZBQW88ZBXac9bH55q7rFEWmAWtDqfPTZB0KqYHJdiortXGsbExAcZBAlS49ScVbAGHe8JGGYDDrqZB3jAs7RbGU0bJI6GZCbxcWUneEuSpfUhBfYjB5mugOeexs6FAL0mrRroqo875XBLsAj3W6guAFmpl3otAZDZD"
    MEDIA_ID = "17882286643077424"
    ADVERT_ID = ""

    i_data = get_insta_post_details(USER_ACCESS_TOKEN, MEDIA_ID, BASE_URL)
    m_type = i_data["media_type"]
    i_insights = get_insta_post_insights(USER_ACCESS_TOKEN, MEDIA_ID, BASE_URL, m_type)
    data = dict(i_data.items() | i_insights.items())
    data = json.loads(json.dumps(data))
    print(data)
    


def get_insta_post_details(token, m_id, base):
    m_uri = "?fields=caption,comments_count,like_count,media_type,permalink,timestamp&access_token="
    url = base + m_id + m_uri + token
    data = to_json(url)
    m_created_date = str(parser.parse(data["timestamp"]).date())
    m_created_time = str(parser.parse(data["timestamp"]).time())
    data = {'caption' : data["caption"], 'comments' : data["comments_count"], 'likes' : data["like_count"],
            'media_type' : data["media_type"], 'permalink' : data["permalink"], 'm_time' : m_created_time, "m_date" : m_created_date }
    return data

def get_insta_post_insights(token, m_id, base, m_type):
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
        return val
    else:
        url = base + m_id + m_vuri + token
        data = to_json(url)
        param = ["egagement", "impressions", "reach", "saved", "views"]
        val = {}
        counter = 0
        for e in param:
            val[e] = data["data"][counter]["values"][0]["value"]
            counter+=1
        return val

def get_insta_ad_data(token, m_id, base):
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