# LIBRARY
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
from st_aggrid import AgGrid, GridOptionsBuilder
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
from matplotlib import font_manager, rc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from  PIL import Image
import numpy as np
import pandas as pd
import io
import os
from colors import Color
from feature import feature_engineering
import base64
from datetime import datetime, timedelta


##Dataframe
feature_engineering()
font_path = os.path.join(rf'..\data\font\Pretendard-SemiBold.ttf')
df_gross = pd.read_pickle(rf'..\data\processed\gross.pkl')


##FONT
def get_base64_encoded_font(font_path):
    with open(font_path, "rb") as font_file:
        encoded_string = base64.b64encode(font_file.read()).decode()
    return encoded_string

encoded_font = get_base64_encoded_font(font_path)

font_name = font_manager.FontProperties(fname=font_path).get_name()
font_manager.fontManager.addfont(font_path)
rc('font', family=font_name)


#STREAMLIT
with st.sidebar:
    menu = option_menu("BM", ["Total", "Channel", "Product", "Detailed"],
                         icons=['bi bi-1-square-fill', 'bi bi-2-square-fill', 'bi bi-3-square-fill', 'bi bi-4-square-fill'],
                         menu_icon="bi bi-activity", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": Color.BLACK},
        "icon": {"color": "white", "font-size": "20px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": Color.R_BLACK},
        "nav-link-selected": {"background-color": Color.R_BLACK},
    }
    )

if menu == 'Total':
    st.write('#### **Sales by Date**')

    #date
    today = datetime.today()

    #filtered period: 2024. 01. 01
    filtered_data_2024 = df_gross[(df_gross['date'] >= '2024-01-01') & (df_gross['date'] <= today)]

    #daily gross(sum)
    sales_per_date_2024 = filtered_data_2024.groupby('date')['sales'].sum().reset_index()

    #formatted_date: mm-dd (a)
    sales_per_date_2024['formatted_date'] = sales_per_date_2024['date'].dt.strftime('%m-%d (%a)')

    end_date = sales_per_date_2024['date'].max()
    start_date = end_date - timedelta(days=7)

    date_range = st.date_input('SELECT DATE', (start_date, end_date))
    start_date, end_date = date_range

    # Plotly 그래프 생성
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sales_per_date_2024['date'], 
        y=sales_per_date_2024['sales'], 
        mode='lines+markers+text', 
        name='2024', 
        line=dict(color='blue'),
        fill='tozeroy',
        fillcolor='rgba(0, 0, 255, 0.3)',
        text=[f'{s/1e6:.1f}M' for s in sales_per_date_2024['sales']],
        textposition='top center'
    ))

    # x축 범위 설정: 사용자 선택에 따른 기간
    fig.update_xaxes(range=[start_date, end_date])

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Sales',
        xaxis_tickformat='%m-%d (%a)',  # x축 포맷 설정
        xaxis_tickangle=-45,
        height=600
    )

    st.plotly_chart(fig)

