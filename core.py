import math
import numpy as np
import pandas as pd
import scipy


def run_simulation(client_validators, annual_growth, sim_days):
    start_validators = 550_715

    # cl
    cl_df = pd.DataFrame()
    cl_df['Day'] = range(sim_days)
    cl_df['epoch_in_day'] = 225
    cl_df['validators'] = np.linspace(start_validators, start_validators + annual_growth, sim_days, dtype=int)
    cl_df['p_for_block_proposal'] = 1 / cl_df['validators'] * 7200
    cl_df['base_reward_per_increment'] = cl_df['validators'].apply(lambda x: 64 / math.sqrt(x * 31.999705 * pow(10, 9)))
    cl_df['issue_per_day'] = cl_df['base_reward_per_increment'] * 32 * cl_df['epoch_in_day'] * cl_df['validators']
    cl_df['attestation_reward_per_day'] = (14 + 26 + 14) / 64 * 32 * cl_df['base_reward_per_increment'] * 225
    cl_df['possible_sync_reward_per_day'] = (2 / (32 * 512 * 64)) * cl_df['validators'] * 32 * cl_df['base_reward_per_increment'] * 7200 * (512 * 225 / 256 / cl_df['validators'])
    cl_df['possible_proposal_reward_per_day'] = cl_df['validators'] / 32 * 8 / (64 - 8) * cl_df['attestation_reward_per_day'] / 225 * cl_df['p_for_block_proposal']

    cl_df['possible_consensus_reward'] = (cl_df['attestation_reward_per_day'] + cl_df['possible_sync_reward_per_day'] + cl_df['possible_proposal_reward_per_day']) * client_validators

    # el
    expect_block_cost = 0.1079552666 # weighted average by blocks  0 - 100 eth
    el_df = pd.DataFrame()
    el_df['Day'] = cl_df['Day']
    el_df['huge_block_probability'] = cl_df['p_for_block_proposal'] * (cl_df['validators'] - client_validators) / cl_df['validators'] * client_validators * 0.01 * 100 # 0.01 is proven proba, 100 for %

    el_df['possible_execution_reward'] = cl_df['p_for_block_proposal'] * client_validators * expect_block_cost  # block values for client validators

    cl_df = cl_df[['Day', 'possible_consensus_reward']]
    el_df = el_df[['Day', 'possible_execution_reward', 'huge_block_probability']]
    res = cl_df.merge(el_df, how='left', on='Day')

    res['possible_total_per_day'] = (res['possible_consensus_reward'] + res['possible_execution_reward'])
    res['APR'] = res['possible_total_per_day'] / (client_validators * 32) * 365 * 100

    return res

def get_confidence_interval(data):
    # asceding sort
    sorted_data = sorted(data)
    n = len(sorted_data)
    
    # list of cumulative sums
    cumsum = np.cumsum(sorted_data)

    median_sum = np.median(cumsum)
    std_sum = np.std(cumsum)
    
    # calculating conf interval for cumsum with 99% proba
    alpha = 0.01
    z_score = scipy.stats.norm.ppf(0.99) # 2.576
    lower_bound = median_sum - z_score * std_sum / np.sqrt(n) - np.sum(sorted_data) * alpha
    upper_bound = median_sum + z_score * std_sum / np.sqrt(n) + np.sum(sorted_data) * alpha
    
    deviation = (1 - lower_bound/((lower_bound + upper_bound)/2))
    
    return lower_bound, upper_bound, deviation