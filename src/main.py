# LIBRARY
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
from st_aggrid import AgGrid, GridOptionsBuilder
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
import plotly.express as px
from  PIL import Image
import numpy as np
import pandas as pd
import io
import os
from colors import Color
from feature import feature_engineering
import base64


##Dataframe
feature_engineering()
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
file_path = os.path.join(parent_dir, 'data', 'processed', 'gross.pkl')
font_path = os.path.join(parent_dir, 'data', 'font', 'Pretendard-SemiBold.ttf')
df_gross = pd.read_pickle(file_path)

##FONT
def get_base64_encoded_font(font_path):
    with open(font_path, "rb") as font_file:
        encoded_string = base64.b64encode(font_file.read()).decode()
    return encoded_string

encoded_font = get_base64_encoded_font(font_path)

font_prop = FontProperties(fname=font_path)
rcParams['font.family'] = font_prop.get_name()

#STREAMLIT
with st.sidebar:
    menu = option_menu("BM", ["Total", "Channel", "Product", "Detailed"],
                         icons=['bi bi-1-square-fill', 'bi bi-2-square-fill', 'bi bi-3-square-fill', 'bi bi-4-square-fill'],
                         menu_icon="bi bi-activity", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": Color.WHITE},
        "icon": {"color": "black", "font-size": "16px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": Color.GRAY},
        "nav-link-selected": {"background-color": Color.SKYBLUE},
    }
    )

if menu == 'Total':
    st.write('#### **Total Sales**')



    # 초기 세팅: 마지막 일의 해당 월의 1일
    initial_end_date = df_gross['date'].max()
    initial_start_date = initial_end_date.replace(day=1)

    date_range = st.date_input('SELECT', (initial_start_date, initial_end_date))
    start_date, end_date = date_range

    # 선택한 날짜 범위에 따라 데이터 필터링
    filtered_data = df_gross[(df_gross['date'] >= pd.to_datetime(start_date)) & (df_gross['date'] <= pd.to_datetime(end_date))]

    # 날짜별 매출 합계 계산
    sales_per_date = filtered_data.groupby('date')['sales'].sum().reset_index()

    # 날짜 형식을 "MM-DD"로 변경
    sales_per_date['formatted_date'] = sales_per_date['date'].dt.strftime('%m-%d (%a)')

    # 그래프 유형 선택 드롭다운 메뉴
    graph_type = st.selectbox('Select Graph Type', ['Line Plot', 'Bar Plot'])

    plt.figure(figsize=(14, 8))

    if graph_type == 'Line Plot':
        plt.plot(sales_per_date.index, sales_per_date['sales'], marker='o', label='SELECT Period', color='#ff0000')
    elif graph_type == 'Bar Plot':
        plt.bar(sales_per_date.index, sales_per_date['sales'], label='SELECT Period', color='#ff0000')

    plt.xlabel('DATE')
    plt.ylabel('SALES')
    plt.title('Sales by Date ')
    plt.grid(True)

    # x축 레이블을 "MM-DD" 형식으로 설정
    plt.xticks(ticks=sales_per_date.index, labels=sales_per_date['formatted_date'], rotation=45)

    # 백만 단위로 값 표시
    for i, row in sales_per_date.iterrows():
        plt.text(i, row['sales'], f'{row["sales"]/1e6:.1f}M', fontsize=12, ha='center', va='bottom')

    # 비교 기간 추가 체크박스
    compare = st.checkbox('ADD Period')

    if compare:
        compare_start_date = st.date_input('COMPARE', initial_start_date, key='compare_start_date')
        compare_end_date = compare_start_date + (end_date - start_date)
        
        st.write(f"COMPARE Period: {compare_start_date.strftime('%Y-%m-%d')} to {compare_end_date.strftime('%Y-%m-%d')}")

        compare_filtered_data = df_gross[(df_gross['date'] >= pd.to_datetime(compare_start_date)) & (df_gross['date'] <= pd.to_datetime(compare_end_date))]
        compare_sales_per_date = compare_filtered_data.groupby('date')['sales'].sum().reset_index()

        # 비교 기간 데이터의 길이를 선택한 기간 데이터의 길이와 맞추기
        compare_sales_per_date = compare_sales_per_date.iloc[:len(sales_per_date)].copy()

        # 인덱스를 동일하게 맞추기
        compare_sales_per_date.index = sales_per_date.index

        # 비교 기간의 날짜 형식을 "MM-DD"로 변경
        compare_sales_per_date['formatted_date'] = compare_sales_per_date['date'].dt.strftime('%m-%d (%a)')

        # 비교 기간 매출 그래프 추가
        if graph_type == 'Line Plot':
            plt.plot(compare_sales_per_date.index, compare_sales_per_date['sales'], marker='o', linestyle='--', label='COMPARE Period', color='#0092ff')
        elif graph_type == 'Bar Plot':
            plt.bar(compare_sales_per_date.index, compare_sales_per_date['sales'], label='COMPARE Period', color='#0092ff')

        # 백만 단위로 값 표시
        for i, row in compare_sales_per_date.iterrows():
            plt.text(i, row['sales'], f'{row["sales"]/1e6:.1f}M', fontsize=12, ha='center', va='bottom')

    plt.legend()
    st.pyplot(plt)

