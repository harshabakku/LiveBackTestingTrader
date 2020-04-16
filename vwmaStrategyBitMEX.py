from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import math
from VolumeWeightedAveragePrice import VWAP


# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('stoploss', 0.01),   
        ('profit_mult', 4),
        ('maperiod1', 15),
        ('maperiod2', 30),
        ('printlog', False),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.datetime(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.dataopen  = self.datas[0].open
        self.datahigh  = self.datas[0].high
        self.datalow   = self.datas[0].low
                  

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        self.trades = 0
        
        self.order_dict = {}

        # Add a MovingAverageSimple indicator
        self.sma1 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod1)
        
#        self.sma2 = bt.indicators.SimpleMovingAverage(
#            self.datas[0], period=self.params.maperiod2)
        
        self.vwap = VWAP(period=self.params.maperiod1)
                    
            

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
#           cancel take profit or stop loss order that was placed earlier //bracket order is efficient and this problem is eliminated.
#            if 'name' in order.info:
#                self.broker.cancel(self.order_dict[order.ref])
#                print("other order cancelled")
#                if self.order_dict[order.ref].executed.price > 0:
#                    print(' problem error take profit and stop loss got executed ################################################################################################')
#                    self.log('Open %.7f ,High %.7f ,Low %.7f , Close %.7f,  SMA1,2 %.7f %.7f' % (self.dataopen[0],self.datahigh[0],self.datalow[0], self.dataclose[0], self.sma1[0], self.sma2[0]), doprint=True)
#        
            if order.isbuy():

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                
                
                self.log(
                    'BUY EXECUTED, Price: %.7f, Cost: %.7f, Comm %.7f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.7f, Cost: %.7f, Comm %.7f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
#                print('current Portfolio Value: %.7f' % cerebro.broker.getvalue())          

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.trades = self.trades + 1;
#        self.log('Open %.7f , Close %.7f,  SMA1,2 %.7f %.7f' % (self.dataopen[0], self.dataclose[0], self.sma1[0], self.sma2[0]))                
        self.log('OPERATION PROFIT, GROSS %.7f, NET %.7f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Open %.7f , High %.7f , Low %.7f , Close %.7f,  SMA %.7f , VWAP %.7f' % (self.dataopen[0],self.datahigh[0],self.datalow[0], self.dataclose[0], self.sma1[0], self.vwap[0]))
        
#        handle NaN data that causes Order Canceled/Margin/Rejected error 
        if (math.isnan(self.dataopen[0]) or math.isnan(self.dataclose[0]) or math.isnan(self.sma1[0]) or math.isnan(self.vwap[0])):
            return
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        
        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            # sma1 should be breaking out sma2, so check the earlier candle as well
            if self.sma1[-1] <= self.vwap[-1]: 
                if self.sma1[0] > self.vwap[0]:
    
                    # BUY, BUY, BUY!!! (with all possible default parameters)
                    self.log('CREATE BRACKET ORDER WITH BUY , %.7f' % self.dataclose[0])
    
    
                    order_price = self.dataclose[0];
                    stop_loss = order_price*(1.0 - (self.p.stoploss))
                    take_profit = order_price*(1.0 + self.p.profit_mult*(self.p.stoploss))
    
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy_bracket(limitprice=take_profit, price=order_price, stopprice=stop_loss)

    #                self.log(self.order)
                       
#                    sl_ord = self.sell(exectype=bt.Order.Stop,
#                                       price=stop_loss)
#                    sl_ord.addinfo(name="Stop")
#    
#                    tkp_ord = self.sell(exectype=bt.Order.Limit,
#                                        price=take_profit)
#                    tkp_ord.addinfo(name="Prof")
#    
#                    self.order_dict[sl_ord.ref] = tkp_ord
#                    self.order_dict[tkp_ord.ref] = sl_ord
    
                    self.log(
                        'STOP LOSS : %.7f AND TAKE PROFIT : %.7f' %
                        (stop_loss,
                         take_profit))                

               
       # else:

       #     if self.sma1[0] < self.sma2[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
       #         self.log('SELL CREATE, %.7f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
       #         self.order = self.sell()

    def stop(self):
        self.log('Ending Value %.7f (Profit Multiplier: %2d) (MA and VWAP Periods %2d ) Total trades %.2f ' %
                 (self.broker.getvalue(),self.params.profit_mult, self.params.maperiod1, self.trades ), doprint=True)

def printTradeAnalysis(analyzer):
        '''
        Function to print the Technical Analysis results in a nice format.
        '''
        #Get the results we are interested in
        total_open = analyzer.total.open
        total_closed = analyzer.total.closed
        total_won = analyzer.won.total
        total_lost = analyzer.lost.total
        win_streak = analyzer.streak.won.longest
        lose_streak = analyzer.streak.lost.longest
        pnl_net = round(analyzer.pnl.net.total,2)
        strike_rate = (total_won / total_closed) * 100
        #Designate the rows
        h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
        h2 = ['Strike Rate','Win Streak', 'Losing Streak', 'PnL Net']
        r1 = [total_open, total_closed,total_won,total_lost]
        r2 = [strike_rate, win_streak, lose_streak, pnl_net]
        #Check which set of headers is the longest.
        if len(h1) > len(h2):
            header_length = len(h1)
        else:
            header_length = len(h2)
        #Print the rows
        print_list = [h1,r1,h2,r2]
        row_format ="{:<20}" * (header_length + 1)
        print("Trade Analysis Results:")
        for row in print_list:
            print(row_format.format('',*row))
    
def printSQN(analyzer):
    sqn = round(analyzer.sqn,2)
    print('SQN: {}'.format(sqn))

def printDrawDownAnalysis(analyzer):
    '''
    Function to print the Technical Analysis results in a nice format.
    '''
    #Get the results we are interested in
    drawdown = round(analyzer.drawdown, 2)
    moneydown = round(analyzer.moneydown, 2)
    length = analyzer.len
    max_dd = round(analyzer.max.drawdown, 2)
    max_md = round(analyzer.max.moneydown, 2)
    max_len = analyzer.max.len

    #Designate the rows
    h1 = ['Drawdown', 'Moneydown', 'Length']
    h2 = ['Max drawdown','Max moneydown', 'Max len']
    r1 = [drawdown, moneydown,length]
    r2 = [max_dd, max_md, max_len]
    #Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)
    #Print the rows
    print_list = [h1,r1,h2,r2]
    row_format ="{:<20}" * (header_length + 1)
    print("Drawdown Analysis Results:")
    for row in print_list:
        print(row_format.format('',*row))
    

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro(optreturn=False)


# optstrategy approach doesnt work with analyzers as of now
    # Add a strategy
#    strats = cerebro.optstrategy(
#        TestStrategy,
#        maperiod1=range(10, 31))
    cerebro.optstrategy(TestStrategy,  profit_mult = range(1,5), maperiod1 = range(15,30))
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '')

    # Create a Data Feed
