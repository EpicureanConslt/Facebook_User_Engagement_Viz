import httplib2
import simplejson as json
import os
import sys
import requests
from datetime import date, timedelta, datetime
from requests_oauthlib import OAuth2

def reaction_counter(parsed_json,like_count,love_count,wow_count,haha_count,sad_count,thankful_count,angry_count,none_count):
    reactions = parsed_json['data']
    for k in range(0,len(reactions)):
        if(reactions[k]['type'] == 'LIKE'):
            like_count = like_count+1
        elif(reactions[k]['type'] == 'LOVE'):
            love_count = love_count+1
        elif(reactions[k]['type'] == 'WOW'):
            wow_count = wow_count+1
        elif(reactions[k]['type'] == 'HAHA'):
            haha_count = haha_count+1
        elif(reactions[k]['type'] == 'SAD'):
            sad_count = sad_count+1
        elif(reactions[k]['type'] == 'THANKFUL'):
            thankful_count = thankful_count+1
        elif(reactions[k]['type'] == 'ANGRY'):
            angry_count = angry_count+1
        else:
            none_count = none_count+1
    if 'next' in parsed_json['paging']:
        next_url = parsed_json['paging']['next']
        next_parsed_json=requests.get(next_url).json()
        return reaction_counter(next_parsed_json,like_count,love_count,wow_count,haha_count,sad_count,thankful_count,angry_count,none_count)
    else:
        return(str(like_count) + "," + str(love_count) + "," + str(wow_count) + "," + str(haha_count) + "," + \
                         str(sad_count) + "," + str(thankful_count) + "," + str(angry_count))

if __name__ == "__main__":
    
    app_secret = ""
    app_id = ""
    auth_url = "https://graph.facebook.com/v2.7/oauth/access_token?client_id=" + app_id + "&client_secret=" + app_secret + "&grant_type=client_credentials"
    
    token=requests.get(auth_url).json()
    token=token['access_token']

    page_name = "https://www.facebook.com/kuowpublicradio/"

    page_url = "https://graph.facebook.com/v2.7/" + page_name + "?fields=fan_count,were_here_count,talking_about_count,name&access_token=" + token
    page_details=requests.get(page_url).json()
    page_likes = page_details['fan_count']
    page_id = page_details['id']
    page_name = page_details['name'].encode('utf-8')
    were_here = page_details['were_here_count']
    talking_about = page_details['talking_about_count']
            
    post_url = "https://graph.facebook.com/v2.7/" + page_id + "/posts?access_token=" + token
    post_details=requests.get(post_url).json()
    post_date = date.today()
    post_counter = 0
    
    while(post_counter < 100):
        for i in range(0, len(post_details['data'])):
            post_id = post_details['data'][i]['id']
            post_date = datetime.strptime(str(post_details['data'][i]['created_time'])[0:10], '%Y-%m-%d').date()
            reaction_url = "https://graph.facebook.com/v2.7/" + post_id + "/?fields=reactions,shares&access_token=" + token
            reaction_details=requests.get(reaction_url).json()
            if 'shares' in reaction_details:
                share_count=reaction_details['shares']['count']
            if 'reactions' in reaction_details:
                county = reaction_counter(reaction_details['reactions'],0,0,0,0,0,0,0,0)
            k = open("OutputLog.txt", "r+")
            k.seek(1,2)
            fb_log = "\n" + page_name + "," + str(post_details['data'][i]['created_time'])[0:10] + "," + str(page_likes) + "," + \
                         str(were_here) + "," + str(talking_about) + "," + str(share_count) + "," + county
            k.write(fb_log)
            k.close()
            if(post_counter < 100):
                post_counter = post_counter + 1
            else:
                break
            print("Processing Post #: " + str(post_counter))
        next_url = post_details['paging']['next']
        post_details=requests.get(next_url).json()
    print("Done!")
