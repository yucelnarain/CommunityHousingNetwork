import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title('Sample Dashboard')

df1 = pd.read_csv('ACSDT1Y2019.B25070-2022-01-21T214228.csv')

# Toggle data display
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df1)


# Draw
county_option = st.selectbox("Select county", ('Macomb', 'Oakland', 'Wayne'))
if county_option == 'Macomb':
    county_filter = "Macomb County, Michigan!!Estimate"
elif county_option == 'Oakland':
    county_filter = "Oakland County, Michigan!!Estimate"
else:
    county_filter = "Wayne County, Michigan!!Estimate"


st.subheader(
    f'Gross Rent As A Percentage Of Household Income for {county_option} County In The Past 12 Months')


def strip(input):
    output = input.replace(",", "")
    return int(output)


hist_values = df1[county_filter][1:].apply(strip)
labels = df1['Label (Grouping)'][1:]
fig, ax = plt.subplots()
ax.bar(labels, hist_values)
plt.xticks(rotation='90')
st.pyplot(fig)
