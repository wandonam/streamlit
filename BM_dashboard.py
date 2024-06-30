# SET UP
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from  PIL import Image
import numpy as np
import pandas as pd
import io

# FONT
font_path = r'C:\Users\dohoo\AppData\Local\Microsoft\Windows\Fonts\NotoSansKR-Bold.ttf'
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

# COLOR
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=[
    '#FFB5E8', '#B28DFF', '#AFF8DB', '#FFABAB', '#FFC3A0', '#FFFFD1',
    '#FF9CEE', '#BFFCC6', '#CFCFCF', '#97A2FF'
])

# FEATURE
df_original = pd.read_excel(r'C:\Users\dohoo\Desktop\JUPYTER\workspace\gross\raw_2024.xlsx')

df_gross = pd.DataFrame()

## Datetime
df_gross['date'] = df_original['결제일']
df_gross['year'] = df_original['결제일'].dt.year
df_gross['month'] = df_original['결제일'].dt.month
df_gross['day'] = df_original['결제일'].dt.day

weekday_map = {0: '월', 1: '화', 2: '수', 3: '목', 4: '금', 5: '토', 6: '일'}
df_gross['weekday'] = df_original['결제일'].dt.weekday.map(weekday_map)

df_gross['hour'] = df_original['출고일'].dt.hour

def convert_hour_to_text(hour):
    if hour == 0:
        return 'Other'
    elif 1 <= hour < 6:
        return 'Dawn'
    elif 6 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 18:
        return 'Afternoon'
    elif 18 <= hour < 24:
        return 'Evening'
    else:
        return 'Other'

df_gross['hour'] = df_gross['hour'].apply(convert_hour_to_text)

## Channel

df_gross['channel'] = df_original['매출처']

def change_sales_channel(value):
    mapping = {
        '쿠팡윙': 'wing',
        '로켓그로스': 'growth',
        '스마트스토어': 'smartstore',
        '자사몰': 'cafe24'
    }
    return mapping.get(value, 'Other')

df_gross['channel'] = df_gross['channel'].apply(change_sales_channel)

## Product
df_gross['product'] = df_original['상품명']
df_original['옵션명'] = df_original['옵션명'].replace('기타', '1')
df_original['입수량'] = df_original['옵션명'].str.replace('BOX', '').astype(int)
df_gross['option'] = df_original['옵션명']

## Sales
df_gross['quantity'] = df_original['수량'].fillna(0)
df_gross['quantity'] = df_gross['quantity'].astype(int)
df_gross['sales'] = df_original['총\n결제가'].astype(int)


#STREAMLIT
with st.sidebar:
    menu = option_menu("BM", ["Total Sales", "Trend by Channel", "Trend by Product", "Detailed by Channel"],
                         icons=['bi bi-1-square-fill', 'bi bi-2-square-fill', 'bi bi-3-square-fill', 'bi bi-4-square-fill'],
                         menu_icon="bi bi-activity", default_index=0,
                         styles={
                         # default_index = 처음에 보여줄 페이지 인덱스 번호
        "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": {"color": "black", "font-size": "16px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#d3d3d3"},
        "nav-link-selected": {"background-color": "#b3e5fc"},
    } # css 설정
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

    # 매출 그래프 그리기
    plt.figure(figsize=(14, 8))
    plt.plot(sales_per_date.index, sales_per_date['sales'], marker='o', label='SELECT Period', color='#ff0000')
    plt.xlabel('DATE')
    plt.ylabel('SALES')
    plt.title('Sales by Date ')
    plt.grid(True)

    # x축 레이블을 "MM-DD" 형식으로 설정
    plt.xticks(ticks=sales_per_date.index, labels=sales_per_date['formatted_date'], rotation=45)

    # 백만 단위로 값 표시
    for i, row in sales_per_date.iterrows():
        plt.text(i, row['sales'], f'{row["sales"]/1e6:.1f}M', fontsize=8, ha='center', va='bottom')

    # 비교 기간 추가 체크박스
    compare = st.checkbox('ADD Period')

    if compare:
        compare_start_date = st.date_input('COMPARE', initial_start_date, key='compare_start_date')
        compare_end_date = compare_start_date + (end_date - start_date)
        
        st.write(f"COMEPARE Period: {compare_start_date.strftime('%Y-%m-%d')} to {compare_end_date.strftime('%Y-%m-%d')}")

        compare_filtered_data = df_gross[(df_gross['date'] >= pd.to_datetime(compare_start_date)) & (df_gross['date'] <= pd.to_datetime(compare_end_date))]
        compare_sales_per_date = compare_filtered_data.groupby('date')['sales'].sum().reset_index()

        # 비교 기간 데이터의 길이를 선택한 기간 데이터의 길이와 맞추기
        compare_sales_per_date = compare_sales_per_date.iloc[:len(sales_per_date)].copy()

        # 인덱스를 동일하게 맞추기
        compare_sales_per_date.index = sales_per_date.index

        # 비교 기간의 날짜 형식을 "MM-DD"로 변경
        compare_sales_per_date['formatted_date'] = compare_sales_per_date['date'].dt.strftime('%m-%d')

        # 비교 기간 매출 그래프 추가
        plt.plot(compare_sales_per_date.index, compare_sales_per_date['sales'], marker='o', linestyle='--', label='COMEPARE Period', color='#0092ff')

        # 백만 단위로 값 표시
        for i, row in compare_sales_per_date.iterrows():
            plt.text(i, row['sales'], f'{row["sales"]/1e6:.1f}M', fontsize=8, ha='center', va='bottom')

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