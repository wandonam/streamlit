# LIBRARY
import streamlit as st
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder
from matplotlib import font_manager, rc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from colors import Color
from feature import feature_engineering
from datetime import datetime, timedelta


##Dataframe
feature_engineering()
font_path = rf'..\data\font\Pretendard-SemiBold.ttf'
df_gross = pd.read_pickle(rf'..\data\raw\gross.pkl')


##FONT
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
    filtered_data_2024 = df_gross[(df_gross['date'] >= '2023-01-01') & (df_gross['date'] <= today)]

    #daily gross(sum)
    sales_per_date_2024 = filtered_data_2024.groupby('date')['sales'].sum().reset_index()

    #formatted_date: mm-dd (a)
    sales_per_date_2024['formatted_date'] = sales_per_date_2024['date'].dt.strftime('%y-%m-%d (%a)')

    end_date = sales_per_date_2024['date'].max()
    start_date = end_date - timedelta(days=7)


    st.write('##### Daily')
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

    fig.update_xaxes(range=[start_date, end_date])

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Sales',
        xaxis_tickformat='%Y-%m-%d (%a)',
        xaxis_tickangle=-45,
        height=600
    )

    st.plotly_chart(fig)




    filtered_data_2024['month'] = filtered_data_2024['date'].dt.to_period('M')
    sales_per_month_2024 = filtered_data_2024.groupby('month')['sales'].sum().reset_index()
    sales_per_month_2024['month'] = sales_per_month_2024['month'].dt.to_timestamp()

    sales_per_month_2024['formatted_month'] = sales_per_month_2024['month'].dt.strftime('%Y-%m')


    st.write('##### Monthly')

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sales_per_month_2024['month'], 
        y=sales_per_month_2024['sales'], 
        mode='lines+markers+text', 
        name='2024', 
        line=dict(color='blue'),
        fill='tozeroy',
        fillcolor='rgba(0, 0, 255, 0.3)',
        text=[f'{s/1e6:.1f}M' for s in sales_per_month_2024['sales']],
        textposition='top center'
    ))

    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Sales',
        xaxis_tickformat='%Y-%m',
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

    format_pivot = channel_pivot.map(format_number)

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

    channels = ['cafe24', 'growth', 'smartstore', 'wing', 'Other']
    selected_channels = st.multiselect('Select Channels', channels, default=channels)


    st.write('##### Daily')
    fig = go.Figure()

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

    fig.update_xaxes(range=[start_date, end_date])

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Sales',
        xaxis_tickformat='%m-%d (%a)',
        xaxis_tickangle=-45,
        height=600
    )

    st.plotly_chart(fig)

    df_gross['month'] = df_gross['date'].dt.to_period('M')
    monthly_pivot = pd.pivot_table(df_gross, values='sales', index=['month'], columns=['channel'], aggfunc='sum')
    monthly_pivot['Total'] = monthly_pivot.sum(axis=1)
    monthly_pivot = monthly_pivot[['cafe24', 'growth', 'smartstore', 'wing', 'Other', 'Total']]
    monthly_pivot = monthly_pivot.sort_index()
    monthly_pivot = monthly_pivot.fillna(0)
    monthly_pivot = monthly_pivot.astype(int)


    st.write('##### Monthly')
    fig_monthly = go.Figure()

    for channel in selected_channels:
        fig_monthly.add_trace(go.Scatter(
            x=monthly_pivot.index.to_timestamp(),
            y=monthly_pivot[channel],
            mode='lines+markers+text',
            name=channel,
            line=dict(color=ch_colors[channel]),
            text=[f'{s/1e6:.1f}M' for s in monthly_pivot[channel]],
            textposition='top center'
        ))


    fig_monthly.update_layout(
        xaxis_title='Month',
        yaxis_title='Sales',
        xaxis_tickformat='%Y-%m',  # x축 포맷 설정
        xaxis_tickangle=-45,
        height=600
    )

    st.plotly_chart(fig_monthly)

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

    all_product_data = df_gross[df_gross['product'].isin(filtered_products)]

    for product in filtered_products:
        product_data = all_product_data[all_product_data['product'] == product]
        product_sales_per_month = product_data.set_index('date').resample('M')['sales'].sum()
        
        line_fig.add_trace(go.Scatter(
            x=product_sales_per_month.index, 
            y=product_sales_per_month.values, 
            mode='lines+markers+text', 
            name=product,
            text=[f'{s/1e6:.1f}M' for s in product_sales_per_month],
            textposition='top center'
        ))

    # 꺾은선 그래프 초기화면을 선택된 기간으로 설정

    line_fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Sales',
        xaxis_tickformat='%Y-%m',  # x축 포맷 설정
        xaxis_tickangle=-45,
        height=600
    )

    st.plotly_chart(line_fig)

    # Cat으로 그룹화한 꺾은선 그래프 추가 (월별)
    st.write('##### Trend by Category')

    line_fig_cat = go.Figure()

    for cat in df_gross['cat'].unique():
        cat_data = df_gross[df_gross['cat'] == cat]
        cat_sales_per_month = cat_data.set_index('date').resample('M')['sales'].sum()
        
        line_fig_cat.add_trace(go.Scatter(
            x=cat_sales_per_month.index, 
            y=cat_sales_per_month.values, 
            mode='lines+markers+text', 
            name=cat,
            text=[f'{s/1e6:.1f}M' for s in cat_sales_per_month],
            textposition='top center'
        ))

    # 꺾은선 그래프 초기화면을 선택된 기간으로 설정

    line_fig_cat.update_layout(
        xaxis_title='Month',
        yaxis_title='Sales',
        xaxis_tickformat='%Y-%m',  # x축 포맷 설정
        xaxis_tickangle=-45,
        height=600
    )

    st.plotly_chart(line_fig_cat)

