import pandas
import MetaTrader5 as mt5


class MetaTrader(object):

    TIMEFRAME = {
        '1Min'   : mt5.TIMEFRAME_M1,
        '5Min'   : mt5.TIMEFRAME_M5,
        '10Min'  : mt5.TIMEFRAME_M10,
        '15Min'  : mt5.TIMEFRAME_M15,
        '30Min'  : mt5.TIMEFRAME_M30,
        '1H'     : mt5.TIMEFRAME_H1,
        '4H'     : mt5.TIMEFRAME_H4,
        '12H'    : mt5.TIMEFRAME_H12,
        '1D'     : mt5.TIMEFRAME_D1,
        '1W'     : mt5.TIMEFRAME_W1,
        '1M'     : mt5.TIMEFRAME_MN1
    }

    def __init__(
            self, path=None, account=None, 
            password=None, server=None,
        ):
        self.path     = path
        self.account  = account
        self.password = password
        self.server   = server
        self.records  = pandas.DataFrame({
            'function'  : [],
            'proc_time' : [],
        })

        self._initialize()

    def connected(self):
        print(mt5.terminal_info())
        print(mt5.last_error())
        return mt5.terminal_info()

    def get_tick(self, instrument):
        tick = mt5.symbol_info_tick(instrument)
        return tick.bid, tick.ask

    def get_ohlcv(self, instrument, timeframe, lookback):
        bars = self._copy_rates_from_pos(
            instrument, timeframe, lookback
        )
        return pandas.DataFrame(bars)

    def get_orders(self):
        orders = self._orders_get()
        return orders

    def get_trades(self):
        trades = []
        trades_mt5 = self._positions_get()
        for trade in trades_mt5:
            trades.append({
                'ticket'     : trade.ticket,
                'symbol'     : trade.symbol,
                'price_open' : trade.price_open,
                'tp'         : trade.tp,
                'sl'         : trade.sl,
                'profit'     : trade.profit,
                'volume'     : trade.volume,
                'time'       : trade.time,
                'side'       : 'BUY' if trade.type == 0 else 'SELL'
            })
        return trades

    def get_equity(self):
        equity = self._account_info().equity
        return equity

    def get_balance(self):
        balance = self._account_info().balance
        return balance
    
    def get_contract_size(self, instrument):
        contract_size = self._symbol_info(instrument).trade_contract_size
        return contract_size

    def buy(
            self, instrument, volume, deviation=20, 
            takeprofit=None, stoploss=None, 
            magic=123456, comment="Python-MT5"
        ):
        request = {
            'action'       : mt5.TRADE_ACTION_DEAL,
            'symbol'       : instrument,
            'volume'       : volume,
            'type'         : mt5.ORDER_TYPE_BUY,
            'deviation'    : deviation,
            'magic'        : magic,
            'comment'      : comment,
            'type_time'    : mt5.ORDER_TIME_GTC,
            'type_filling' : mt5.ORDER_FILLING_FOK
        }

        if takeprofit : request['tp'] = takeprofit
        if stoploss   : request['sl'] = stoploss
        
        response = self._order_send(request)
        print(response)
        return response

    def buy_limit(
            self, instrument, price, volume, deviation=20, 
            takeprofit=None, stoploss=None, 
            magic=123456, comment="Python-MT5"
        ):
        request = {
            'action'       : mt5.TRADE_ACTION_PENDING,
            'symbol'       : instrument,
            'volume'       : volume,
            'price'        : price,
            'type'         : mt5.ORDER_TYPE_BUY_LIMIT,
            'deviation'    : deviation,
            'magic'        : magic,
            'comment'      : comment,
            'type_time'    : mt5.ORDER_TIME_GTC,
            'type_filling' : mt5.ORDER_FILLING_FOK
        }

        if takeprofit : request['tp'] = takeprofit
        if stoploss   : request['sl'] = stoploss
        
        response = self._order_send(request)
        return response
    
    def buy_stop(
            self, instrument, price, volume, deviation=20, 
            takeprofit=None, stoploss=None, 
            magic=123456, comment="Python-MT5"
        ):
        request = {
            'action'       : mt5.TRADE_ACTION_PENDING,
            'symbol'       : instrument,
            'volume'       : volume,
            'price'        : price,
            'type'         : mt5.ORDER_TYPE_BUY_STOP,
            'deviation'    : deviation,
            'magic'        : magic,
            'comment'      : comment,
            'type_time'    : mt5.ORDER_TIME_GTC,
            'type_filling' : mt5.ORDER_FILLING_FOK
        }

        if takeprofit : request['tp'] = takeprofit
        if stoploss   : request['sl'] = stoploss
        
        response = self._order_send(request)
        return response

    def sell(
            self, instrument, volume, deviation=20, 
            takeprofit=None, stoploss=None, 
            magic=123456, comment="Python-MT5"
        ):
        request = {
            'action'       : mt5.TRADE_ACTION_DEAL,
            'symbol'       : instrument,
            'volume'       : volume,
            'type'         : mt5.ORDER_TYPE_SELL,
            'deviation'    : deviation,
            'magic'        : magic,
            'comment'      : comment,
            'type_time'    : mt5.ORDER_TIME_GTC,
            'type_filling' : mt5.ORDER_FILLING_FOK
        }

        if takeprofit : request['tp'] = takeprofit
        if stoploss   : request['sl'] = stoploss
        
        response = self._order_send(request)
        return response

    def sell_limit(
            self, instrument, price, volume, deviation=20, 
            takeprofit=None, stoploss=None, 
            magic=123456, comment="Python-MT5"
        ):
        request = {
            'action'       : mt5.TRADE_ACTION_PENDING,
            'symbol'       : instrument,
            'volume'       : volume,
            'price'        : price,
            'type'         : mt5.ORDER_TYPE_SELL_LIMIT,
            'deviation'    : deviation,
            'magic'        : magic,
            'comment'      : comment,
            'type_time'    : mt5.ORDER_TIME_GTC,
            'type_filling' : mt5.ORDER_FILLING_FOK
        }

        if takeprofit : request['tp'] = takeprofit
        if stoploss   : request['sl'] = stoploss
        
        response = self._order_send(request)
        return response
    
    def sell_stop(
            self, instrument, price, volume, deviation=20, 
            takeprofit=None, stoploss=None, 
            magic=123456, comment="Python-MT5"
        ):
        request = {
            'action'       : mt5.TRADE_ACTION_PENDING,
            'symbol'       : instrument,
            'volume'       : volume,
            'price'        : price,
            'type'         : mt5.ORDER_TYPE_SELL_STOP,
            'deviation'    : deviation,
            'magic'        : magic,
            'comment'      : comment,
            'type_time'    : mt5.ORDER_TIME_GTC,
            'type_filling' : mt5.ORDER_FILLING_FOK
        }

        if takeprofit : request['tp'] = takeprofit
        if stoploss   : request['sl'] = stoploss
        
        response = self._order_send(request)
        return response
    
    def modify_trade_tpsl(self, trade_id, tp=None, sl=None):
        request = {
            'action'   : mt5.TRADE_ACTION_SLTP,
            'position' : trade_id,
        }

        if tp: request['tp'] = tp 
        if sl: request['sl'] = sl

        response = self._order_send(request)
        return response

    def close_trade(self, trade_id, trade_side, instrument, volume, deviation=20):
        request = {
            'action'    : mt5.TRADE_ACTION_DEAL,
            'position'  : trade_id,
            'symbol'    : instrument,
            'volume'    : volume,
            'deviation' : deviation
        }

        if trade_side == 'BUY'  : request['type'] = mt5.ORDER_TYPE_SELL
        if trade_side == 'SELL' : request['type'] = mt5.ORDER_TYPE_BUY

        response = self._order_send(request)
        return response

    
    def _initialize(self):
        return mt5.initialize(
                    path     = self.path,
                    login    = self.account,
                    password = self.password,
                    server   = self.server,
                    timeout  = 10,
                    portable = False
                )

    def _symbol_info_tick(self, instrument):
        return mt5.symbol_info_tick(instrument)

    def _copy_rates_from_pos(self, instrument, timeframe, lookback):
        return mt5.copy_rates_from_pos(
            instrument, MetaTrader.TIMEFRAME[timeframe], 0, lookback
        )
    
    def _orders_get(self):
        return mt5.orders_get()
    
    def _positions_get(self):
        return mt5.positions_get()

    def _account_info(self):
        return mt5.account_info()
    
    def _symbol_info(self, instrument):
        return mt5.symbol_info(instrument)
    
    def _order_send(self, request):
        return mt5.order_send(request)
