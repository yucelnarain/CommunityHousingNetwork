import altair as alt
from altair import datum
import pandas as pd
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
    parser.add_argument('ASSETS_PATH', help='input path for datasets')
    parser.add_argument('COUNTY', help='GrossRent by BedRooms file (json)')
    parser.add_argument('COST_BURDEN_INCOME', help='Cost burden by income transformed file (csv)')
    parser.add_argument('COST_BURDEN_TENURE', help='Cost burden by tenure transformed file (csv)')
    parser.add_argument('GROSS_RENT_BY_BEDROOMS', help='GrossRent by BedRooms file (csv)')    
    parser.add_argument('COST_BURDEN_INCOME_IMG', help='Cost burden by income output viz file (html)')
    parser.add_argument('COST_BURDEN_TENURE_IMG', help='Cost burden by tenure output viz file(html)')
    parser.add_argument('GROSS_RENT_BY_BEDROOMS_IMG', help='GrossRent by BedRooms file (html)')    
    
    args = parser.parse_args()            
    county = args.COUNTY
    
# create visualization for metric - cost_burden_by_income    
    cost_burden_income_df = pd.read_csv(args.ASSETS_PATH + args.COST_BURDEN_INCOME)
    income_cols = list(cost_burden_income_df.columns)

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
    income_chart.save(args.ASSETS_PATH + args.COST_BURDEN_INCOME_IMG, embed_options={'renderer':'svg'})
    
# create visualization for metric - cost_burden_by_tenure    
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
    tenure_chart.save(args.ASSETS_PATH + args.COST_BURDEN_TENURE_IMG, embed_options={'renderer':'svg'})
    
# create visualization for metric - gross_rent_by_bedrooms    
    sort_order = ['No Rooms', '1 Room', '2 Rooms', '3 Rooms', '4 Rooms', '5 or more Rooms']
    gross_rent_est_df = pd.read_csv(args.ASSETS_PATH + args.GROSS_RENT_BY_BEDROOMS)
    bars = alt.Chart(gross_rent_est_df).mark_bar(color='orange').encode(
            x=alt.X('No_of_Rooms:N', sort=sort_order, axis=alt.Axis(title='')),
            y = alt.Y('Rent:Q',axis=alt.Axis(title='Median Gross Rent in Dollars -($)')),
            tooltip=['No_of_Rooms', 'Rent']
    ).transform_filter(datum.NAME == f'{county}'
    ).properties(width=350, height=350, title='Median Gross Rent by Bedrooms - ' + f'{county}')

    grossRentByBedrooms_chart = bars.configure_title(fontSize=20
    ).configure_axis(labelFontSize=15, titleFontSize=17)    
    
    grossRentByBedrooms_chart.save(args.ASSETS_PATH + args.GROSS_RENT_BY_BEDROOMS_IMG, embed_options={'renderer':'svg'})