elif menu == 'Channel':
    st.write('#### **Sales by Channel**')

    st.write('##### Dataframe')
    channel_pivot = pd.pivot_table(df_gross, values='sales', index=['date'], columns=['channel'], aggfunc='sum')
    channel_pivot['Total'] = channel_pivot.sum(axis=1)
    channel_pivot = channel_pivot[['cafe24', 'growth', 'smartstore', 'wing', 'Other', 'Total']]
    channel_pivot = channel_pivot.sort_index(ascending=False)
    channel_pivot = channel_pivot.fillna(0)
    channel_pivot = channel_pivot.astype(int)
    channel_pivot.index = pd.to_datetime(channel_pivot.index).strftime('%y-%m-%d (%a)')

    def format_number(value):
        return f"{value:,}"

    format_pivot = channel_pivot.applymap(format_number)

    gb = GridOptionsBuilder.from_dataframe(format_pivot.reset_index())
    gb.configure_default_column(filterable=True, sortable=True)
    gb.configure_pagination(paginationAutoPageSize=True)
    gridOptions = gb.build()

    aggrid_response = AgGrid(
        format_pivot.reset_index(),
        gridOptions=gridOptions,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=True,
        update_mode='MODEL_CHANGED')
    
    df_gross['date'] = pd.to_datetime(df_gross['date'])
    channel_pivot2 = pd.pivot_table(df_gross, values='sales', index=['date'], columns=['channel'], aggfunc='sum')
    channel_pivot2['Total'] = channel_pivot2.sum(axis=1)
    channel_pivot2 = channel_pivot2[['cafe24', 'growth', 'smartstore', 'wing', 'Other', 'Total']]
    channel_pivot2 = channel_pivot2.sort_index()
    channel_pivot2 = channel_pivot2.fillna(0)
    channel_pivot2 = channel_pivot2.astype(int)

    # 채널 선택
    channels = ['cafe24', 'growth', 'smartstore', 'wing', 'Other']
    selected_channels = st.multiselect('Select Channels', channels, default=channels)

    fig = go.Figure()

    # 초기 화면을 마지막 날짜로부터 7일간 설정
    end_date = channel_pivot2.index.max()
    start_date = end_date - timedelta(days=7)

    date_range = st.date_input('SELECT DATE', (start_date, end_date))
    start_date, end_date = date_range

    ch_colors = {
        'cafe24': Color.CF24,
        'growth': Color.BROWN,
        'smartstore': Color.SS,
        'wing': Color.CP,
        'Other': Color.ETC
    }

    for channel in selected_channels:
        fig.add_trace(go.Scatter(
            x=channel_pivot2.index,
            y=channel_pivot2[channel],
            mode='lines+markers+text',
            name=channel,
            line=dict(color=ch_colors[channel]),
            text=[f'{s/1e6:.1f}M' for s in channel_pivot2[channel]],
            textposition='top center'
        ))

    # x축 범위 설정: 사용자 선택에 따른 기간
    fig.update_xaxes(range=[start_date, end_date])

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Sales',
        xaxis_tickformat='%m-%d (%a)',  # x축 포맷 설정
        xaxis_tickangle=-45,
        height=600
    )

    st.plotly_chart(fig)