#    data = bt.feeds.YahooFinanceCSVData(
#        dataname=datapath,
#        # Do not pass values before this date
#        fromdate=datetime.datetime(2000, 1, 1),
#        # Do not pass values before this date
#        todate=datetime.datetime(2000, 12, 31),
#        # Do not pass values after this date
#        reverse=False)

    data = bt.feeds.GenericCSVData(dataname="./datas/bitmex_XBT_USD.csv",
                                   datetime=0,
                                   fromdate=datetime.datetime(2020,1,21),
                                   todate=datetime.datetime(2020,3,21),
                                   open=1,
                                   high=2,
                                   low=3,
                                   close=4,
                                   openinterest=-1,
                                   time=-1,
                                   volume=5,
                                   timeframe=bt.TimeFrame.Minutes,
                                   compression=1,
                                   dtformat=1)

#     Add the Data Feed to Cerebro
#    cerebro.adddata(data)
#   use resample functionality instead of adding 1 minute data directly
    cerebro.resampledata(data,
                         timeframe=bt.TimeFrame.Minutes,
                         compression=5)
    # Add the Data Feed to Cerebro

    # Set our desired cash start
    # trading with around 1000 dollars each time
    cerebro.broker.setcash(100000.0)
    
    
    # Add the analyzers we are interested in
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="dd")
    

    # Add a FixedSize sizer according to the stake
    #1313 dollars is around 1 lakh, 2lakh cash is set just to ensure not to run out of money
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
     # Set the commission - 0.25% ... divide by 100 to remove the %    
    cerebro.broker.setcommission(commission=0.0025)


#    print('Starting Portfolio Value: %.7f' % cerebro.broker.getvalue())
#    print('Final Portfolio Value: %.7f' % cerebro.broker.getvalue())

    # Run over everything
    strategies = cerebro.run(maxcpus=1)
    # print(strategies[0][0].analyzers)
 
#    for run in strategies:
#        for strategy in run:
#            value = round(strategy.broker.get_value(),2)
##            PnL = round(value - startcash,2)
##            period = strategy.params.period
##            final_results_list.append([period,PnL])
#   
    print('################################################################################################')
    
    for strat in strategies:
        strategy = strat[0]
        value = round(strategy.broker.get_value(),2)
        profit_mult = strategy.params.profit_mult
        print('profit multiplier: %.2f' % profit_mult)
        
#        incorrect value print('final portfolio value: %.2f' % value)
        print('maperiod1: %.2f' % strategy.params.maperiod1)
        print('maperiod2: %.2f' % strategy.params.maperiod2)        
        # print the analyzers
        # list of list is returned this is way to find analyzer    
        printSQN(strategy.analyzers.sqn.get_analysis())
        printTradeAnalysis(strategy.analyzers.ta.get_analysis())
        printDrawDownAnalysis(strategy.analyzers.dd.get_analysis())
        print('################################################################################################')
    
    