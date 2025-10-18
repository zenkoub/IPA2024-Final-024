#######################################################################################
# Yourname: Koobun Kritnetithat
# Your student ID: 66070024
# Your GitHub Repo: https://github.com/zenkoub/IPA2024-Final-024

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.
import os
import time
import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import restconf_final as rc
import netmiko_final as nc
import ansible_final as ac

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.

ACCESS_TOKEN = os.environ.get("WEBEX_TOKEN")

room_response = requests.get(
    "https://webexapis.com/v1/rooms",
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
)
print(room_response.status_code)
print(room_response.text)

rooms = room_response.json()["items"]

for room in rooms:
    if room["title"] == "66070024":  # Change this to your actual Webex room name if needed
        roomId = room["id"]
        print("Using room:", room["title"])
        break

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = os.environ.get("WEBEX_ROOM_ID")


while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    if message.startswith("/"):
        try:
            parts = message.split()
            studentID = parts[0][1:]
            command = parts[1].lower()
        except IndexError:
            continue
        print(command)

# 5. Complete the logic for each command

        if command == "create":
            responseMessage = rc.create(studentID)
        elif command == "delete":
            responseMessage = rc.delete(studentID)
        elif command == "enable":
            responseMessage = rc.enable(studentID)
        elif command == "disable":
            responseMessage = rc.disable(studentID)
        elif command == "status":
            responseMessage = rc.status(studentID)
        elif command == "gigabit_status":
            responseMessage = rc.gigabit_status()
        elif command == "showrun":
            responseMessage = rc.showrun()
        else:
            responseMessage = "Error: No command or unknown command"
        
# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail

        if command == "showrun" and responseMessage == 'ok':
            filename = "showrun.json"
            fileobject = open(filename, "rb")
            filetype = "application/json"
            
            postData = {
                "roomId": roomId,
                "text": "show running config",
                "files": (filename, fileobject, filetype),
            }
            
            postData = MultipartEncoder(postData)
            HTTPHeaders = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": postData.content_type,
            }
        # other commands only send text, or no attached file.
        else:
            print("Response from RESTCONF:", responseMessage)

            postData = {"roomId": roomId, "text": responseMessage}
            postData = json.dumps(postData)

            # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
            HTTPHeaders = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json",
            }   

        # Post the call to the Webex Teams message API.
        r = requests.post(
            "https://webexapis.com/v1/messages",
            data=postData,
            headers=HTTPHeaders,
        )
        
        print("Webex POST response:", r.status_code, r.text)
        
        if not r.status_code in [200, 201]:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
            )
