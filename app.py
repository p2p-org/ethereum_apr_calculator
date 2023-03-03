import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from core import run_simulation, get_confidence_interval


SIM_DAYS = 365

st.title('Ethereum staking APR simulator') # prediction, modelling
hide_streamlit_style = """<style>
                            #MainMenu {visibility: hidden;}
                            footer {visibility: hidden;}
                       </style>"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def main():
    left_column, right_column = st.columns((2, 5))

    client_validators = left_column.number_input('Number of your validators: ', value=10)
    annual_growth = left_column.number_input('Annual network growth:', value=300000)
    start_button = left_column.button('Start Simulation')
    left_column.markdown("<a href='https://p2p.org/networks/ethereum/staking-application' style='text-align: left; '>Try it yourself</a>", 
                         unsafe_allow_html=True)

    if start_button:
        data = run_simulation(client_validators, annual_growth)

        scatter_plot = alt.Chart(data).mark_point(color='orangered').encode(
                                                                    x='Day', 
                                                                    y=alt.Y('APR', axis=alt.Axis(title='APR, %'))
                                                                    )
        diagram = right_column.altair_chart(scatter_plot, use_container_width=True)

        spread = list()
        for i in range(1, SIM_DAYS+1):
            deviation = get_confidence_interval(data['possible_total_per_day'].iloc[:i])[1]
            min_apr = data['APR'].iloc[i-1]*(1-deviation)
            max_apr = data['APR'].iloc[i-1]*(1+deviation)

            for _ in range(np.random.randint(3, 4 + 18*(SIM_DAYS-i)/SIM_DAYS)):
                APR = np.random.uniform(min_apr, max_apr)
                spread.append({'Day': i, 'APR': APR})

        scatter_plot += alt.Chart(pd.DataFrame(spread)).mark_point(opacity=0.35, size=1.5).encode(
                                                                                        x='Day', 
                                                                                        y=alt.Y('APR', axis=alt.Axis(title='APR, %'))
                                                                                        )

        diagram.altair_chart(scatter_plot, use_container_width=True)


        st.write(f"1 month rewards: {get_confidence_interval(data['possible_total_per_day'].iloc[:30])[0]}")
        st.write(f"3 months rewards: {get_confidence_interval(data['possible_total_per_day'].iloc[:90])[0]}")
        st.write(f"Year rewards: {get_confidence_interval(data['possible_total_per_day'].iloc[:365])[0]}")


if __name__ == '__main__':
    main()
