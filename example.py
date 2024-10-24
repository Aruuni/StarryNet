#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
StarryNet: empowering researchers to evaluate futuristic integrated space and terrestrial networks.
author: Zeqi Lai (zeqilai@tsinghua.edu.cn) and Yangtao Deng (dengyt21@mails.tsinghua.edu.cn)
"""

from starrynet.sn_observer import *
from starrynet.sn_orchestrater import *
from starrynet.sn_synchronizer import *

def load_config(config_file_path):
    with open(config_file_path, 'r') as file:
        config = json.load(file)
    return config

if __name__ == "__main__":
    configuration_file_path = "./config.json"
    config = load_config(configuration_file_path)
    # Starlink 5*5: 25 satellite nodes, 2 ground stations.
    # The node index sequence is: 25 sattelites, 2 ground stations.
    # In this example, 25 satellites and 2 ground stations are one AS.

    # 50.110924, 8.682127 FRANKFURT
    # 37.532600, 127.024612 SEOUL 
    # 44.439663, 26.096306 BUCURESTI
    # 51.509865, -0.118092 LONDON

    SATELLITES = config["# of satellites"] * config["# of orbit"]
    print (SATELLITES)
    AS = [[1, SATELLITES + 4]]  # Node #1 to Node #27 are within the same AS.
    GS_lat_long = [[26.1952052,-12.7316508], [-19.4134112,23.1653584],
                   [-22.2063933,26.3963913], [-49.2888288,69.3817622]]  # latitude and longitude of frankfurt and  Austria

    print('Start StarryNet.')
    sn = StarryNet(configuration_file_path, GS_lat_long, config["update_time (s)"], AS)
    sn.create_nodes()
    sn.create_links()
    sn.run_routing_deamon()

    neighbors_inode_index1 = 4
    neighbors_inode_index2 = 27
    neighbors_inode_index3 = 5
    neighbors_index_time = 1

    # neighbors_index1 = sn.get_neighbors(neighbors_inode_index1, neighbors_index_time)
    # print("neighbors_index: " + str(neighbors_index1))
    # neighbors_index2 = sn.get_neighbors(neighbors_inode_index2, neighbors_index_time)
    # print("neighbors_index: " + str(neighbors_index2))
    # neighbors_index3 = sn.get_neighbors(neighbors_inode_index3, neighbors_index_time)
    # print("neighbors_index: " + str(neighbors_index3))

    
    # # distance between nodes at a certain time
    # node_distance = sn.get_distance(node_index1, node_index2, time_index)
    # print("node_distance (km): " + str(node_distance))

    # # neighbor node indexes of node at a certain time
    # neighbors_index = sn.get_neighbors(node_index1, time_index)
    # print("neighbors_index: " + str(neighbors_index))

    # GS connected to the node at a certain time
    # node_index1 = 7
    # GSes = sn.get_GSes(node_index1, time_index)
    # print("GSes are: " + str(GSes))

    # LLA of a node at a certain time
    #LLA = sn.get_position(node_index1, time_index)
    #print("LLA: " + str(LLA))


    # ping msg of two nodes at a certain time. The output file will be written at the working directory.
    for i in range(1, config["Duration (s)"]):
        time_ping = i
        # ping msg of two nodes at a certain time. The output file will be written at the working directory.
        #sn.set_ping(SATELLITES + 1, SATELLITES + 2, time_index)
        #sn.set_ping(SATELLITES + 3, SATELLITES + 4, time_index)
        sn.set_ping(SATELLITES + 1, SATELLITES + 2, time_ping)
        sn.set_ping(SATELLITES + 3, SATELLITES + 4, time_ping)
        #sn.set_ping(1, 50, time_ping)
        node_from = SATELLITES + 4
        node_to = 94

        node_from = SATELLITES + 4
        node_to = 95


    # perf msg of two nodes at a certain time. The output file will be written at the working directory.
    sn.set_perf(SATELLITES + 1, SATELLITES + 2, 2)
    sn.set_perf(SATELLITES + 3, SATELLITES + 4, 2)

    sn.start_emulation()
    sn.stop_emulation()
