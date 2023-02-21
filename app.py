import streamlit as st
import pandas as pd
import numpy as np


def run_simulation(n_validators, annual_growth):

    values = np.random.normal(loc=0, scale=1, size=365)
    df = pd.DataFrame({
                      'Date': pd.date_range(start='2023-01-01', periods=365, freq='D'), 
                      'APR': values.cumsum()
                      })
    df['APR'] = df['APR'] / ((n_validators * 32) + annual_growth/100*np.random.random())

    return df.set_index('Date')


def main():
    st.title('APR Calculator')
    left_column, right_column = st.columns((2, 5))

    n_validators = left_column.number_input('Number of your validators: ', value=10)
    annual_growth = left_column.number_input('Annual network growth:', value=200_000)
    start_button = left_column.button('Start Simulation')

    if start_button:
        results = run_simulation(n_validators, annual_growth)

        right_column.line_chart(results)

        st.write(f"Profit: {results['APR'].pct_change().mean() * 365 * 100:.2f}%")
        st.write(f"Huge block probability: {float(results[results['APR'] > 0].min()):.5f}%")


if __name__ == '__main__':
    main()


