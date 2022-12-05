import requests, os, csv, urllib.parse, urllib3, time
from dotenv import load_dotenv

TELEVIC_DEVICE_TYPE = "Multimedia Handset touch"

urllib3.disable_warnings()

def generate_switch_interface_list():
    st = time.time()
    result = []
    i = 0

    # Read input MAC addresses
    with open("input.csv", "r") as f:
        reader = csv.reader(f, delimiter=';')
        for line in reader:
            device_type = line[3]
            device_mac = line[6]
            if device_type == TELEVIC_DEVICE_TYPE and str(device_mac[0:5]) == '00:0E':
                switch = find_switch_for_mac(device_mac)
                if switch is not None:
                    switch_ip, switch_interface = switch
                    result += [{
                        "device" : device_mac,
                        "ip" : switch_ip,
                        "port" : switch_interface
                    }]
    
    # Write output switches/ports
    with open("output.csv", "w") as f:
        writer = csv.writer(f, delimiter=";", lineterminator="\n")
        writer.writerow(["Device MAC", "Switch IP", "Switch interface"])
        for entry in result:
            writer.writerow([entry['device'], entry['ip'], entry['port']])
    elapsed_time = time.time() - st
    print(len(result), "Televic devices found.")
    print("Executed in:", round(elapsed_time,1), "secs")

def find_switch_for_mac(mac):
    prime_host = os.environ['PRIME_HOST']
    prime_user = os.environ['PRIME_USERNAME']
    prime_pass = os.environ['PRIME_PASSWORD']
    # Get client details for given MAC address
    url = f"{prime_host}/webacs/api/v4/data/Clients.json?macAddress={mac.replace(':', '')}"
    resp = requests.request("GET", "https://" + url, verify=False, auth=requests.auth.HTTPBasicAuth(prime_user, prime_pass))
    query_response = resp.json()['queryResponse']
    if query_response['@count'] == 1:
        client_url = query_response['entityId'][0]['@url']
        client_resp = requests.request("GET", client_url + ".json", verify=False, auth=requests.auth.HTTPBasicAuth(prime_user, prime_pass))
        switch_det = client_resp.json()['queryResponse']['entity'][0]['clientsDTO']
        switch_ip = switch_det['deviceName']
        switch_interface = switch_det['clientInterface']

        return (switch_ip, switch_interface)

if __name__ == "__main__":
    load_dotenv()
    generate_switch_interface_list()
