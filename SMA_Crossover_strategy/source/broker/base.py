from abc import ABC, abstractmethod

class AbstractBroker(ABC):

    @abstractmethod
    def connected(self):
        raise NotImplementedError("Should implement ping()")
    
    @abstractmethod
    def get_tick(self):
        raise NotImplementedError("Should implement get_bid()")

    @abstractmethod
    def get_ohlcv(self):
        raise NotImplementedError("Should implement get_ohlc()")

    @abstractmethod
    def get_orders(self):
        raise NotImplementedError("Should implement get_orders()")

    @abstractmethod
    def get_trades(self):
        raise NotImplementedError("Should implement get_trades()")

    @abstractmethod
    def get_equity(self):
        raise NotImplementedError("Should implement get_equity()")

    @abstractmethod
    def get_balance(self):
        raise NotImplementedError("Should implement get_balance()")
    
    @abstractmethod
    def buy(self):
        raise NotImplementedError("Should implement buy()")

    @abstractmethod
    def buy_limit(self):
        raise NotImplementedError("Should implement buy_limit()")

    @abstractmethod
    def buy_stop(self):
        raise NotImplementedError("Should implement buy_stop()")

    @abstractmethod
    def sell(self):
        raise NotImplementedError("Should implement sell()")

    @abstractmethod
    def sell_limit(self):
        raise NotImplementedError("Should implement sell_limit()")

    @abstractmethod
    def sell_stop(self):
        raise NotImplementedError("Should implement sell_stop()")

    @abstractmethod
    def modify_trade_tpsl(self):
        raise NotImplementedError("Should implement modify_trade_tpsl()")