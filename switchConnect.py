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
            device_address = line[1]
            port = line[2]
            port = port.replace("gabitEthernet","")
            if prev_address != device_address:
                cleanup_config(net_connect, port_list)
                ### Save config after all changes have been made
                if net_connect is not None:
                    net_connect.save_config()
                net_connect = ConnectHandler(
                    device_type = "cisco_xe",
                    host = device_address,
                    username = os.environ['PRIME_USERNAME'], 
                    password = os.environ['PRIME_PASSWORD'],
                )
                port_list = []
            port_list.append(port)
            output = modify_port(net_connect, port)
            prev_address = device_address
        cleanup_config(net_connect, port_list)
        ### Save config after all changes have been made
        net_connect.save_config()
    print("Executed in:", round(time.time() - st,1), "secs")

def modify_port(switch, port):
    ### Modify port config when necessary
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
        # config_output = switch.send_config_set(config_list)
        return config_output

def cleanup_config(switch, port_list):
    if switch is not None:
        all_ports = switch.send_command("sh int desc | i #televic_script")
        ### Transform ports string into list and remove unnecessary info
        all_ports = all_ports.split(sep= None, maxsplit=-1)
        ports_status = all_ports[1::4]
        all_ports = all_ports[0::4]
        ### Create list with all ports that still have televic config but no televic device connected
        old_ports = list(set(all_ports) - set(port_list))
        if len(old_ports) > 0:
            for old_port,port_status in zip(old_ports,ports_status):
                if port_status == "down":
                    config_list = [
                        "int " + old_port,
                        "default desc",
                        "power in auto",
                    ]
                    switch.send_config_set(config_list)
    return None

if __name__ == "__main__":
    load_dotenv()
    switch_login()