elif menu == 'Detailed':
    st.write('#### **Trend by Product**')
    st.write('##### Product')

    if 'selected_products' not in st.session_state:
        st.session_state.selected_products = list(df_gross['product'].unique())

    # 초기 세팅: 마지막 일의 해당 월의 1일
    initial_end_date = df_gross['date'].max()
    initial_start_date = initial_end_date - timedelta(days=7)

    date_range = st.date_input('SELECT DATE', (initial_start_date, initial_end_date))
    start_date, end_date = date_range

    # 선택한 날짜 범위 및 제품에 따라 데이터 필터링
    df_gross_filtered = df_gross[(df_gross['date'] >= pd.to_datetime(start_date)) & 
                                 (df_gross['date'] <= pd.to_datetime(end_date))]

    # 상품 목록
    products = df_gross_filtered['product'].unique()


    df_gross_filtered = df_gross_filtered[df_gross_filtered['product'].isin(st.session_state.selected_products)]


    total_sales_per_product = df_gross_filtered.groupby('product')['sales'].sum()

    # 기간 내 일수 계산
    num_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1
    
    average_daily_sales_per_product = total_sales_per_product / num_days
    filtered_products = average_daily_sales_per_product[average_daily_sales_per_product > 50000].index

    sales_per_product = total_sales_per_product[filtered_products]
    sales_per_product = sales_per_product.sort_values(ascending=False)


    channels = ['cafe24', 'growth', 'smartstore', 'wing']
    
    for channel in channels:
        st.write(f'##### Sales Trend for {channel.capitalize()}')

        channel_data = df_gross_filtered[df_gross_filtered['channel'] == channel]
        line_fig = go.Figure()

        all_product_data = channel_data[channel_data['product'].isin(filtered_products)]

        for product in filtered_products:
            product_data = all_product_data[all_product_data['product'] == product]
            product_sales_per_day = product_data.groupby('date')['sales'].sum().reindex(pd.date_range(all_product_data['date'].min(), all_product_data['date'].max(), freq='D'), fill_value=0)
            
            line_fig.add_trace(go.Scatter(
                x=product_sales_per_day.index, 
                y=product_sales_per_day.values, 
                mode='lines+markers+text', 
                name=product,
                text=[f'{s/1e6:.1f}M' for s in product_sales_per_day],
                textposition='top center'
            ))

        line_fig.update_xaxes(range=[start_date, end_date])

        line_fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Sales',
            xaxis_tickformat='%m-%d (%a)',
            xaxis_tickangle=-45,
            height=600
        )

        st.plotly_chart(line_fig)