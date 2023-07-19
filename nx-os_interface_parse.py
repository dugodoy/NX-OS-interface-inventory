#!/usr/bin/python

#import getpass, asks for the password and shows as secret
import getpass
#import regex
import re
#import scrapli
from scrapli.driver.core import NXOSDriver
#import threading pool
from multiprocessing.dummy import Pool as ThreadPool
#import date and time
from datetime import datetime
import time

##########################################################################
##########################################################################
##########################################################################

##########################################################################
####################### Function extract_devices #########################
##########################################################################

def extract_devices(device_file):
    list_devices=[]
    read_devices = open(device_file)
    for line in read_devices:
        line = line.strip()
        dict_devices = {'host': line,
                        'auth_username': username,
                        'auth_password': password,
                        'auth_strict_key': False}
        list_devices.append(dict_devices)
    return list_devices

##########################################################################
##########################################################################
##########################################################################

##########################################################################
######################### Function session_conn ##########################
##########################################################################

def session_conn(conn_device):
    print("Connecting to device "+conn_device['host'])
    conn = NXOSDriver(**conn_device, timeout_ops=360)
    conn.open()
    hostname = conn.get_prompt()
    print("Connected to device "+conn_device['host'])
    print("Getting Outputs from device "+conn_device['host'])
    sc_output = conn.send_command("show interface")
    sc_output2 = conn.send_command("show interface switchport")
    sc_channels = conn.send_command("show port-channel summary")
    sc_inttype = conn.send_command("show interface transceiver")
    sc_cdp_neighbors = conn.send_command("show cdp neighbor detail")
    output = sc_output.textfsm_parse_output()
    output2 = sc_output2.textfsm_parse_output()
    channels = sc_channels.textfsm_parse_output()
    tranceivers = sc_inttype.genie_parse_output()
    cdp_neighbors = sc_cdp_neighbors.textfsm_parse_output()
    file_output = open(conn_device['host']+".txt", mode='w')
    file_output.write(str(output))
    file_output.write("\n"+"-"*18+" show")
    file_output.write("\n"+"-"*18+" show"+"\n\n")
    file_output.write(str(output2))
    file_output.write("\n"+"-"*18+" show")
    file_output.write("\n"+"-"*18+" show"+"\n\n")
    file_output.write(str(channels))
    file_output.write("\n"+"-"*18+" show")
    file_output.write("\n"+"-"*18+" show"+"\n\n")
    file_output.write(str(tranceivers))
    file_output.write("\n"+"-"*18+" show")
    file_output.write("\n"+"-"*18+" show"+"\n\n")
    file_output.write(str(cdp_neighbors))
    file_output.close
    conn.close()
    print("Connection closed to device "+conn_device['host'])
    int_list=[]
    int_vlan_list=[]
    print("Processing Output from device "+conn_device['host'])
    for out1 in output:
        cdp_remote_host = "-"
        cdp_remote_int = "-"
        cdp_remote_plat = "-"

        if out1['last_link_flapped'] == "":
            link_flap = "-"
        else:
            link_flap = out1['last_link_flapped']

        link_flap = out1['last_link_flapped']
        channel = "-"
        int_trans = "-"
        interface = out1['interface']
        protocol = out1['admin_state']
        int_trans = 'No Transceiver Present'

        if out1['link_status'] == "":
            status = "-"
        else:
            status = out1['link_status']

        description = out1['description']
        speed = out1['speed']
        duplex = out1['duplex']
        mode = out1['mode']
        mtu = out1['mtu']

        if out1['ip_address'] == "":
            ip = "-"
        else:
            ip = out1['ip_address']


        if "Vlan" in interface:
            speed = "-"
            duplex = "-"
            int_trans = "-"
            mode = "-"
            native = "-"
            vlans = "-"
            int_vlan_list.append([hostname+"&"+interface+"&"+description+"&"+status+"&"+protocol+"&"+speed+"&"+duplex+"&"+int_trans+"&"+channel+"&"+mode+"&"+native+"&"+vlans+"&"+ip+"&"+mtu+"&"+cdp_remote_host+"&"+cdp_remote_plat+"&"+cdp_remote_int+"&"+link_flap])
        
        if "Ethernet" in interface:

            for po_channel in channels:
                
                for ch_int in po_channel['phys_iface']:
                    temp_int = re.search("Ethernet(.*?)$", interface).group(1)
                
                    if "Eth"+temp_int == ch_int:
                        channel = po_channel['bundle_iface']
                
                        if "R" in po_channel['bundle_status']:
                            temp_int_po = re.search("Po(.*?)$", po_channel['bundle_iface']).group(1)
                
                            for channel_int in output:
                
                                if "port-channel"+temp_int_po == channel_int['interface']:
                                    ip = channel_int['ip_address']

            for int_type in tranceivers:
                if interface == int_type:
                    if 'transceiver_present' in tranceivers[interface]:
                        if tranceivers[int_type]['transceiver_present']:
                            int_trans = tranceivers[interface]['transceiver_type']
                        else:
                            int_trans = 'No Transceiver Present'
                    else:
                        int_trans = 'No Transceiver Present'

            for neighbor in cdp_neighbors:
                if interface == neighbor['local_port']:
                    cdp_remote_host = neighbor['dest_host']
                    cdp_remote_plat = neighbor['platform']
                    cdp_remote_int = neighbor['remote_port']

            if mode == "":
                mode = "-"
                vlans = "-"
                native = "-"
                int_list.append([hostname+"&"+interface+"&"+description+"&"+status+"&"+protocol+"&"+speed+"&"+duplex+"&"+int_trans+"&"+channel+"&"+mode+"&"+native+"&"+vlans+"&"+ip+"&"+mtu+"&"+cdp_remote_host+"&"+cdp_remote_plat+"&"+cdp_remote_int+"&"+link_flap])

            if mode == "routed":
                vlans = "-"
                native = "-"
                int_list.append([hostname+"&"+interface+"&"+description+"&"+status+"&"+protocol+"&"+speed+"&"+duplex+"&"+int_trans+"&"+channel+"&"+mode+"&"+native+"&"+vlans+"&"+ip+"&"+mtu+"&"+cdp_remote_host+"&"+cdp_remote_plat+"&"+cdp_remote_int+"&"+link_flap])

            if mode == "FabricPath":
                vlans = "-"
                native = "-"
                int_list.append([hostname+"&"+interface+"&"+description+"&"+status+"&"+protocol+"&"+speed+"&"+duplex+"&"+int_trans+"&"+channel+"&"+mode+"&"+native+"&"+vlans+"&"+ip+"&"+mtu+"&"+cdp_remote_host+"&"+cdp_remote_plat+"&"+cdp_remote_int+"&"+link_flap])

            if mode == "fex-fabric":
                vlans = "-"
                native = "-"
                int_list.append([hostname+"&"+interface+"&"+description+"&"+status+"&"+protocol+"&"+speed+"&"+duplex+"&"+int_trans+"&"+channel+"&"+mode+"&"+native+"&"+vlans+"&"+ip+"&"+mtu+"&"+cdp_remote_host+"&"+cdp_remote_plat+"&"+cdp_remote_int+"&"+link_flap])

            if mode == "access":
                for out2 in output2:
                    if out2['interface'] == interface:
                        vlans = out2['access_vlan']
                        native = "-"
                        mode = "access"
                        int_list.append([hostname+"&"+interface+"&"+description+"&"+status+"&"+protocol+"&"+speed+"&"+duplex+"&"+int_trans+"&"+channel+"&"+mode+"&"+native+"&"+vlans+"&"+ip+"&"+mtu+"&"+cdp_remote_host+"&"+cdp_remote_plat+"&"+cdp_remote_int+"&"+link_flap])

            if mode == "trunk":
                for out2 in output2:
                    if out2['interface'] == interface:
                        if out2['trunking_vlans'] == "1-4094":
                            vlans = "ALL"
                        else:
                            vlans = "'"+out2['trunking_vlans']
                        mode = "trunk"
                        native = out2['native_vlan']
                        int_list.append([hostname+"&"+interface+"&"+description+"&"+status+"&"+protocol+"&"+speed+"&"+duplex+"&"+int_trans+"&"+channel+"&"+mode+"&"+native+"&"+vlans+"&"+ip+"&"+mtu+"&"+cdp_remote_host+"&"+cdp_remote_plat+"&"+cdp_remote_int+"&"+link_flap])

    out_file = open('interface_output.txt', 'a')
    for item in int_list:
        print(item[0])
        out_file.write(item[0]+"\n")

    for int_vlan in int_vlan_list:
        print(int_vlan[0])
        out_file.write(int_vlan[0]+"\n")

##########################################################################
################################# Main ###################################
##########################################################################

#Asks username, password, enable secret and number of threads to be executed in parallel
num_threads_str = input("Number of threads (10): " ) or "10"
num_threads  = int( num_threads_str )
username = input("Username: ")
password = getpass.getpass("Password: ")

#Call function "extract_devices" passing filename where devices IP are stored
devices = extract_devices("devices.txt")

start_time = datetime.now()

#Create threadpool and call function session_conn passing "devices" list
threads=ThreadPool(num_threads)
exec_thread=threads.map(session_conn, devices)
threads.close()
threads.join()


print("\nElapsed time: " + str(datetime.now() - start_time))

##########################################################################
##########################################################################
##########################################################################