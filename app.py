import math
import numpy as np
import pandas as pd
import scipy
import streamlit as st
import random
import altair as alt

hide_streamlit_style = """<style>
                            #MainMenu {visibility: hidden;}
                            footer {visibility: hidden;}
                       </style>"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def run_simulation(client_validators, annual_growth):
    current_validators_count = 550715

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
    cl_df['possible_proposal_reward_per_day'] = cl_df['validators'] / 32 * 8 / (64 - 8) * cl_df['attestation_reward_per_day'] / 225 * cl_df['p_for_block_proposal']

    cl_df['possible_consensus_reward'] = (cl_df['attestation_reward_per_day'] + cl_df['possible_sync_reward_per_day'] + cl_df['possible_proposal_reward_per_day']) * client_validators

    # el
    expect_block_cost = 0.1079552666 # weighted average by blocks  0 - 100 eth
    el_df = pd.DataFrame()
    el_df['Day'] = range(0, 365, 1)
    el_df['epoch_in_day'] = 225
    el_df['validators'] = range(current_validators_count, current_validators_count + annual_growth - int(annual_growth / 365), int(annual_growth / 365))

    el_df['possible_execution_reward'] = 1 / cl_df['validators'] * 7200 * client_validators * expect_block_cost  # block values for client validators

    cl_df = cl_df[['Day', 'possible_consensus_reward']]
    el_df = el_df[['Day', 'possible_execution_reward']]
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
    
    return f'{round(lower_bound, 3)} - {round(upper_bound, 3)} ETH', deviation

def main():
    st.title('APR Calculator')
    left_column, right_column = st.columns((2, 5))

    client_validators = left_column.number_input('Number of your validators: ', value=10)
    annual_growth = left_column.number_input('Annual network growth:', value=300000)
    start_button = left_column.button('Start Simulation')
    left_column.markdown("<a href='https://p2p.org/networks/ethereum/staking-application' style='text-align: left; color: white;'>Try it yourself</a>", 
                         unsafe_allow_html=True)

    if start_button:
        data = run_simulation(client_validators, annual_growth)

        scatter_plot = alt.Chart(data).mark_point(color='green').encode(x='Day', y='APR')
        diagram = right_column.altair_chart(scatter_plot, use_container_width=True)

        spread = list()
        for i in range(1,366):
            deviation = get_confidence_interval(data['possible_total_per_day'].iloc[:i])[1]
            min_apr = data['APR'].iloc[i-1]*(1-deviation)
            max_apr = data['APR'].iloc[i-1]*(1+deviation)

            for _ in range(random.randint(3, 5)):
                spread.append({'Day': i, 'APR': np.random.uniform(min_apr, max_apr)})

        spread = pd.DataFrame(spread)
        scatter_plot = scatter_plot + alt.Chart(spread).mark_point().encode(x='Day', y='APR')
        diagram.altair_chart(scatter_plot, use_container_width=True)


        st.write(f"1 month rewards: {get_confidence_interval(data['possible_total_per_day'].iloc[:30])[0]}")
        st.write(f"3 months rewards: {get_confidence_interval(data['possible_total_per_day'].iloc[:90])[0]}")
        st.write(f"Year rewards: {get_confidence_interval(data['possible_total_per_day'].iloc[:365])[0]}")


if __name__ == '__main__':
    main()
