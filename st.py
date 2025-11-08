import streamlit as st
import pandas as pd
import plotly.express as px
import plutora as p
import streamlit_extras.chart_container as scc

tecrs = p.Get_TECRs("2025-06-01", "2025-12-01")
releases = p.Get_Releases("2024-01-01", "2024-12-31")
tab1, tab2, tab3 = st.tabs(["Releases", "TECRs Chart", "Tecrs edit Data Grid"])
st.set_page_config(page_title="TECR Dashboard", layout="wide")
with tab1:
    data1 = releases
    # Ensure Start Date is datetime
    data1['implementationDate'] = pd.to_datetime(data1['implementationDate'], errors='coerce')

    # Create a month-period column for sorting
    data1['MonthPeriod'] = data1['implementationDate'].dt.to_period('M')

    # Create a readable month label
    data1['Month'] = data1['MonthPeriod'].dt.strftime('%b %Y')

    # Group by MonthPeriod and TECR Status (to preserve order)
    monthly_status_counts = (
        data1.groupby(['MonthPeriod', 'Month', 'Release State'])
        .size()
        .reset_index(name='Count')
        .sort_values('MonthPeriod')  # ensures chronological order
    )

    # Plot
    fig1 = px.bar(
        monthly_status_counts,
        x='Month',
        y='Count',
        color='Release State',
        title='Releases per month by Status',
        labels={'Month': 'Month', 'Count': 'Number of Releases', 'Release Status': 'Status'},
        text='Count'
    )

    # Format layout
    fig1.update_layout(
        barmode='stack',
        xaxis={'categoryorder': 'array', 'categoryarray': monthly_status_counts['Month'].unique()},
        template='plotly_white'
    )

    with scc.chart_container(monthly_status_counts):
        st.plotly_chart(fig1, use_container_width=True)

    st.dataframe(releases)

with tab2:
    data = tecrs
    # Ensure Start Date is datetime
    data['Start Date'] = pd.to_datetime(data['Start Date'], errors='coerce')

    # Create a month-period column for sorting
    data['MonthPeriod'] = data['Start Date'].dt.to_period('M')

    # Create a readable month label
    data['Month'] = data['MonthPeriod'].dt.strftime('%b %Y')

    # Group by MonthPeriod and TECR Status (to preserve order)
    monthly_status_counts = (
        data.groupby(['MonthPeriod', 'Month', 'TECR Status'])
        .size()
        .reset_index(name='Count')
        .sort_values('MonthPeriod')  # ensures chronological order
    )

    # Plot
    fig = px.bar(
        monthly_status_counts,
        x='Month',
        y='Count',
        color='TECR Status',
        title='TECRs per month by Status',
        labels={'Month': 'Month', 'Count': 'Number of TECRs', 'TECR Status': 'Status'},
        text='Count'
    )

    # Format layout
    fig.update_layout(
        barmode='stack',
        xaxis={'categoryorder': 'array', 'categoryarray': monthly_status_counts['Month'].unique()},
        template='plotly_white'
    )

    with scc.chart_container(monthly_status_counts):
        st.plotly_chart(fig, use_container_width=True)

with tab3:

    edit_df = st.data_editor(tecrs, num_rows="dynamic",height=1200)
