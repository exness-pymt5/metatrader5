import os
import time
import logging
from datetime import datetime

import talib
import pandas
import MetaTrader5 as mt5

from source.broker.metatrader import MetaTrader

# config
BROKER      = "EXNESS"
INSTRUMENT  = "EURUSD"
TIMEFRAME   = "5Min"
LOOBACK     = 200
HEART_BEAT  = 10
LOTSIZE     = 0.01
OUTPUT_PATH = './result/sma_cross_{}_{}.csv'.format(INSTRUMENT.lower(), BROKER.lower())

# terminal config
TERMINAL_PATH = # 'Path EXNESS terminal64.exe'
ACCOUNT       = # Account Int type
PASSWORD      = # "Password"
SERVER        = "Exness-MT5Real" # Account type

LOG_TICK = '{time} - {instrument} bid : {bid}, ask : {ask}, close : {close}, sma_s : {sma_s:.5f}, sma_m : {sma_m:.5f}'
LOG_ENTY = '{time} - OPEN LONG {instrument} @ {bid} volume : {volume}'
LOG_MDFY = '{time} - PROTECT RISK {trade_id} sl : {old_sl} -> {new_sl}'

def open_position(side):
    open_attempt    = 0
    trade_open_info = None
    
    while not trade_open_info:
        # open request counter
        print("open attempt : {}".format(open_attempt))

        open_attempt += 1
        open_request = {
            "action"       : mt5.TRADE_ACTION_DEAL, 
            "symbol"       : INSTRUMENT, 
            "price"        : mt5.symbol_info_tick(INSTRUMENT).ask,
            "volume"       : 0.01, 
            "deviation"    : 50, 
            "magic"        : 123456, 
            "comment"      : "order_send_market", 
            "type_time"    : mt5.ORDER_TIME_GTC, 
            "type_filling" : mt5.ORDER_FILLING_IOC
        }

        if side == 'BUY':
            open_request["type"]  = mt5.ORDER_TYPE_BUY
            open_request["price"] = mt5.symbol_info_tick(INSTRUMENT).ask
        
        if side == 'SELL':
            open_request["type"] = mt5.ORDER_TYPE_SELL
            open_request["price"] = mt5.symbol_info_tick(INSTRUMENT).bid
            
        open_timed = time.perf_counter_ns()
        response   = mt5.order_send(open_request)
        open_timed = time.perf_counter_ns() - open_timed
        
        time.sleep(2)
        
        trades = broker.get_trades()
    
        for trade in trades:
            if trade['symbol'] == INSTRUMENT:
                trade_open_info = [trade['ticket'],
                                   trade['symbol'], 
                                   trade['volume'],
                                   trade['price_open'],
                                   open_request["price"],
                                   open_attempt,
                                   open_timed,
                                   trade['time']]
                print("open success : {}".format(trade_open_info))
                break
    
    return trade_open_info

def close_position(position, side):
    close_attempt    = 0
    trade_close_info = None
    
    while not trade_close_info:
        # close request counter
        print("close attempt : {}".format(close_attempt))

        close_attempt += 1

        close_request = {
            'action'       : mt5.TRADE_ACTION_DEAL,
            'position'     : position,
            'symbol'       : INSTRUMENT,
            'volume'       : LOTSIZE,
            'price'        : mt5.symbol_info_tick(INSTRUMENT).bid if side == 'BUY' else mt5.symbol_info_tick(INSTRUMENT).ask,
            'deviation'    : 50,
            'type'         : mt5.ORDER_TYPE_SELL if side == 'BUY' else mt5.ORDER_TYPE_BUY,
            "type_filling" : mt5.ORDER_FILLING_IOC
        }

        print(close_request)
            
        close_timed = time.perf_counter_ns()
        response    = mt5.order_send(close_request)
        close_timed = time.perf_counter_ns() - close_timed
        
        time.sleep(2)

        position_deals = mt5.history_deals_get(position=position)
        
        try:
            trade_close_info = [position_deals[1].price,
                                position_deals[1].profit,
                                close_request["price"],
                                close_attempt,
                                close_timed,
                                position_deals[1].time,
                                position_deals[1].commission]
            print("close success : {}".format(trade_close_info))
        except:
            trade_close_info = None
    
    return trade_close_info

