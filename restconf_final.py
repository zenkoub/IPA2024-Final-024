import json
import requests
import time
requests.packages.urllib3.disable_warnings()

router_ip = "10.0.15.61"

api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface="
api_url_status = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces-state/interface="

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

basicauth = ("admin", "cisco")

def check_interface(loopback_name, retries=3):
    url = api_url + loopback_name
    for i in range(retries):
        resp = requests.get(url, auth=basicauth, headers=headers, verify=False)
        if resp.status_code == 200:
            return 200
    print(f"Checking {loopback_name}: {resp.status_code}, {resp.text}")
    return resp.status_code


def create(student_id):
    loopback_name = f"Loopback{student_id}"
    if check_interface(loopback_name) == 200:
        return f"Cannot create: Interface {loopback_name}"

    last3 = int(str(student_id)[-3:])
    x = last3 // 100
    y = last3 % 100
    if y == 0:
        y = 1
    ip_addr = f"172.{x}.{y}.1"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": loopback_name,
            "description": f"Interface for student {student_id}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [{"ip": ip_addr, "netmask": "255.255.255.0"}]
            }
        }
    }

    resp = requests.put(
        api_url + loopback_name,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )
    
    print("PUT Response:", resp.status_code, resp.text)

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {loopback_name} is created successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def delete(student_id):
    loopback_name = f"Loopback{student_id}"
    if check_interface(loopback_name) != 200:
        return f"Cannot delete: Interface {loopback_name}"
    
    resp = requests.delete(
        api_url + loopback_name,
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {loopback_name} is deleted successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def enable(student_id):
    loopback_name = f"Loopback{student_id}"
    if check_interface(loopback_name) != 200:
        return f"Cannot enable: Interface {loopback_name}"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "enabled": True
        }
    }

    resp = requests.patch(
        api_url + loopback_name,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {loopback_name} is enabled successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def disable(student_id):
    loopback_name = f"Loopback{student_id}"
    if check_interface(loopback_name) != 200:
        return f"Cannot shutdown: Interface {loopback_name}"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "enabled": False
        }
    }

    resp = requests.patch(
        api_url + loopback_name,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {loopback_name} is disabled successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def status(student_id):
    loopback_name = f"Loopback{student_id}"
    url = api_url_status + loopback_name

    resp = requests.get(url, auth=basicauth, headers=headers, verify=False)

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        admin_status = response_json["ietf-interfaces:interface"]["admin-status"]
        oper_status = response_json["ietf-interfaces:interface"]["oper-status"]
        if admin_status == 'up' and oper_status == 'up':
            return f"Interface {loopback_name} is enabled"
        elif admin_status == 'down' and oper_status == 'down':
            return f"Interface {loopback_name} is disabled"
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return f"No Interface {loopback_name}"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))

def gigabit_status():
    url = "https://" + router_ip + "/restconf/data/ietf-interfaces:interfaces-state"
    resp = requests.get(url, auth=basicauth, headers=headers, verify=False)
    
    if resp.status_code != 200:
        return f"Error: Unable to retrieve interfaces. Status code: {resp.status_code}"
    
    data = resp.json()
    result = []
    for iface in data["ietf-interfaces:interfaces-state"]["interface"]:
        if "GigabitEthernet" in iface["name"]:
            name = iface["name"]
            admin = iface["admin-status"]
            oper = iface["oper-status"]
            result.append(f"{name}: admin={admin}, oper={oper}")

    if not result:
        return "No GigabitEthernet interfaces found."
    else:
        return "\n".join(result)
    
def showrun():
    url = "https://" + router_ip + "/restconf/data/Cisco-IOS-XE-native:native"
    resp = requests.get(url, auth=basicauth, headers=headers, verify=False)

    if resp.status_code != 200:
        return f"Error: Cannot retrieve running-config. HTTP {resp.status_code}"

    with open("showrun.json", "w") as f:
        json.dump(resp.json(), f, indent=2)

    print("Running configuration saved to showrun.json")
    return "ok"