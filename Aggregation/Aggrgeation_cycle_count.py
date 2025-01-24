#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 17:07:22 2024

@author: sudiptamondal
"""

import numpy as np
import math
import pickle as pkl
from collections import Counter

class node_property():
    def __init__(self, neighbor_list, node_identity, total_edges, partition_id, cluster_id, intra_sub_cluster_edge, inter_sub_cluster_edge, inter_cluster_edge, intra_SC_dict={}, inter_SC_dict={}, inter_C_dict={}):
        self.neighbor_list = neighbor_list
        self.node_identity = node_identity
        self.total_edges = total_edges
  

def load_vertices(file_path):
    with open(file_path, "rb") as file:
        return pkl.load(file)

def process_sub_graph(sub_graph, vertices, gamma):
    num_edge_processed = 0
    removed_node_cnt = 0
    removed_nodes = []

    for curr_node in sub_graph:
        for nbr_iter in curr_node.neighbor_list[:]:
            nbr = vertices[nbr_iter]
            if nbr.sub_graph_presence:
                if nbr_iter != curr_node.node_identity:
                    vertices[nbr_iter].total_edges -= 1
                    vertices[nbr_iter].neighbor_list.remove(curr_node.node_identity)
                curr_node.total_edges -= 1
                curr_node.neighbor_list.remove(nbr_iter)
                num_edge_processed += 1

        if not curr_node.neighbor_list or curr_node.total_edges <= gamma:
            removed_node_cnt += 1
            removed_nodes.append(curr_node)
            curr_node.sub_graph_presence = []

    for curr_node in removed_nodes:
        sub_graph.remove(curr_node)

    return num_edge_processed, removed_node_cnt, removed_nodes

def refill_sub_graph(sub_graph, vertices, dram_index, buffer_cap, Vsize):
    fetch_cnt = 0
    k = dram_index
    while len(sub_graph) <= buffer_cap:
        if vertices[k].neighbor_list:
            sub_graph.append(vertices[k])
            vertices[k].sub_graph_presence.append(1)
            fetch_cnt += 1
        k = (k + 1) % Vsize
        if k == dram_index:
            break
    return k, fetch_cnt

def check_all_nodes_done(vertices):
    return all(not v.neighbor_list for v in vertices)

def main(file_path, buffer_cap, gamma):
    vertices = load_vertices(file_path)
    Vsize = len(vertices)
    sub_graph = vertices[:buffer_cap]

    for v in sub_graph:
        v.sub_graph_presence.append(1)

    total_removal = 0
    dram_index = buffer_cap
    num_off_chip_acc = 4096
    round_count = 0

    num_edge_processed_list = []
    cycle_count_list = []
    removed_count_list = []

    for iter in range(50):
        num_edge_processed, removed_node_cnt, removed_nodes = process_sub_graph(sub_graph, vertices, gamma)

        num_edge_processed_list.append(num_edge_processed)
        cycle_count_list.append(math.ceil(num_edge_processed / 256))
        removed_count_list.append(removed_node_cnt)

        if removed_node_cnt > 0:
            dram_index, fetch_cnt = refill_sub_graph(sub_graph, vertices, dram_index, buffer_cap, Vsize)
            num_off_chip_acc += fetch_cnt

        total_removal += removed_node_cnt

        if check_all_nodes_done(vertices):
            print(f'all nodes processed in iter {iter + 1}')
            break
    else:
        print(f'Completed {iter + 1} iterations and could not process all nodes')

    proceesed_node_cnt = sum(1 for nodes in vertices if nodes.total_edges <= 0)

    print("proceesed_node_cnt:", proceesed_node_cnt)
    print("off_chip_acc:", ((num_off_chip_acc * 128) / (1024 ** 2)))

if __name__ == "__main__":
    file_path = input("Enter the path to the vertex data file: ")
    buffer_cap = int(input("Enter the buffer capacity: "))
    gamma = int(input("Enter the gamma value: "))
    main(file_path, buffer_cap, gamma)
