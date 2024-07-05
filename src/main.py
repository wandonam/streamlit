# LIBRARY
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from  PIL import Image
import numpy as np
import pandas as pd
import io
import os
import font
from colors import Color
from feature import feature_engineering

##FONT
font_name = "Pretendard-SemiBold"
font.set_font(font_name)

##Dataframe
feature_engineering()
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
file_path = os.path.join(parent_dir, 'data', 'processed', 'gross.pkl')
df_gross = pd.read_pickle(file_path)

#STREAMLIT
with st.sidebar:
    menu = option_menu("BM", ["Total Sales", "Trend by Channel", "Trend by Product", "Detailed by Channel"],
                         icons=['bi bi-1-square-fill', 'bi bi-2-square-fill', 'bi bi-3-square-fill', 'bi bi-4-square-fill'],
                         menu_icon="bi bi-activity", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": Color.WHITE},
        "icon": {"color": "black", "font-size": "16px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": Color.GRAY},
        "nav-link-selected": {"background-color": Color.SKYBLUE},
    }
    )

if menu == 'Total Sales':
    st.title('Total Sales')

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
    sales_per_date['formatted_date'] = sales_per_date['date'].dt.strftime('%m-%d')

    # 그래프 유형 선택 드롭다운 메뉴
    graph_type = st.selectbox('Select Graph Type', ['Line Plot', 'Bar Plot'])

    plt.figure(figsize=(18, 14))

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
        compare_sales_per_date['formatted_date'] = compare_sales_per_date['date'].dt.strftime('%m-%d')

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



elif menu == 'Trend by Channel':
    st.title('Trend by Channel')

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
    sales_per_date_channel.index = sales_per_date_channel.index.strftime('%m-%d')

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