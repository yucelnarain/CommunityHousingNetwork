import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go


df1 = pd.read_csv('ACSDT1Y2019.B25070-2022-01-21T214228.csv', decimal=",")


# Toggle data display
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df1)


# Barplot container
with st.container():
    # Draw barplot
    county_option = st.selectbox("Select county", ('Macomb', 'Oakland', 'Wayne'))
    if county_option == 'Macomb':
        county_filter = "Macomb County, Michigan!!Estimate"
    elif county_option == 'Oakland':
        county_filter = "Oakland County, Michigan!!Estimate"
    else:
        county_filter = "Wayne County, Michigan!!Estimate"

    st.subheader(
        f'Gross rent as a percentage of household income for {county_option} county in the past 12 months (in thousands)')

    hist_values = df1[county_filter][1:]
    labels = df1['Label (Grouping)'][1:]
    # fig, ax = plt.subplots()
    # ax.bar(labels, hist_values)
    # plt.xticks(rotation='90')
    # st.pyplot(fig)

    fig = px.bar(x=labels, y=hist_values)
    fig.update_layout(xaxis=go.layout.XAxis(tickangle=270))
    fig.update_yaxes(title_text="Number of households (in thousands)")

    st.plotly_chart(fig)


    # Explanation
    with st.expander("See explanation"):
        st.markdown("Gross Rent as a Percent of Household Income (GRAPHI) is th\
            e percent of household income that is allocated to gross rent for \
            housing. When this measure exceeds 30%, the household is often living\
             at risk of financial catastrophe. These individuals are often \
            living in either poverty or near poverty. For example, the United \
            Way describes asset limited, income constrained, and employed (ALICE)\
            individuals as living from pay check to pay check, struggling to \
            afford necessities, and often one crisis away from poverty.")

# Map container
with st.container():
    # Draw map
    Wayne_values = df1["Wayne County, Michigan!!Estimate"][9]
    Macomb_values = df1["Wayne County, Michigan!!Estimate"][9]
    Oakland_values = df1["Oakland County, Michigan!!Estimate"][9]
    map_data = pd.DataFrame([[-83.3362, 42.2791, Wayne_values], [-82.8210, 42.7169, Macomb_values], [-83.3362, 42.5922, Oakland_values]], columns=["lng", "lat", "values"])

    layer = pdk.Layer(
        'ColumnLayer',
        data=map_data,
        get_position=["lng", "lat"],
        get_elevation=["values"],
        elevation_scale=500,
        radius=3000,
        get_fill_color=["values * 10", "values", "values * 10", 140],
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=42.3314,
        longitude=-83.0458,
        zoom=8,
        min_zoom=5,
        max_zoom=10,
        pitch=60,
        bearing=-3)

    tooltip = {
        "html": "<b>{values}</b> thousand household in this county have spend over 50% of their household income on gross rent.",
        "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
    }

    st.subheader('Households in Wayne, Macomb, and Oakland Counties whose gross rent exceeded 50% of household income in the last year')

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        layers=layer,
        initial_view_state=view_state,
        tooltip = tooltip))


# Plotly choropleth map
with st.container():
    from urllib.request import urlopen
    import json
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)