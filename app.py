import time
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from core import run_simulation, get_confidence_interval
from typography import text, refurl


SIM_DAYS = 365

st.set_page_config(page_title='Ethereum APR simulator', page_icon='img/favicon.ico')
with open( "css/style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.title(text['title'])
st.markdown(text['subtitle'], unsafe_allow_html=True) 
st.markdown(text['legend'], unsafe_allow_html=True)



def main():
    left_column, right_column = st.columns((2, 5), gap='medium')

    client_validators = left_column.number_input('Number of your validators: ', value=10, min_value=1)
    annual_growth = left_column.number_input('Annual network growth:', value=200000)
    start_button = left_column.button('Start simulation')
    left_column.markdown(f"<a href='{refurl}' style='text-align: left; '>Try it yourself</a>", 
                         unsafe_allow_html=True)

    if start_button:
        with st.spinner('Simulating...'):
            time.sleep(3)
        data = run_simulation(client_validators, annual_growth, SIM_DAYS)

        scatter_plot = alt.Chart(data).mark_point(color='orangered').encode(
                                                                    x='Day', 
                                                                    y=alt.Y('APR', axis=alt.Axis(title='APR, %'))
                                                                    )

        table_content, spread = list(), list()
        for i in range(1, SIM_DAYS+1):
            min_rwd, max_rwd, deviation = get_confidence_interval(data['possible_total_per_day'].iloc[:i])
            min_apr = data['APR'].iloc[i-1]*(1-deviation)
            max_apr = data['APR'].iloc[i-1]*(1+deviation)

            if i in (30, 90, 365):
                reward_range = f'{round(min_rwd, 3)} - {round(max_rwd, 3)} ETH'
                apr_range = f'{round(min_apr, 2)} - {round(max_apr, 2)} %'
                huge_block_proba = f'{round(data["huge_block_probability"].iloc[:i].sum(), 2)} %' if data["huge_block_probability"].iloc[:i].sum() < 100 else '99.99 %'
                table_content.append([reward_range, apr_range, huge_block_proba])

            for _ in range(np.random.randint(3, 4 + 18*(SIM_DAYS-i)/SIM_DAYS)):
                APR = np.random.uniform(min_apr, max_apr)
                spread.append({'Day': i, 'APR': APR})

        scatter_plot += alt.Chart(pd.DataFrame(spread)).mark_point(opacity=0.35, size=1.5).encode(
                                                                                        x='Day', 
                                                                                        y=alt.Y('APR', axis=alt.Axis(title='APR, %'))
                                                                                        )

        right_column.altair_chart(scatter_plot, use_container_width=True)
        st.table(pd.DataFrame(table_content, columns=['Rewards', 'APR', 'Block >1 ETH probability'], index=['1 month', '3 months', 'Year']))


if __name__ == '__main__':
    main()
