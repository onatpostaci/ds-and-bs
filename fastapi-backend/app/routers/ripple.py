from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from typing import Optional
from pydantic import BaseModel
import requests
import os
import json
import numpy as np
import io
from fastapi import HTTPException
from datetime import datetime, timedelta
import pandas as pd

"Router provider to modularize the routers. This router will only be for Audio Routes"
router = APIRouter()

# Assuming the CSV file has no header, we define the column names based on the README file
column_names = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 
                'Close time', 'Quote asset volume', 'Number of trades', 
                'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']


df = pd.read_csv(r"C:\Users\onat.postaci\Desktop\Projects\ds-and-bs\fastapi-backend\app\routers\Merged_CSV.csv", names=column_names)

@router.get("/data-summary")
async def data_summary():
    local_df = df.copy()
    summary = local_df.describe().replace({np.nan: None}).to_dict()
    summary_list = [{**{'statistic': key}, **value} for key, value in summary.items()]
    summary_list.append({'statistic': 'count', 'value': len(local_df)})
    return summary_list

@router.post("/clean-data")
async def clean_data():
    local_df = df.copy()
    cleaned_df = local_df.drop_duplicates().dropna()
    return {"original_count": len(local_df), "cleaned_count": len(cleaned_df)}



@router.get("/monthly-statistics")
async def monthly_statistics():
    local_df = df.copy()
    local_df['Month'] = pd.to_datetime(local_df['Open time'], unit='ms').dt.month
    return local_df.groupby('Month').agg({'Close': ['mean', 'max', 'min'], 'Volume': ['sum', 'mean']}).to_dict()

@router.get("/price-trends")
async def price_trends():
    local_df = df.copy()
    local_df['Open time'] = pd.to_datetime(local_df['Open time'], unit='ms')
    trends_data = local_df[['Open time', 'Open', 'High', 'Low', 'Close']].fillna(method='ffill')
    return trends_data.to_dict(orient='records')

@router.get("/trade-analysis")
async def trade_analysis():
    local_df = df.copy()
    local_df['Date'] = pd.to_datetime(local_df['Open time'], unit='ms')
    local_df['YearMonth'] = local_df['Date'].dt.to_period('M').astype(str)
    monthly_trades = local_df.groupby('YearMonth')['Number of trades'].sum().reset_index()
    return monthly_trades.to_dict('records')

@router.get("/correlation-analysis")
async def correlation_analysis():
    local_df = df.copy()
    return local_df[['Volume', 'Number of trades']].corr().to_dict()

@router.get("/price-prediction")
async def price_prediction():
    return {"message": "Price prediction model not implemented"}

@router.get("/closing-price-over-time")
async def closing_price_over_time():
    local_df = df.copy()
    local_df['Timestamp'] = pd.to_datetime(local_df.iloc[:, 0], unit='ms')
    grouped_df = local_df.groupby(local_df['Timestamp'].dt.date)['Close'].mean()
    return grouped_df.to_dict()

@router.get("/calculate-rsi")
async def rsi():
    local_df = df.copy()
    local_df['RSI'] = calculate_rsi(local_df)
    local_df.dropna(subset=['RSI'], inplace=True)
    local_df['Open time'] = pd.to_datetime(local_df['Open time'], unit='ms').dt.strftime('%Y-%m-%dT%H:%M:%S')
    rsi_data = local_df[['Open time', 'Close', 'RSI']].to_dict(orient='records')
    return rsi_data

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = ((delta > 0) * delta).fillna(0)
    loss = ((delta < 0) * -delta).fillna(0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi
