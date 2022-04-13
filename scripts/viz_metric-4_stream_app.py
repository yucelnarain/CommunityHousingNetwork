import streamlit as st
import altair as alt
from altair import datum
import pandas as pd
import numpy as np
import argparse
alt.renderers.enable('svg')


# Utitlities to create Bars and Text viz for cost_burden metrics 
def createBars(df, cols, county, labelTitle, tooltipTitle, col_sort_order):
    metricCol1 = cols[0]
    metricCol2 = cols[1]
    groupbyCol = cols[1:3]
    valueCol = cols[3]
    bars = alt.Chart(df
            ).transform_joinaggregate(
                total=f'sum({valueCol})',
                groupby=[f'{groupbyCol[0]}', f'{groupbyCol[1]}']
            ).transform_calculate(
                pct = alt.datum.value / alt.datum.total
            ).mark_bar().encode(
                x=alt.X('pct:Q', stack='zero',
                        axis=alt.Axis(format='%', title='', ticks=False)),
                y=alt.Y(f'{metricCol2}:N', axis=alt.Axis(title=''), sort=col_sort_order),
                color=alt.Color(f'{metricCol1}:N',
                    scale=alt.Scale(domain=cost_burden_display, range=range_),
                    legend=alt.Legend(orient='none', direction='horizontal',
                    legendY=-30, title=f'{labelTitle}', 
                    titleAnchor='middle', titleFontSize=15)),
                order=alt.Order('cost_burden_index:Q', sort='ascending'),
                tooltip=[
                        alt.Tooltip(f'{metricCol1}:N'),
                        alt.Tooltip(f'{valueCol}:Q', title=f'{tooltipTitle}'),
                        alt.Tooltip('pct:Q', title='Percent', format='0.0%')                    
                      ]
      ).transform_filter(datum.county == f'{county}') 
    return(bars)

def createText(df, cols, county, labelTitle, col_sort_order):
        metricCol1 = cols[0]
        metricCol2 = cols[1]
        groupbyCol = cols[1:3]
        valueCol = cols[3]  
        text = alt.Chart(df
                ).transform_joinaggregate(
                      total=f'sum({valueCol})',
                      groupby=[f'{groupbyCol[0]}', f'{groupbyCol[1]}']
                ).transform_calculate(
                      pct = alt.datum.value / alt.datum.total
                ).mark_text(dx=-10, dy=3, color='white').encode(
                            x=alt.X('pct:Q', stack='zero',
                                    axis=alt.Axis(format='.1%', title='', ticks=False)),
                            y=alt.Y(f'{metricCol2}:N', axis=alt.Axis(title=''), sort=col_sort_order),
                            text=alt.Text('pct:Q', format='.0%'),
                            detail='pct:Q',
                            order=alt.Order('cost_burden_index:Q',
                                            sort='ascending')
                ).transform_filter(datum.county == f'{county}')
        return(text)
    
cost_burden_display = ['Severly Cost Burdened (50% or more)', 'Cost Burdened (30% or more, but less than 50%)','Unburdened (Less than 30%)']
household_incomes_ord = ['Extremely Low Income (0-30% AMI)', 'Very Low Income (31-50% AMI)',  \
                             'Low Income (51-80% AMI)', '80+% AMI']
cost_burden_ord = ['Severly Cost Burdened (50% or more)', 'Cost Burdened (30% or more, but less than 50%)','Unburdened (Less than 30%)']  
range_ = ['#7e537f','#e4891e', '#eab676']

tenure_ord = ['Renter', 'Owner', 'Total']
labelTitle = 'Level of Cost Burden'
tooltipTitle = 'Cost Burdened Households'


if __name__ == '__main__':    
    parser = argparse.ArgumentParser()
