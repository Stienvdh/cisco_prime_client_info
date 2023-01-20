import requests, os, csv, urllib.parse, urllib3, time
from dotenv import load_dotenv
from netmiko import ConnectHandler

def switch_login():
    st = time.time()
    port_list = []
    net_connect = None
    ### Read output file switch addresses
    with open("output.csv", "r") as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        prev_address = ""
        for line in reader:
            device_address = line[0]
            port = line[1]
            if prev_address != device_address:
                ### Save config after all changes have been made
                if net_connect is not None:
                    print("Saving config")
                    # cleanup_config(net_connect, port_list)
                    # net_connect.save_config()
                print("Connecting to", device_address)
                net_connect = ConnectHandler(
                    device_type = "cisco_xe",
                    host = device_address,
                    username = os.environ['PRIME_USERNAME'], 
                    password = os.environ['PRIME_PASSWORD'],
                )
                port_list = []
            port_list.append(port)
            output = modify_port(net_connect, port, line)
            prev_address = device_address
        # cleanup_config(net_connect, port_list)
        ### Save config after all changes have been made
        print("Saving config")
        # net_connect.save_config()
    print("Executed in:", round(time.time() - st,1), "secs")
### add port number to prints
def modify_port(switch, port, line):
    ### Modify port config when necessary
    config_list = [ "int " + port,]; config_output = None
    
    port_power = line[2]
    if "30w" in port_power:
        config_list += ["power in static max 30000",]
        print("power set to 30w")
        
    port_description = line[3]
    if "add" in port_description:
        ### add tag behind description
        description = switch.send_command("sh int " + port + " description")
        description = description.split(sep= None, maxsplit=-1)
        description = description[3::4]
        if len(description) <= 1:
            description += " "
            print(description)
        config_list += ["description "+ description[1] + " #max_poe",]
        print("description set")
        
    if len(config_list) <= 1:
        cleanup_config(switch, port, line)
    config_output = switch.send_config_set(config_list)
    return config_output

def cleanup_config(switch, port, line):
    ### Modify port config when necessary
    config_list = [ "int " + port,]; config_output = None
    
    port_power = line[2]
    if "auto" in port_power:
        config_list += ["power in auto",]
        print("power set to auto")
        
    port_description = line[3]
    if "remove" in port_description:
        description = switch.send_command("sh int " + port + " description")
        description = description.split(sep= None, maxsplit=-1)
        description = description[3::4]
        ### add tag behind description
        config_list += ["description "+ description[1],]
        print("Description changed back to" , description[1])
        
    config_output = switch.send_config_set(config_list)
    return config_output
    
if __name__ == "__main__":
    load_dotenv()
    switch_login()