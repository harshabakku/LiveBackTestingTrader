# -*- coding: utf-8 -*-
"""
'''
Author: B. Bradford 

MIT License

Copyright (c) B. Bradford

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

That they contact me for shipping information for the purpose of sending a 
local delicacy of their choice native to whatever region they are domiciled.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# Import the backtrader platform
import backtrader as bt

class RSIDivergenceIndicator(bt.ind.PeriodN):
    lines = ('signal',)
    params = dict(
        rsi_period=30,
        hl_period=100,
        hl_min=25
    )
    alias = ('RSIDiv', 'RSIDivergenceIndicator',)


    def __init__(self):
        self.hfi = bt.ind.FindFirstIndexHighest(self.data.high, period=self.p.hl_period)
        self.lfi = bt.ind.FindFirstIndexLowest(self.data.low, period=self.p.hl_period)
        self.rsi = bt.ind.RSI_Safe(period=self.p.rsi_period)

    def signal_get(self):
        signal = 0
        if self.hfp >= self.hsp:
            if self.rsi[-int(self.hfi[0])] < self.rsi[-int(self.hsi)]:
                signal -= 1

        if self.lfp <= self.lsp:
            if self.rsi[-int(self.lfi[0])] > self.rsi[-int(self.lsi)]:
                signal += 1

        return signal

    def next(self):
        h_iterable = self.data.get(size=self.p.hl_period, ago=-int(self.hfi[0]) - self.p.hl_min)
        l_iterable = self.data.get(size=self.p.hl_period, ago=-int(self.lfi[0]) - self.p.hl_min)

        if len(h_iterable) > 0 and len(l_iterable) > 0:
            m = max(h_iterable)
            self.hsi = next(i for i, v in enumerate(reversed(h_iterable)) if v == m) + int(self.hfi[0]) + self.p.hl_min

            m = min(l_iterable)
            self.lsi = next(i for i, v in enumerate(reversed(l_iterable)) if v == m) + int(self.lfi[0]) + self.p.hl_min

            self.hfp = self.data.high[-int(self.hfi[0])]
            self.hsp = self.data.high[-int(self.hsi)]
            self.lfp = self.data.low[-int(self.lfi[0])]
            self.lsp = self.data.low[-int(self.lsi)]

            self.lines.signal[0] = self.signal_get()
        else:
            self.lines.signal[0] = 0