#     parser.add_argument('ASSETS_PATH', help='input path for datasets')
#     parser.add_argument('COST_BURDEN_INCOME', help='Cost burden by income transformed file (csv)')
#     parser.add_argument('COST_BURDEN_TENURE', help='Cost burden by income transformed file (csv)')      

    
    args = parser.parse_args()    
    args.ASSETS_PATH = 'assets/'
    args.COST_BURDEN_INCOME = 'cost_burden_income.csv'
    args.COST_BURDEN_TENURE = 'cost_burden_tenure.csv'
    
    cost_burden_income_df = pd.read_csv(args.ASSETS_PATH + args.COST_BURDEN_INCOME)
    income_cols = list(cost_burden_income_df.columns) 
    county_list = tuple(cost_burden_income_df.county.unique())
    add_county = st.sidebar.selectbox(
                    'Which County you would like to explore?',
                       county_list)
    county = add_county
    
    bars = createBars(cost_burden_income_df, income_cols, county, labelTitle, tooltipTitle, household_incomes_ord)
    text = createText(cost_burden_income_df, income_cols, county, labelTitle, household_incomes_ord)
                      

    income_chart = (bars + text
                     ).properties(width=600, height=400, title={"text" : 'Cost Burden By Income - ' + f'{county} (2014-2018)',
                                              "subtitle" : 'Percent of Households',
                                              "fontSize": 25,
                                              "subtitleFontSize":20,
                                              "anchor":"start"}
                    ).configure_view(strokeWidth=0
                    ).configure_axis(labelFontSize=15, 
                                     grid=False, domain=False,labelLimit=250
                    ).configure_legend(labelLimit=0)    
    
    idx = cost_burdened_idx = np.where((cost_burden_income_df['county'] == county) &
                                 (cost_burden_income_df['household_income'] == 'Extremely Low Income (0-30% AMI)'))
    cost_burdened_idx = np.where((cost_burden_income_df['county'] == county)  &
                                   (cost_burden_income_df['household_income'] == 'Extremely Low Income (0-30% AMI)') &
                                   (cost_burden_income_df['cost_burden'].isin(['Severly Cost Burdened (50% or more)', 
                                                                'Cost Burdened (30% or more, but less than 50%)'])))

    cost_burden_stat = round(cost_burden_income_df.loc[cost_burdened_idx].sum()['value'] * 100  \
                                            / cost_burden_income_df.loc[idx].sum()['value'], 2)
    cost_burden_brief = str(cost_burden_stat) + '% of extremely low-income households (0-30% AMI) in ' + county + ' are cost burdened.'
    
    
    cost_burden_tenure_df = pd.read_csv(args.ASSETS_PATH + args.COST_BURDEN_TENURE)
    tenure_cols = list(cost_burden_tenure_df.columns)

    bars = createBars(cost_burden_tenure_df, tenure_cols, county, labelTitle, tooltipTitle, tenure_ord)
    text = createText(cost_burden_tenure_df, tenure_cols, county, labelTitle, tenure_ord)

    tenure_chart = (bars + text
                     ).properties(width=600, height=400, title={"text" : 'Cost Burden By Tenure - ' +f'{county} (2014-2018)',
                                              "subtitle" : 'Percent of Households',
                                              "fontSize": 25,
                                              "subtitleFontSize":20,
                                              "anchor":"start"}
                    ).configure_view(strokeWidth=0
                    ).configure_axis(labelFontSize=15, 
                                     grid=False, domain=False,labelLimit=250
                    ).configure_legend(labelLimit=0)    
    
    idx = cost_burdened_idx = np.where((cost_burden_tenure_df['county'] == county) &
                                 (cost_burden_tenure_df['tenure'] == 'Renter'))
    tenure_idx = np.where((cost_burden_tenure_df['county'] == county)  &
                                   (cost_burden_tenure_df['tenure'] == 'Renter') &
                                   (cost_burden_tenure_df['cost_burden'].isin(['Severly Cost Burdened (50% or more)', 
                                                                'Cost Burdened (30% or more, but less than 50%)'])))

    tenure_stat = round(float(cost_burden_tenure_df.loc[tenure_idx].sum()['value']) * 100   \
                                            / float(cost_burden_tenure_df.loc[idx].sum()['value']), 2)
    tenure_brief = str(tenure_stat) + ' % of the renters in ' + county + ' are cost burdened.'

    county = add_county
    gross_rent_est_df = pd.read_csv(args.ASSETS_PATH + 'gross_rent_est.csv')
    sort_order = ['No Rooms', '1 Room', '2 Rooms', '3 Rooms', '4 Rooms', '5 or more Rooms']
    gross_rent_by_bedrooms_chart = alt.Chart(gross_rent_est_df).mark_bar(color='orange').encode(
                x=alt.X('No_of_Rooms:N', sort=sort_order, axis=alt.Axis(title='')),
                y = alt.Y('Rent:Q',axis=alt.Axis(title='Median Gross Rent in Dollars -($)')),
                tooltip=['No_of_Rooms', 'Rent']
    ).transform_filter(datum.NAME == f'{county}'
    ).configure_title(fontSize=20
    ).configure_axis(labelFontSize=15, titleFontSize=17
    ).properties(width=600, height=400, title='Median Gross Rent by Bedrooms - ' + f'{county}')

    st.title('CHN Affordable Housing Dashboard')
    st.title('')

    choosen_metric = st.sidebar.selectbox(
        'Which metric you would like to see?',
        ('Cost burden by Income', 'Cost burden by Tenure', 'Gross Rent By Bedrooms')
    )

    explore_metric = st.sidebar.selectbox(
        'How you would like to explore metric?',
        ('Explore Tabular Data', 'Explore Chart')
    )

    df_indx = np.where(cost_burden_income_df['county'] == county)
    dashboard_brief = "**Certain households are more likely than others to live in an unaffordable home.**\
                        Cost burden is unevenly distributed among county residents based on income, race and ethnicity, housing tenure   (whether they own or rent), and age. An equitable approach to reducing cost burden will reduce the disparities where the need is the greatest."
    st.write(dashboard_brief)
    if choosen_metric == 'Cost burden by Income':
        if explore_metric == 'Explore Tabular Data':
            st.write(cost_burden_income_df.loc[df_indx])
        else:
            st.altair_chart(income_chart, use_container_width=True)
        st.write(str(cost_burden_brief))
        st.write('Data Source: https://www.huduser.gov/portal/dataset/chas-api.html')
    elif choosen_metric == 'Cost burden by Tenure':
        if explore_metric == 'Explore Tabular Data':
            st.write(cost_burden_tenure_df)
        else:        
            st.altair_chart(tenure_chart, use_container_width=True)
        st.write(tenure_brief)
        st.write('Data Source: https://www.huduser.gov/portal/dataset/chas-api.html')
    else:
        if explore_metric == 'Explore Tabular Data':
            st.write(gross_rent_est_df[gross_rent_est_df['NAME'] == county])
        else:
            st.altair_chart(gross_rent_by_bedrooms_chart)
        st.write('Source: https://api.census.gov/')