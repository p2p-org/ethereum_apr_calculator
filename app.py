import math
import numpy as np
import pandas as pd
import scipy
import streamlit as st


def run_simulation(client_validators, annual_growth):
    current_validators_count = 523715

    # --- cl
    cl_df = pd.DataFrame()
    cl_df['Day'] = range(0, 365, 1)
    cl_df['epoch_in_day'] = 225
    cl_df['validators'] = range(current_validators_count, current_validators_count + annual_growth - int(annual_growth / 365), int(annual_growth / 365))
    cl_df['p_for_block_proposal'] = 1 / cl_df['validators'] * 7200
    cl_df['base_reward_per_increment'] = cl_df['validators'].apply(lambda x: 64 / math.sqrt(x * 31.999705 * pow(10, 9)))
    cl_df['issue_per_day'] = cl_df['base_reward_per_increment'] * 32 * cl_df['epoch_in_day'] * cl_df['validators']
    cl_df['attestation_reward_per_day'] = (14 + 26 + 14) / 64 * 32 * cl_df['base_reward_per_increment'] * 225
    cl_df['possible_sync_reward_per_day'] = (2 / (32 * 512 * 64)) * cl_df['validators'] * 32 * cl_df['base_reward_per_increment'] * 7200 * (512 * 225 / 256 / cl_df['validators'])
    cl_df['possible_proposal_reward_per_day'] = cl_df['validators'] / 32 * 8 / (64 - 8) * cl_df['attestation_reward_per_day'] / 255 * cl_df['p_for_block_proposal']

    cl_df['possible_consensus_reward'] = (cl_df['attestation_reward_per_day'] + cl_df['possible_sync_reward_per_day'] + cl_df['possible_proposal_reward_per_day']) * client_validators

    cl_df['rt_sum_cl'] = cl_df['possible_consensus_reward'].cumsum()

    # el
    expect_block_cost = 0.1079552666 # weighted average by blocks  0 - 100 eth
    el_df = pd.DataFrame()
    el_df['Day'] = range(0, 365, 1)
    el_df['epoch_in_day'] = 225
    el_df['validators'] = range(current_validators_count, current_validators_count + annual_growth - int(annual_growth / 365), int(annual_growth / 365))

    el_df['possible_execution_reward'] = 1 / cl_df['validators'] * 7200 * client_validators * expect_block_cost  # block values for client validators

    el_df['rt_sum_el'] = el_df['possible_execution_reward'].cumsum()

    cl_df = cl_df[['Day', 'possible_consensus_reward', 'rt_sum_cl']]
    el_df = el_df[['Day', 'possible_execution_reward', 'rt_sum_el']]
    res = cl_df.merge(el_df, how='left', on='Day')
    res['cumulative_reward'] = res['rt_sum_cl'] + res['rt_sum_el']
    res['cumulative_apr'] = res['cumulative_reward'] / (client_validators * 32) * 100


    print('consensus:')
    print(res['possible_consensus_reward'])
    print('------')
    print('execution:')
    print(res['possible_execution_reward'])

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
    
    return f'{round(lower_bound, 3)} - {round(upper_bound, 3)} ETH'

def main():
    st.title('APR Calculator')
    left_column, right_column = st.columns((2, 5))

    client_validators = left_column.number_input('Number of your validators: ', value=10)
    annual_growth = left_column.number_input('Annual network growth:', value=200000)
    start_button = left_column.button('Start Simulation')

    if start_button:
        results = run_simulation(client_validators, annual_growth)

        right_column.line_chart(results, x='Day', y='APR')

        st.write(f"1 month rewards: {get_confidence_interval(results['possible_total_per_day'].iloc[:30])}")
        st.write(f"3 months rewards: {get_confidence_interval(results['possible_total_per_day'].iloc[:90])}")
        st.write(f"Year rewards: {get_confidence_interval(results['possible_total_per_day'].iloc[:365])}")


if __name__ == '__main__':
    main()
