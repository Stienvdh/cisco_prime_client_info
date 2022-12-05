import requests, os, csv, urllib.parse, urllib3
from dotenv import load_dotenv
from netmiko import ConnectHandler

def switch_login():

    # Read output file switch addresses
    with open("output.csv", "r") as f:
        reader = csv.reader(f, delimiter=';')
        for line in reader:
            device_address = line[1]
            net_connect = ConnectHandler(
                device_type = "cisco_xe",
                host = device_address,
                username = os.environ['PRIME_USERNAME'],
                password = os.environ['PRIME_PASSWORD'],
)

output = net_connect.send_command(
    "show ip arp"
)
print(output) 
                
if __name__ == "__main__":
    load_dotenv()
    switch_login()