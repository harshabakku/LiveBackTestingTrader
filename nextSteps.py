# -*- coding: utf-8 -*-
"""

@author: harsha

vwap crossover strategy and vwap mean reversion strategy once long is profitable, add short brackets as well 
and then comes in leverage as last piece of this game. 

rsi divergence is dif to implement and opens up a lot of possiblities. using simple RSI 30, 70, 20, 80, // relative minima, maxima

std deviation away from VWAP makes sense as well....

VWMA of RSI is also a good idea.
stoch RSI

find signals and place multiple buy orders wait for their take profit close.



trailing stop loss without taking profit is also a good idea, to catch the peaks and variable profitablity

analyze every day or every weeks trades 
as backtesting is not real testing, see if we can count on params computed using last 2 months, 1 months data
and use it for one day/one week in reality



-------------------------------------------done----------------------------------------------------


just take profit over 2 years results in losses
take profit and stop loss sma crossover results in severe losses 100000 reduced to 5000
sma vwma crossover results for all periods also results in losses.




take profit and stop loss should go in together, need to use bracket orders
then maybe include VWMA to see improvement



70 percent in 4 months for BTC data in 2019.
backtest for entire  2 year BTC data to see results. //simple take profit obviously returns in losses





done // test with wazirx data as well.



done // get 30 min data(last 1 year), exhaustive test using sma crossover to identify the peak profit params //done
done //81 percent per year on wazir USDT INR market so far.

360 percent is the goal. position sizing trying to catch more signals, long, short at the same time, along with leverage.(vwap, volume, RSI divergence is key)

"""

