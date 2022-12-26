import requests, os, csv, urllib.parse, urllib3
from dotenv import load_dotenv
from netmiko import ConnectHandler

def switch_login():

    # Read output file switch addresses
    with open("output.csv", "r") as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        prev_address = ""
        for line in reader:
            device_address = line[1]
            port = line[2]
            if prev_address != device_address:
                print("this is a new session")
                net_connect = ConnectHandler(
                    device_type = "cisco_xe",
                    host = device_address,
                    username = os.environ['PRIME_USERNAME'],
                    password = os.environ['PRIME_PASSWORD'],
                )
            output = modify_port(net_connect, port)
            # print(output)
            prev_address = device_address

def modify_port(switch, port):
    config_list = [ "int " + port,]; config_output = None
    port_power = switch.send_command("sh power in  " + port )
    if "static" not in port_power:
        # config_list += ["power in static max 30000",]
        print("power set")
    port_description = switch.send_command("sh int " + port + " description")
    if "#televic_script" not in port_description:
        # config_list += ["description #televic_script",]
        print("description set")
    if len(config_list) > 1:
        config_output = switch.send_config_set(config_list)
        switch.save_config()
    return config_output

if __name__ == "__main__":
    load_dotenv()
    switch_login()