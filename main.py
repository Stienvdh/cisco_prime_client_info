import requests, os, csv, urllib.parse, urllib3, time
from dotenv import load_dotenv

TELEVIC_DEVICE_TYPE = "Multimedia Handset touch"

urllib3.disable_warnings()

def generate_switch_interface_list():
    st = time.time()
    result = []
    i = 0

    ### Read input MAC addresses
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
    ### Order result by switch ipimport requests, os, csv, urllib.parse, urllib3, time
from dotenv import load_dotenv
from netmiko import ConnectHandler

TELEVIC_DEVICE_TYPE = "Multimedia Handset touch"

urllib3.disable_warnings()

def generate_switch_interface_list():
    st = time.time()
    result = []
    i = 0
    print("Connecting with Cisco Prime")
    ### Read input MAC addresses
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
    ### Order result by switch ip
    result = sorted(result, key=lambda x: x['ip'])
    switch_login(result)
    # !!! Write output switches/ports !!!
    # with open("output.csv", "w") as f:
        # writer = csv.writer(f, delimiter=";", lineterminator="\n")
        # writer.writerow(["Device MAC", "Switch IP", "Switch interface"])
        # for entry in result:
            # writer.writerow([entry['device'], entry['ip'], entry['port']])
    elapsed_time = time.time() - st
    print(len(result), "Televic devices found.")
    print("Executed in:", round(elapsed_time,1), "secs")

def find_switch_for_mac(mac):
    prime_host = os.environ['PRIME_HOST']
    prime_user = os.environ['PRIME_USERNAME']
    prime_pass = os.environ['PRIME_PASSWORD']
    ### Get client details for given MAC address
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
        
def switch_login(reader):
    # reader = [{'ip': 'MEC01-2Fc2-SWA1', 'port': 'Gi2/0/43'}, {'ip': 'MEC01-2Fc2-SWA1', 'port': 'Gi5/0/45'}, {'ip': 'MEC01-2Hc2-SWA2', 'port': 'Gi3/0/10'}, {'ip': 'MEC01-2Hc6-SWA2', 'port': 'Gi3/0/6'}, {'ip': 'ZOE50-0S4-SWR2', 'port': 'Gi1/0/6'}, {'ip': 'MEC01-3Fc2-SWA1', 'port': 'Gi4/0/28'}, {'ip': 'MEC01-3Hc2-SWA2', 'port': 'Gi1/0/20'}, {'ip': 'MEC01-3Hc6-SWA1', 'port': 'Gi5/0/2'}]
    reader = [{'ip': 'MEC01-2Fc2-SWA1', 'port': 'Gi1/0/6'}]
    port_list = []
    net_connect = None
    result = []
    ### Read output file switch addresses
    prev_address = ""
    for line in reader:
        newline = []
        device_address = line["ip"]
        port = line["port"]
        port = port.replace("gabitEthernet","")
        # Log in to the switch
        if prev_address != device_address:
            print("Connecting to", device_address)   
            result += cleanup_config(net_connect, port_list, prev_address)
            net_connect = switch_connect(device_address)
            port_list = []
        port_list.append(port)    
        newline += [{
                        "ip" : device_address,
                        "port" : port,
                    }]
        port_power = net_connect.send_command("sh power in  " + port )
        if "static" not in port_power:
            newline[0].update({
            "power" : "30w"
                })
        port_description = net_connect.send_command("sh int " + port + " description")
        if "#max_poe" not in port_description:
            newline[0].update({
            "description" : "add tag"
                })
        if len(newline[0]) > 2:
            result += newline
        
        prev_address = device_address
    result += cleanup_config(net_connect, port_list, prev_address)   
    result += remaining_switches(result)
    result = sorted(result, key=lambda x: x['ip'])
    # !!! Write output switches/ports !!!
    print("Writing output to output.csv")
    with open("output.csv", "w") as f:
        writer = csv.writer(f, delimiter=";", lineterminator="\n")
        writer.writerow(["Switch IP", "Switch interface", "Updating power to", "Updating description to"])
        for entry in result:
            writer.writerow([entry['ip'], entry['port'], entry['power'], entry['description']])

def cleanup_config(switch, port_list, address):
    result = []
    if switch is not None:
        all_ports = switch.send_command("sh int desc | i #max_poe")
        ### Transform ports string into list and remove unnecessary info
        all_ports = all_ports.split(sep= None, maxsplit=-1)
        ports_status = all_ports[1::4]
        all_ports = all_ports[0::4]
        ### Create list with all ports that still have televic config but no televic device connected
        old_ports = list(set(all_ports) - set(port_list))
        if len(old_ports) > 0:
            print("gathering old televic ports from" , address)
            for old_port,port_status in zip(old_ports,ports_status):
                result += [{
                        "ip" : address,
                        "port" : old_port,
                        "power" : "auto",
                        "description" : "remove tag"
                    }]
    return result          

def remaining_switches(output):
    with open("3850_swa_switchen_short.csv", "r") as f:
        all_switches = []
        current_switches = []
        reader = csv.reader(f, delimiter=';')
        result = []
        for row in reader:
            all_switches += row
        
        for row in output:
            current_switches.append(row["ip"])
        
        input = set(all_switches) - set(current_switches)
        for line in input:
            switch = switch_connect(line)
            result += cleanup_config(switch, [], line)
            
        return result
            
        
        
    

def switch_connect(address):
    result = ConnectHandler(
                device_type = "cisco_xe",
                host = address,
                username = os.environ['PRIME_USERNAME'], 
                password = os.environ['PRIME_PASSWORD'],
            )
    return result

if __name__ == "__main__":
    load_dotenv()
    # generate_switch_interface_list()
    switch_login(None)

    result = sorted(result, key=lambda x: x['ip'])
    
    ### Write output switches/ports
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
    ### Get client details for given MAC address
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
