import subprocess
import os

def showrun(studentID):
    router_name = "CSR1KV-Pod1-1"
    filename = f"show_run_{studentID}_{router_name}.txt"

    command = ["ansible-playbook",  "playbook.yaml"]

    result = subprocess.run(command, capture_output=True, text=True)
    result = result.stdout

    if 'ok=2' in result:
        return filename
    else:
        return "Error: Ansible"
