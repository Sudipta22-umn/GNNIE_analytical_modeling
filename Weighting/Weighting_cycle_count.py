import numpy as np
import csv
import math
import copy

def read_csv(file_path):
    """Read the CSV file and return the rows."""
    with open(file_path) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        return [row for row in readCSV]

def process_rows(rows):
    """Process rows to get non-zero counts, locations, and block indices."""
    non_zero_count_list = []
    all_non_zero_location_list = []
    all_block_index_list = []
    all_block_index_list_16 = []

    for row in rows:
        non_zero_count = 0
        non_zero_location_list = []
        block_index_list = []
        block_index_list_16 = []

        for item_track, item in enumerate(row, start=1):
            if float(item) > 0:
                non_zero_count += 1
                non_zero_location_list.append(item_track)
                block_index_list.append(int(item_track / 32))

        non_zero_count_list.append(non_zero_count)
        all_non_zero_location_list.append(non_zero_location_list)
        all_block_index_list.append(block_index_list)
        all_block_index_list_16.append(block_index_list_16)

    return non_zero_count_list, all_non_zero_location_list, all_block_index_list, all_block_index_list_16

def calculate_block_cycle_counts(all_block_index_list, num_blocks=16):
    """Calculate the block cycle counts for each row."""
    all_block_cycle_count_list = []

    for item_1 in all_block_index_list:
        block_cycle_count_list = [0] * num_blocks
        for blocks in item_1:
            block_cycle_count_list[blocks] += 1
        all_block_cycle_count_list.append(block_cycle_count_list)

    return all_block_cycle_count_list

def calculate_workload(all_block_cycle_count_list, num_blocks=16):
    """Calculate the workload for each processing element (PE)."""
    all_workload_list = []

    for k in range(num_blocks):
        pe_workload_list = []
        for j in range(len(all_block_cycle_count_list)):
            pe_workload_list.append(all_block_cycle_count_list[j][k])
        all_workload_list.append(pe_workload_list)

    return all_workload_list

def calculate_node_assignments(all_workload_list):
    """Calculate node assignments based on non-zero workload."""
    return [np.count_nonzero(element) for element in all_workload_list]

def sort_non_zero_workloads(all_workload_list):
    """Sort the non-zero workloads for each PE."""
    return [sorted([i for i in element if i != 0]) for element in all_workload_list]

def calculate_average_workload(non_zero_workloads, num_blocks=16):
    """Calculate the average workload per processing element."""
    total_workload = sum(sum(z) for z in non_zero_workloads)
    return total_workload / num_blocks

def calculate_cycle_counts(non_zero_workloads, mac_nums):
    """Calculate the cycle counts based on MAC numbers."""
    cycle_count_list = []

    for load in non_zero_workloads:
        cycle_count = 0
        for item_load in load:
            if item_load <= mac_nums[0]:
                cycle_count += 1
            else:
                cycle_count += math.ceil(item_load / mac_nums[0])

        cycle_count_list.append(cycle_count)

    return cycle_count_list

def cycle_calculation_variable_mac(variable_mac_list, ordered_list):
    """Calculate cycle counts using variable MAC list."""
    cycle_count_order_list = []
    feature_index = 1

    for feature in ordered_list:
        cycle_count_order = 0
        mac_num_order = get_mac_num_order(variable_mac_list, feature_index)
        
        for item_feature in feature:
            if item_feature <= mac_num_order:
                cycle_count_order += 1
            else:
                cycle_count_order += math.ceil(item_feature / mac_num_order)
        
        cycle_count_order_list.append(cycle_count_order)
        feature_index += 1

    return cycle_count_order_list

def get_mac_num_order(variable_mac_list, feature_index):
    """Get MAC number order based on feature index."""
    if(feature_index <= 2):
            return variable_mac_list[0]
        
    if(feature_index > 2  and feature_index <= 4):
        return variable_mac_list[1]
    
    if(feature_index > 4  and feature_index <= 6):
        return variable_mac_list[1]
    
    if(feature_index > 6  and feature_index <= 8):
        return variable_mac_list[1]
        
    if(feature_index > 8  and feature_index <= 10):
        return variable_mac_list[2]
    
    if(feature_index > 10  and feature_index <= 12):
        return variable_mac_list[2]
        
    if(feature_index > 12  and feature_index <= 14):
        return variable_mac_list[3]
    
    if(feature_index > 14):
        return variable_mac_list[3]
        
def redistribute_workloads(ordered_list):
    """Redistribute workloads to balance the load."""
    redistributed_list = copy.deepcopy(ordered_list)

    for s in range(len(redistributed_list)):
        if s <= 1:
            r = 15 - s
            p = len(redistributed_list[s]) - 1
            for m in range(math.ceil(p / 6)):
                redistributed_list[s].append(redistributed_list[r][m])
                redistributed_list[r].remove(redistributed_list[r][m])

    return redistributed_list

def second_pass_redistribution(redistributed_list):
    """Perform a second pass of redistribution."""
    redistributed_list_2 = copy.deepcopy(redistributed_list)

    for s in range(len(redistributed_list_2)):
        if 1 < s <= 3:
            r = 15 - s
            p = len(redistributed_list_2[s]) - 1
            for m in range(math.ceil(p / 8)):
                redistributed_list_2[s].append(redistributed_list_2[r][m])
                redistributed_list_2[r].remove(redistributed_list_2[r][m])

    return redistributed_list_2

def main():
    file_path = 'pubmed_ordered.csv'
    rows = read_csv(file_path)
    
    non_zero_count_list, all_non_zero_location_list, all_block_index_list, all_block_index_list_16 = process_rows(rows)
    
    all_block_cycle_count_list = calculate_block_cycle_counts(all_block_index_list)
    
    all_workload_list = calculate_workload(all_block_cycle_count_list)
    
    node_assignment_list = calculate_node_assignments(all_workload_list)
    
    non_zero_workloads = sort_non_zero_workloads(all_workload_list)
    
    average_workload = calculate_average_workload(non_zero_workloads)
    #print("Average workload:", average_workload)
    
    mac_nums = [3, 4, 7]
    cycle_count_list_low = calculate_cycle_counts(non_zero_workloads, [mac_nums[0]])
    cycle_count_list_up = calculate_cycle_counts(non_zero_workloads, [mac_nums[1]])
    cycle_count_list_top = calculate_cycle_counts(non_zero_workloads, [mac_nums[2]])
    #print(f'Cycle required for lower config: {min(cycle_count_list_low)}')
    #print(f'Cycle required for upper config: {min(cycle_count_list_up)}')
    #print(f'Cycle required for top config: {min(cycle_count_list_top)}')
    
    mac_list = [4, 4, 5, 6]
    cycle_count_order_list_3 = cycle_calculation_variable_mac(mac_list, non_zero_workloads)
    #print(f'Cycle required with FM only : {min(cycle_count_order_list_3)}')
    
    redistributed_list = redistribute_workloads(non_zero_workloads)
    redistributed_list_2 = second_pass_redistribution(redistributed_list)
    
    ordered_list_2 = sorted(redistributed_list_2, key=sum)
    cycle_count_order_list_3_re = cycle_calculation_variable_mac(mac_list, ordered_list_2)
    print(f'Cycle required with FM + LR: {min(cycle_count_order_list_3_re)}')
    
    # The rest of the code for saving the results can be added here

if __name__ == "__main__":
    main()
