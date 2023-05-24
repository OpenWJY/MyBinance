# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : main.py
# Time       ：2023/4/6 13:23
# Author     ：author yjw
# version    ：python 3.10
# Description：
"""
import configparser
import binance.spot as spot
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# 读取配置
config = configparser.ConfigParser()
config.read('config.ini')

# 创建客户端
client = spot.Spot(api_key=config['BINANCE']['ApiKey'], api_secret=config['BINANCE']['Secret'])

with st.sidebar:
    # 获取交易对信息
    exchange_info_df = client.exchange_info()
    # 转换为DataFrame
    exchange_info_df = pd.DataFrame(exchange_info_df['symbols'])
    # 选取交易对
    symbol_select = st.selectbox('选择交易对', options=exchange_info_df['symbol'])


my_trades_info_df = pd.DataFrame(client.my_trades(symbol=symbol_select))

# 数据判空
if my_trades_info_df.empty:
    st.error('没有交易记录')
    st.stop()

# 将price转换为浮点数
my_trades_info_df['price'] = my_trades_info_df['price'].astype(float)
my_trades_info_df['qty'] = my_trades_info_df['qty'].astype(float)

# 绘制交易金额图表
fig = go.Figure()
symbol_select_df = exchange_info_df[exchange_info_df['symbol'] == symbol_select]
quoteAsset = symbol_select_df['quoteAsset'].values[0]
fig.update_layout(title=symbol_select + ' 交易图谱', xaxis_title='交易序号', yaxis_title='单价(' + quoteAsset + ')')

# 添加买入和卖出标记
buy_data = my_trades_info_df[my_trades_info_df['isBuyer']]
sell_data = my_trades_info_df[~my_trades_info_df['isBuyer']]
fig.add_trace(go.Scatter(x=buy_data.index, y=buy_data['price'], mode='markers', name='买入',
                         marker=dict(color='green', symbol='triangle-up')))
fig.add_trace(go.Scatter(x=sell_data.index, y=sell_data['price'], mode='markers', name='卖出',
                         marker=dict(color='red', symbol='triangle-down')))

# 计算买入价格的加权平均值
buy_avg = []
cumulative_qty = 0.0
cumulative_weighted_price = 0.0
for _, row in buy_data.iterrows():
    cumulative_qty += row['qty']
    cumulative_weighted_price += row['price'] * row['qty']
    avg_price = cumulative_weighted_price / cumulative_qty
    buy_avg.append(avg_price)
fig.add_trace(
    go.Scatter(x=buy_data.index, y=buy_avg, mode='lines', name='买入均线', line=dict(color='blue', dash='dash')))

# 设置鼠标悬停信息
hover_text = []
for _, row in my_trades_info_df.iterrows():
    text = f"订单ID: {row['orderId']}<br>"
    text += f"价格: {row['price']}<br>"
    text += f"数量: {row['qty']}<br>"
    text += f"金额: {row['quoteQty']}<br>"
    hover_text.append(text)
fig.update_traces(hovertext=hover_text, hoverinfo='text')

# 使用Streamlit显示图表
st.plotly_chart(fig)

# 交易明细
trades_summary = my_trades_info_df[['price', 'qty', 'quoteQty', 'time', 'isBuyer']]
trades_summary['isBuyer'] = trades_summary['isBuyer'].map({True: '买入', False: '卖出'})
trades_summary['time'] = pd.to_datetime(trades_summary['time'], unit='ms')
trades_summary['time'] = trades_summary['time'].dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
trades_summary_rename = trades_summary.rename(columns={'price': '单价(' + quoteAsset + ')', 'qty': '数量（个）', 'quoteQty': '消耗(' + quoteAsset + ')', 'time': '时间', 'isBuyer': '类型'})
st.table(trades_summary_rename)
