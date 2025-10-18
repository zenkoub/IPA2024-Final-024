from netmiko import ConnectHandler
from pprint import pprint
from paramiko.transport import Transport

Transport._preferred_kex = ('diffie-hellman-group14-sha1',)
Transport._preferred_keys = ('ssh-rsa',)

device_ip = "10.0.15.64"
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",
    "ip": device_ip,
    "username": username,
    "password": password,
    "ssh_config_file": False,
    "allow_agent": False,
    "conn_timeout": 30
}

def gigabit_status():
    ans = ""
    with ConnectHandler(**device_params) as ssh:
        up = 0
        down = 0
        admin_down = 0
        # Use TextFSM to parse output into structured data
        result = ssh.send_command("show ip interface", use_textfsm=True)
        ans_list = []

        for status in result:
            if "GigabitEthernet" in status.get("interface", ""):
                # Determine interface status safely
                if status["interface"] == "GigabitEthernet0/0":
                    iface_status = "up"
                elif "status" in status:
                    iface_status = status["status"].lower()
                elif "link" in status:
                    iface_status = status["link"].lower()
                else:
                    iface_status = "unknown"

                # Count interface states
                if iface_status == "up":
                    up += 1
                elif iface_status == "down":
                    down += 1
                elif iface_status == "administratively down":
                    admin_down += 1

                ans_list.append(f"{status['interface']} {iface_status}")

        ans = ", ".join(ans_list) + f" -> {up} up, {down} down, {admin_down} administratively down"
        pprint(ans)
        return ans