elif menu == 'Channel':
    st.write('#### **Trend by Channel**')
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


    st.write('##### Vizualization')
    # 채널 리스트
    channels = df_gross['channel'].unique()
    selected_channels = st.multiselect('SELECT CHANNELS', channels, default=channels)

    # 초기 세팅: 마지막 일의 해당 월의 1일
    initial_end_date = df_gross['date'].max()
    initial_start_date = initial_end_date.replace(day=1)

    date_range = st.date_input('SELECT', (initial_start_date, initial_end_date))
    start_date, end_date = date_range

    # 선택한 날짜 범위 및 채널에 따라 데이터 필터링
    filtered_data = df_gross[(df_gross['date'] >= pd.to_datetime(start_date)) & 
                             (df_gross['date'] <= pd.to_datetime(end_date)) & 
                             (df_gross['channel'].isin(selected_channels))]

    # 날짜 및 채널별 매출 합계 계산
    sales_per_date_channel = filtered_data.groupby(['date', 'channel'])['sales'].sum().unstack().fillna(0)

    # 날짜 형식을 "MM-DD"로 변경
    sales_per_date_channel.index = sales_per_date_channel.index.strftime('%m-%d (%a)')

    # 매출 그래프 그리기
    plt.figure(figsize=(14, 8))

    for channel in selected_channels:
        plt.plot(sales_per_date_channel.index, sales_per_date_channel[channel], marker='o', label=channel)

    plt.xlabel('DATE')
    plt.ylabel('SALES')
    plt.title('Sales by Date for Selected Channels')
    plt.grid(True)

    # x축 레이블을 "MM-DD" 형식으로 설정
    plt.xticks(rotation=45)

    # 백만 단위로 값 표시
    for channel in selected_channels:
        for i, sales in enumerate(sales_per_date_channel[channel]):
            if sales > 0:
                plt.text(i, sales, f'{sales/1e6:.1f}M', fontsize=8, ha='center', va='bottom')

    # 비교 기간 추가 체크박스
    compare = st.checkbox('ADD Period')

    if compare:
        compare_start_date = st.date_input('COMPARE', initial_start_date, key='compare_start_date')
        compare_end_date = compare_start_date + (end_date - start_date)

        st.write(f"COMPARE Period: {compare_start_date.strftime('%Y-%m-%d')} to {compare_end_date.strftime('%Y-%m-%d')}")

        compare_filtered_data = df_gross[(df_gross['date'] >= pd.to_datetime(compare_start_date)) & 
                                         (df_gross['date'] <= pd.to_datetime(compare_end_date)) & 
                                         (df_gross['channel'].isin(selected_channels))]

        compare_sales_per_date_channel = compare_filtered_data.groupby(['date', 'channel'])['sales'].sum().unstack().fillna(0)

        # 비교 기간 데이터의 길이를 선택한 기간 데이터의 길이와 맞추기
        compare_sales_per_date_channel = compare_sales_per_date_channel.iloc[:len(sales_per_date_channel)].copy()

        # 인덱스를 동일하게 맞추기
        compare_sales_per_date_channel.index = sales_per_date_channel.index

        # 비교 기간의 날짜 형식을 "MM-DD"로 변경
        # compare_sales_per_date_channel.index = compare_sales_per_date_channel.index.strftime('%m-%d')

        # 비교 기간 매출 그래프 추가
        for channel in selected_channels:
            plt.plot(compare_sales_per_date_channel.index, compare_sales_per_date_channel[channel], marker='o', linestyle='--', label=f'{channel} (Compare)')

        # 백만 단위로 값 표시
        for channel in selected_channels:
            for i, sales in enumerate(compare_sales_per_date_channel[channel]):
                if sales > 0:
                    plt.text(i, sales, f'{sales/1e6:.1f}M', fontsize=8, ha='center', va='bottom')

    plt.legend()
    st.pyplot(plt)

elif menu == 'Product':
    st.write('#### **Trend by Product**')
    st.write('##### Product')

    if 'selected_products' not in st.session_state:
        st.session_state.selected_products = list(df_gross['product'].unique())

    # 초기 세팅: 마지막 일의 해당 월의 1일
    initial_end_date = df_gross['date'].max()
    initial_start_date = initial_end_date.replace(day=1)

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
    filtered_products = average_daily_sales_per_product[average_daily_sales_per_product > 100000].index


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
    sales_per_product = sales_per_product[average_daily_sales_per_product[average_daily_sales_per_product > 100000].index]
    sales_per_product = sales_per_product.sort_values(ascending=False)

    plt.figure(figsize=(14, 8))
    bars = sales_per_product.plot(kind='bar', color=plt.cm.Paired(range(len(sales_per_product))))

    plt.xlabel('Product')
    plt.ylabel('Sales')
    plt.title('Sales by Product')
    plt.grid(True)

    plt.xticks(rotation=45)

    for i, sales in enumerate(sales_per_product):
        plt.text(i, sales, f'{sales/1e6:.1f}M', fontsize=12, ha='center', va='bottom')
    
    st.pyplot(plt)

    st.write('##### Option')
    selected_product = st.selectbox('SELECT PRODUCT', sales_per_product.index)
    if selected_product:
        product_data = filtered_data[filtered_data['product'] == selected_product]
        option_distribution = product_data['option'].value_counts(normalize=True) * 100

    if selected_product:
        product_data = filtered_data[filtered_data['product'] == selected_product]
        option_sales_distribution = product_data.groupby('option')['sales'].sum()
        option_sales_percentage = (option_sales_distribution / option_sales_distribution.sum()) * 100

    plt.figure(figsize=(14, 14))
    plt.pie(option_distribution, labels=option_distribution.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired(range(len(option_distribution))))
    plt.title(f'Sales by Option: {selected_product}')
    st.pyplot(plt)

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
