import json, requests
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("CLIENT_ID")
redirect_url = os.getenv("R_URL")
client_secret = os.getenv("C_S")
graph_api_url = "https://graph.microsoft.com/v1.0/"


# To generate access token from refresh token and save the new refresh token


acc_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

ref_token_js = json.load(open("teams_ref.json"))['ref_token']

val = {"grant_type":"refresh_token","client_id":client_id,"redirect_uri":redirect_url,"client_secret": client_secret,"refresh_token": ref_token_js }

header ={"Content-Type": "application/x-www-form-urlencoded"}

res = requests.post(url=acc_url,data = val,headers = header)

token_get=json.loads(res.text)

teams_ref = {"ref_token":token_get['refresh_token']}

# to save the refresh token
json_object = json.dumps(teams_ref, indent=4)
with open("teams_ref.json", "w") as outfile:
    outfile.write(json_object)





# Iterates through the samplelist and create chat_id   
def create_chatid(email):
    chat_url = f"{graph_api_url}chats"
    headers = {
        "Authorization": f"Bearer {token_get['access_token']}",
        "Content-Type": "application/json",
    }
    
    payload= {
      "chatType": "oneOnOne",
      "members": [
        {
          "@odata.type": "#microsoft.graph.aadUserConversationMember",
          "roles": ["owner"],
          "user@odata.bind": "https://graph.microsoft.com/v1.0/users('platforms.hq@optisolbusiness.com')"
        },
        {
          "@odata.type": "#microsoft.graph.aadUserConversationMember",
          "roles": ["owner"],
          "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{email}')"
        }
    
      ]
    }
    response = requests.post(chat_url, headers=headers, json=payload).text
    return json.loads(response)['id'] #Return the chat_id alone from the output






#Send messages to each chat_id 
def send_anouncement(chatid):
    message_url = f"https://graph.microsoft.com/v1.0/chats/{chatid}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    message_body = {
        "body": {
            "contentType": "html",
            "content": "<h3>This is a simple message.</h3>"
        }
    }


    response = requests.post(message_url, json=message_body, headers=headers)
    return response.text



# ------------------------ to fetch messages ----------------------------------
    
    
def get_msg(email: str, ref_text: str) -> list[str]:
    chat_id = create_chatid(email)
    graph_api_endpoint = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
    headers= {"Authorization":"Bearer "+token_get['access_token']}
    req=requests.get(graph_api_endpoint,headers=headers)
    msg_list=[] # messages in tuple format (sender, message)
    idea_of_the_user = []

    for i in json.loads(req.text)['value'][-2::-1]:
      if 'from' in i.keys():
          msg_list.append((i['from']['user']['displayName'],i['body']['content']))

    for i in msg_list:
      if i[0] != 'Platforms  HQ':
          if ref_text.lower() in i[1].lower():
            idea_of_the_user.append(i[1].replace('\n', ' ').replace('</p>' ,'').replace('<p>', '').replace('&nbsp;', ''))

    return idea_of_the_user
    req=requests.get(graph_api_endpoint,headers=headers)


def get_msg_noref(email: str) -> list[tuple]:
    chat_id = create_chatid(email)
    graph_api_endpoint = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
    headers= {"Authorization":"Bearer "+token_get['access_token']}

    params = {
        'top': 3,  
        '$orderby': 'createdDateTime desc'  
    }

    req=requests.get(graph_api_endpoint,params=params,headers=headers)
    msg_list=[] # messages in tuple format (sender, message)

    for i in json.loads(req.text)['value'][-2::-1]:
      if 'from' in i.keys():
          msg_list.append([i['from']['user']['displayName'],i['body']['content']])


    for i in msg_list:
       i[1] = i[1].replace('\n', ' ').replace('</p>' ,'').replace('<p>', '').replace('&nbsp;', '')


    return msg_list


def get_total_chats(chat_id):
    url = f"https://graph.microsoft.com/v1.0/me/chats/{chat_id}/messages"
    headers = {
        "Authorization": f"Bearer {token_get['access_token']}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        # Count the number of threads
        total_chats = len(data['value'])
        
        return total_chats
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None



