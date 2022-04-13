import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


df2 = pd.read_excel('assets/mi_2021_oor_data.xlsx', sheet_name='Sheet1')
df2 = df2[['COUNTY/METRO','Income needed to afford 1 bdrm FMR', 'Income needed to afford 2 bdrm FMR']]
df2 = df2.dropna()

st.title('Income needed to afford Fair Market Rent (FMR)')

#Toggle data display
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df2)

#County multiselect
if st.checkbox('Show filtered data'):
    st.subheader('Filtered data')
    full_county_list = list(df2['COUNTY/METRO'].values)
    options = st.multiselect('Select counties to inspect - at most 3 locations',
    full_county_list)
    
    button = st.button("Print Locations",disabled=False)

    
    if len(options) <= 3:
        our_counties = options
        df2 = df2[df2['COUNTY/METRO'].isin(our_counties)]
        df2 = pd.melt(df2, id_vars=['COUNTY/METRO'])
        st.write(df2)
    else:
        st.warning("You have to select only 3 locations")


#g.despine(left=True)
#g.set_axis_labels("Counties", "Annual Income to afford Fair Market Rent")
#g.legend.set_title("")
sns.set_style('whitegrid')
if st.checkbox('Show our county chart'):
    #import seaborn as sns
    #st.subheader('Annual Income Needed to Afford FMR')
    #sns.catplot(data=df2, kind='bar',
    #x='COUNTY/METRO', y='value', hue='variable', palette='dark', alpha=.6, height=6)
    #st.pyplot()
    x = np.arange(len(df2['COUNTY/METRO'].unique()))
    labels = list(df2['COUNTY/METRO'].unique())
    width = 0.35
    one_bd = df2.loc[df2['variable']=='Income needed to afford 1 bdrm FMR', 'value']
    two_bd = df2.loc[df2['variable']=='Income needed to afford 2 bdrm FMR', 'value']
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, one_bd, width, label='1 bdrm')
    rects2 = ax.bar(x + width/2, two_bd, width, label='2 bdrm')
    ax.set_ylabel('Annual Income Needed to Afford 1 Bdrm FMR')
    ax.set_title('Income for FMR by County - 1 and 2 Bedrooms')
    ax.legend()
    fig.tight_layout()
    plt.xticks(x, labels)
    st.pyplot(fig)

    with st.expander("Click for explanation"):
     st.write("""
        In 2019 in the USA, a renter household needs an annual income of $51,789 to afford a two-bedroom rental home at the 
        Fair Market Rent.

        "Affordable" rents represent the generallly accepted standard of spending no more than 30% of gross income on gross 
        housing costs.

        Calculation: 
        Multiply the FMR for a unit of a particular size by 12 to get the yearly rental cost (2BR: 1,294.73 x 12 = 15,537). 
        Then divide by .3 to determine the total income needed to afford 15,537 per year in rent (115,537 / .3 = 51,789).
        
        Source: NLIHC Out of Reach 2021
     """)