def record_trade_info(open_position_info, close_position_info):
    info = {
        'source'              : BROKER, 
        'instrument'          : INSTRUMENT,
        'open_ticket'         : open_position_info[0],
        'open_timestamp'      : open_position_info[7],
        'open_request_price'  : open_position_info[4],
        'open_matched_price'  : open_position_info[3],
        'open_attempt'        : open_position_info[5],
        'latency_open'        : open_position_info[6],
        'experiment'          : 'order_send_market', 
        'close_timestamp'     : close_position_info[5],
        'close_request_price' : close_position_info[2],
        'close_matched_price' : close_position_info[0],
        'close_attempt'       : close_position_info[3],
        'latency_close'       : close_position_info[4],
        'profit'              : close_position_info[1],
        'commission'          : close_position_info[6],
    }

    header = not os.path.exists(OUTPUT_PATH)
    df = pandas.DataFrame([info])
    df.to_csv(OUTPUT_PATH, mode='a', index=False, header=header)

def run():
    open_position_info  = None
    close_position_info = None

    long_order_condition   = True
    short_order_condition  = False

    while True:
        # fetch price from broker (candlestick)
        bars = broker.get_ohlcv(INSTRUMENT, TIMEFRAME, LOOBACK)

        # fetch orders & trades from broker 
        orders = broker.get_orders()
        trades = broker.get_trades()

        print("orders : {}".format(orders))
        print("trades : {}".format(trades))

        # calculate indicator
        sma_s = talib.SMA(bars['close'], 5)
        sma_m = talib.SMA(bars['close'], 10)

        print("sma_s : {}".format(sma_s[-5:]))
        print("sma_m : {}".format(sma_m[-5:]))

        # generate long signal
        previous_condition   = sma_s.iloc[-3] < sma_m.iloc[-3]
        current_condition    = sma_s.iloc[-2] > sma_m.iloc[-2]
        long_order_condition = previous_condition & current_condition

        # generate short signal
        previous_condition    = sma_s.iloc[-3] > sma_m.iloc[-3]
        current_condition     = sma_s.iloc[-2] < sma_m.iloc[-2]
        short_order_condition = previous_condition & current_condition

        print("long_condition  : {}".format(long_order_condition))
        print("short_condition : {}".format(short_order_condition))

        assert len(trades) <= 1, "got more than one open position."
        
        # now = datetime.now()
        # if now.minute % 3 == 0:
        #     long_order_condition  = not long_order_condition
        #     short_order_condition = not short_order_condition
        #     time.sleep(55)
        
        # print("^long_condition  : {}".format(long_order_condition))
        # print("^short_condition : {}".format(short_order_condition))

        if len(trades) == 0:
            is_long_position  = False
            is_short_position = False
        else:
            is_long_position  = trades[0]['side'] == 'BUY'
            is_short_position = trades[0]['side'] == 'SELL'

        print("is_long_position  : {}".format(is_long_position))
        print("is_short_position : {}".format(is_short_position))

        # assert is_long_position != is_short_position, "got long and short positions at the same time."

        # get bid, ask price
        bid, ask = broker.get_tick(INSTRUMENT)

        if long_order_condition:
            if is_long_position: 
                print("['long_order_condition']  nothing to do we already have long positions")
            else:
                if is_short_position: 
                    print("['long_order_condition']  we need to close short position before open long")
                    close_position_info = close_position(trades[0]['ticket'], trades[0]['side'])
                    record_trade_info(open_position_info, close_position_info)
                    open_position_info  = None
                    close_position_info = None

                # open long position
                print("['long_order_condition']  open long")
                open_position_info = open_position('BUY')

        if short_order_condition:
            if is_short_position: 
                print("['short_order_condition'] nothing to do we already have short positions")
            else:
                if is_long_position:
                    print("['short_order_condition'] we need to close long position before open short")
                    close_position_info = close_position(trades[0]['ticket'], trades[0]['side'])
                    record_trade_info(open_position_info, close_position_info)
                    open_position_info  = None
                    close_position_info = None

                # open short position
                print("['short_order_condition'] open short")
                open_position_info = open_position('SELL')

        print("sleeping")
        time.sleep(HEART_BEAT)
        print("\n ========================== \n")


if __name__ == "__main__":
    logging.basicConfig(filename='example.log',level=logging.DEBUG)

    broker = MetaTrader(
        TERMINAL_PATH, ACCOUNT, PASSWORD, SERVER
    )

    if broker.connected(): 
        run()
    else:
        raise "Can't connect to broker"