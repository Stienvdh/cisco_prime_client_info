import requests, os, csv, urllib.parse
from dotenv import load_dotenv

TELEVIC_DEVICE_TYPE = "Multimedia Handset touch"

def generate_switch_interface_list():
    result = []

    # Read input MAC addresses
    with open("input.csv", "r") as f:
        reader = csv.reader(f, delimiter=';')
        for line in reader:
            device_type = line[3]
            device_mac = line[6]
            if device_type == TELEVIC_DEVICE_TYPE:
                switch_ip, switch_interface = find_switch_for_mac(device_mac)
                result += [{
                    "device" : device_mac,
                    "ip" : switch_ip,
                    "port" : switch_interface
                }]
    
    # Write output switches/ports
    with open("output.csv", "w") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Device MAC", "Switch IP", "Switch interface"])
        for entry in result:
            writer.writerow([entry['device'], entry['ip'], entry['port']])

def find_switch_for_mac(mac):
    prime_host = os.environ['PRIME_HOST']
    prime_user = os.environ['PRIME_USERNAME']
    prime_pass = os.environ['PRIME_PASSWORD']

    # Get client details for given MAC address
    url = f"{prime_host}/webacs/api/v4/data/Clients?macAddress=\"{mac}\".json"
    resp = requests.request("GET", "https://" + urllib.parse.quote(url), verify=False, auth=requests.auth.HTTPBasicAuth(prime_user, prime_pass), verify=False)
    print(f"Response from Prime (status code): {resp.status_code}")
    print(f"Response from Prime (text): {resp.text}")
    resp_data = resp.json()['queryResponse']['entity']['clientsDTO']
    switch_ip = resp_data['deviceIpAddress']['address']
    switch_interface = resp_data['clientInterface']

    return (switch_ip, switch_interface)

if __name__ == "__main__":
    load_dotenv()
    generate_switch_interface_list()
