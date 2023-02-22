import streamlit as st
import pandas as pd
import math


def run_simulation(n_validators, annual_growth):
    current_validators_count = 523715
    annul_grow = annual_growth
    client_validators = n_validators

    # --- cl
    cl_df = pd.DataFrame()
    cl_df['day'] = range(0, 365, 1)
    cl_df['epoch_in_day'] = 225
    cl_df['validators'] = range(current_validators_count, current_validators_count + annul_grow - int(annul_grow / 365),
                                int(annul_grow / 365))
    cl_df['p_for_block_proposal'] = 1 / cl_df['validators'] * 7200
    cl_df['base_reward_per_increment'] = cl_df['validators'].apply(lambda x: 64 / math.sqrt(x * 31.999705 * pow(10, 9)))
    cl_df['issue_per_day'] = cl_df['base_reward_per_increment'] * 32 * cl_df['epoch_in_day'] * cl_df['validators']
    cl_df['attestation_reward_per_day'] = (14 + 26 + 14) / 64 * 32 * cl_df['base_reward_per_increment'] * 225
    cl_df['possible_sync_reward_per_day'] = (2 / (32 * 512 * 64)) * cl_df['validators'] * 32 * cl_df[
        'base_reward_per_increment'] * 7200 * (512 * 225 / 256 / cl_df['validators'])
    cl_df['possible_proposal_reward_per_day'] = cl_df['validators'] / 32 * 8 / (64 - 8) * cl_df[
        'attestation_reward_per_day'] / 255 * cl_df['p_for_block_proposal']

    cl_df['client_consensus_reward'] = (cl_df['attestation_reward_per_day'] + cl_df['possible_sync_reward_per_day'] +
                                        cl_df[
                                            'possible_proposal_reward_per_day']) * client_validators

    cl_df['rt_sum_cl'] = cl_df['client_consensus_reward'].cumsum()

    expect_block_cost = 0.1079552666
    el_df = pd.DataFrame()
    el_df['day'] = range(0, 365, 1)
    el_df['epoch_in_day'] = 225

    el_df['validators'] = range(current_validators_count, current_validators_count + annul_grow - int(annul_grow / 365),
                                int(annul_grow / 365))
    el_df['block_proposal'] = 1 / cl_df['validators'] * 7200  # blocks for 1 validator
    el_df['block_proposal_client'] = 1 / cl_df[
        'validators'] * 7200 * client_validators * expect_block_cost  # blocks for client validators

    el_df['rt_sum_el'] = el_df['block_proposal_client'].cumsum()

    cl_df = cl_df[['day', 'rt_sum_cl']]
    el_df = el_df[['day', 'rt_sum_el']]
    res = cl_df.merge(el_df, how='left', on='day')
    res['total'] = res['rt_sum_cl'] + res['rt_sum_el']
    res['apr'] = res['total'] / (client_validators * 32) * 100

    return res


def main():
    st.title('APR Calculator')
    left_column, right_column = st.columns((2, 5))

    n_validators = left_column.number_input('Number of your validators: ', value=10)
    annual_growth = left_column.number_input('Annual network growth:', value=200000)
    start_button = left_column.button('Start Simulation')

    if start_button:
        results = run_simulation(n_validators, annual_growth)

        right_column.line_chart(results, x='day', y='apr')
        #column_3.line_chart(results, x='day', y='apr')
        #column_4.bar_chart(results, x='day', y='apr')
        #column_5.bar_chart(results, x='day', y='apr')

        st.write(f"30  days rewards: {round(results['total'][29], 3)} ETH")
        st.write(f"90  days rewards: {round(results['total'][89], 3)} ETH")
        st.write(f"365 days rewards: {round(results['total'][364], 3)} ETH")


if __name__ == '__main__':
    main()
