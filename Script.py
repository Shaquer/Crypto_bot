from binance.client import Client
from binance.enums import *
import datetime
import sys
import time
import winsound

api_key = "asd"
api_secret = "fgh"
symbol_1 = 'BTC'
symbol_2 = 'USDT'
symbol = symbol_1 + symbol_2
ticks_for_avg = 5
avg_offset = 2
price_index = 4  #1 - OPEN, 2 - HIGH, 3 - LOW, 4 - CLOSE
interval = Client.KLINE_INTERVAL_1MINUTE
sleep_interval = 2 #sec
client = Client(api_key, api_secret)
percentage_drop_buy = 1
percentage_pump_sell = 1.5
one_minute = 60
tick = 0
FREQUENCY = 1000  # Hz
DURATION = 200  # ms
PRECISION = 6
#START
QUANTITY_1 = float("{:0.0{}f}".format(float(client.get_asset_balance(asset=symbol_1)['free']), PRECISION))
BALANCE = float("{:0.0{}f}".format(float(client.get_asset_balance(asset=symbol_2)['free']), PRECISION))  
BUY_PRICE = 0
bought = False 

def get_avg_price(candle_sticks):
    avg_price = 0
    for i in range(len(candle_sticks) - avg_offset):
        avg_price = avg_price + float(candle_sticks[i][price_index])
    avg_price = avg_price / (len(candle_sticks) - avg_offset)
    avg_price = float("{:.2f}".format(avg_price))
    return avg_price

def should_buy(current_price, avg_price):
    return current_price < avg_price - (avg_price*percentage_drop_buy/100.0)

def should_sell(BUY_PRICE, current_price):
    return current_price > BUY_PRICE + (BUY_PRICE*percentage_pump_sell/100.0)

def buy(current_price):
    global QUANTITY_1
    print(BALANCE)
    ORDER = client.create_order(
        symbol=symbol,
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity="{:0.0{}f}".format(BALANCE/current_price, PRECISION),
        price=current_price)
    winsound.Beep(FREQUENCY, DURATION)
    QUANTITY_1 = float("{:0.0{}f}".format(float(client.get_asset_balance(asset=symbol_1)['free']), PRECISION))
    log = f'BOUGHT AT PRICE: {current_price},  {QUANTITY_1} {symbol_1} '
    print(log)
    # log to txt file
    return current_price

def sell(current_price):
    global BALANCE
    ORDER = client.create_order(
        symbol=symbol,
        side=SIDE_SELL,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity="{:0.0{}f}".format(QUANTITY_1, PRECISION),
        price=current_price)
    winsound.Beep(FREQUENCY, DURATION)
    BALANCE = float("{:0.0{}f}".format(float(client.get_asset_balance(asset=symbol_2)['free']), PRECISION))
    log = f'SOLD AT PRICE: {current_price},  {BALANCE} {symbol_2} '
    print(log)
    # log to txt file
    return current_price

def calculate_profit(old_BALANCE, BUY_PRICE, SELL_PRICE):
    new_BALANCE = old_BALANCE * (SELL_PRICE/BUY_PRICE)
    log = f'+{new_BALANCE - old_BALANCE:.2f}$, NEW BALANCE: {new_BALANCE:.2f}$'
    print(log)
    # log to txt file
    return new_BALANCE

def print_info(bought):
    global tick
    if (tick == one_minute):
        log = f'{date} - AVG PRICE: {avg_price}'
        print(log)
        # log to txt file
        if(not bought):
            log = f'BUY AT PRICE: {avg_price - (avg_price * percentage_drop_buy / 100.0):.3f}'
            print(log)
            # log to txt file
        else:
            log = f'SELL AT PRICE: {BUY_PRICE + (BUY_PRICE * percentage_pump_sell / 100.0):.3f}'
            print(log)
            # log to txt file
        tick = 0
    else:
        print(f"Current price: {current_price:.2f}")
        tick = tick + sleep_interval

while(1):
    candle_sticks = client.get_klines(symbol=symbol, interval=interval, limit=ticks_for_avg)
    time_ = candle_sticks[ticks_for_avg - 1][0] / 1000.0
    date = datetime.datetime.fromtimestamp(time_).strftime('%Y-%m-%d %H:%M:%S')
    current_price = float(client.get_orderbook_ticker(symbol=symbol)["bidPrice"])
    avg_price = get_avg_price(candle_sticks)
    print_info(bought)

    if(not bought and should_buy(current_price, avg_price)):
        BUY_PRICE = buy(current_price)
        bought = True
    if(bought and should_sell(BUY_PRICE, current_price)):
        SELL_PRICE = sell(current_price)
        bought = False
        BALANCE = calculate_profit(BALANCE, BUY_PRICE, SELL_PRICE)
    time.sleep(sleep_interval)
