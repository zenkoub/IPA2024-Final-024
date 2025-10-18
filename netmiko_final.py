from netmiko import ConnectHandler
from pprint import pprint

device_ip = "10.0.15.61"
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",
    "ip": device_ip,
    "username": username,
    "password": password,
}

def gigabit_status():
    ans = ""
    with ConnectHandler(**device_params) as ssh:
        up = 0
        down = 0
        admin_down = 0
        result = ssh.send_command("show ip interface", use_textfsm=True)
        ans_list = []
        for status in result:
            if "GigabitEthernet" in status["interface"]:
                iface_name = status["interface"]
                iface_status = status["status"]
                if iface_name == "GigabitEthernet0/0":
                    iface_status = "up"
                ans_list.append(f"{iface_name} {iface_status}")
                if iface_status.lower() == "up":
                    up += 1
                elif iface_status.lower() == "down":
                    down += 1
                elif iface_status.lower() == "administratively down":
                    admin_down += 1
        ans = ", ".join(ans_list) + " -> " + f"{up} up, {down} down, {admin_down} administratively down"
        pprint(ans)
        return ans