elif menu == 'Product':
    st.write('#### **Trend by Product**')
    st.write('##### Product')

    if 'selected_products' not in st.session_state:
        st.session_state.selected_products = list(df_gross['product'].unique())

    # 초기 세팅: 마지막 일의 해당 월의 1일
    initial_end_date = df_gross['date'].max()
    initial_start_date = initial_end_date - timedelta(days=7)

    date_range = st.date_input('SELECT DATE', (initial_start_date, initial_end_date))
    start_date, end_date = date_range

    # 상품 목록
    products = df_gross['product'].unique()

    # 선택한 날짜 범위 및 제품에 따라 데이터 필터링
    filtered_data = df_gross[(df_gross['date'] >= pd.to_datetime(start_date)) & 
                             (df_gross['date'] <= pd.to_datetime(end_date)) & 
                             (df_gross['product'].isin(st.session_state.selected_products))]

    # 날짜 및 제품별 매출 합계 계산
    total_sales_per_product = filtered_data.groupby('product')['sales'].sum()

    # 기간 내 일수 계산
    num_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1
    
    average_daily_sales_per_product = total_sales_per_product / num_days
    filtered_products = average_daily_sales_per_product[average_daily_sales_per_product > 30000].index


    sales_per_product = total_sales_per_product[filtered_products]
    sales_per_product = sales_per_product.sort_values(ascending=False)

    selected_products = [p for p in st.session_state.selected_products if p in sales_per_product.index]
    updated_selected_products = st.multiselect('SELECT PRODUCT', products, default=selected_products)
    st.session_state.selected_products = updated_selected_products

    # 필터링된 데이터를 다시 계산
    filtered_data = df_gross[(df_gross['date'] >= pd.to_datetime(start_date)) & 
                             (df_gross['date'] <= pd.to_datetime(end_date)) & 
                             (df_gross['product'].isin(st.session_state.selected_products))]

    # 다시 계산된 데이터를 사용하여 매출 합계 재계산
    sales_per_product = filtered_data.groupby('product')['sales'].sum()
    sales_per_product = sales_per_product[average_daily_sales_per_product[average_daily_sales_per_product > 30000].index]
    sales_per_product = sales_per_product.sort_values(ascending=False)

    bar_fig = px.bar(
        x=sales_per_product.index, 
        y=sales_per_product.values,
        labels={'x': 'Product', 'y': 'Sales'},
        title='Sales by Product',
        color=sales_per_product.index
    )

    bar_fig.update_layout(
        xaxis_title='Product', 
        yaxis_title='Sales', 
        title='Sales by Product',
        xaxis_tickangle=-45,
        height=600,
        width=1200
    )
    bar_fig.update_traces(texttemplate='%{y:.2s}', textposition='outside')

    st.plotly_chart(bar_fig)

    # Plotly로 꺾은선 그래프 그리기
    line_fig = go.Figure()

    for product in filtered_products:
        product_data = filtered_data[filtered_data['product'] == product]
        product_sales_per_day = product_data.groupby('date')['sales'].sum().reindex(pd.date_range(start_date, end_date, freq='D'), fill_value=0)
        
        line_fig.add_trace(go.Scatter(
            x=product_sales_per_day.index, 
            y=product_sales_per_day.values, 
            mode='lines+markers+text', 
            name=product,
            text=[f'{s/1e6:.1f}M' for s in product_sales_per_day],
            textposition='top center'
        ))

    line_fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Sales',
        xaxis_tickangle=-45,
        height=600
    )

    st.plotly_chart(line_fig)

elif menu == 'Detailed':
    st.write('#### **Detailed by Channel**')

    # 초기 세팅: 마지막 일의 해당 월의 1일
    initial_end_date = df_gross['date'].max()
    initial_start_date = initial_end_date.replace(day=1)

    date_range = st.date_input('SELECT DATE', (initial_start_date, initial_end_date))
    start_date, end_date = date_range

    channels = df_gross['channel'].unique()
    selected_channels = st.selectbox('SELECT CHANNEL', channels, index=0)

    # 선택한 날짜 범위 및 채널에 따라 데이터 필터링
    filtered_data = df_gross[(df_gross['date'] >= pd.to_datetime(start_date)) &
                             (df_gross['date'] <= pd.to_datetime(end_date)) &
                             (df_gross['channel'] == selected_channels)]

    # 날짜 및 제품별 매출 합계 계산
    total_sales_per_product = filtered_data.groupby('product')['sales'].sum()

    # 기간 내 일수 계산
    num_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1
    
    # 평균 일일 매출 계산
    average_daily_sales_per_product = total_sales_per_product / num_days

    # 평균 일일 매출이 50,000 이상인 제품 필터링
    filtered_products = average_daily_sales_per_product[average_daily_sales_per_product > 50000].index

    # 총 매출이 50,000 이상인 제품 필터링
    sales_per_product = total_sales_per_product.loc[filtered_products]
    sales_per_product = sales_per_product.sort_values(ascending=False)

    plt.figure(figsize=(14, 8))
    bars = sales_per_product.plot(kind='bar', color=plt.cm.Paired(range(len(sales_per_product))))
    
    plt.xlabel('Product')
    plt.ylabel('Total Sales')
    plt.title(f'Detailed by {selected_channels}')
    plt.grid(True)

    plt.xticks(rotation=45)
    
    for i, sales in enumerate(sales_per_product):
        plt.text(i, sales, f'{sales/1e6:.1f}M', fontsize=12, ha='center', va='bottom')
    
    st.pyplot(plt)
