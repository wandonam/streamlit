##### Library
import os
import pandas as pd



def feature_engineering():
    ##### Load data
    df_original = pd.read_excel(rf'..\data\raw\raw_2024.xlsx')




    ##### Feature Engineering
    df_gross = pd.DataFrame()


    ## Datetime
    df_gross['date'] = df_original['결제일']
    df_gross['year'] = df_original['결제일'].dt.year
    df_gross['month'] = df_original['결제일'].dt.month
    df_gross['day'] = df_original['결제일'].dt.day

    weekday_map = {0: '월', 1: '화', 2: '수', 3: '목', 4: '금', 5: '토', 6: '일'}
    df_gross['weekday'] = df_original['결제일'].dt.weekday.map(weekday_map)

    df_gross['hour'] = df_original['출고일'].dt.hour


    ### Define Time
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

    df_gross['time'] = df_gross['hour'].apply(convert_hour_to_text)


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
    df_original['옵션명'] = df_original['옵션명'].replace('기타', '1BOX')
    df_gross['option'] = df_original['옵션명']


    ## Sales
    df_gross['quantity'] = df_original['수량'].fillna(0)
    df_gross['quantity'] = df_gross['quantity'].astype(int)
    df_gross['sales'] = df_original['총\n결제가'].astype(int)


    ## Save
    df_gross.to_pickle('..\data\processed\gross.pkl')