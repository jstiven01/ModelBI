#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 30 08:23:54 2018

@author: jstiven01
"""

import pandas as pd
import numpy as np
import argparse

#######################################
##### CONSTANTS########################
#Constant Indicator
nameIndic = "MA"
#Constant Filename
filename = "Preciosohlc.csv"
#######################################

class SMAPatterns():

    def __init__(self, ctepips, symbol):
        '''Initializing Attributes'''

        self.dfprices = pd.read_csv("../data/"+filename, header=None)
        # Naming Columns
        self.dfprices.columns = ["Date", "Time", "Open", "High", "Low", "Close", "Volume"]

        #Constant Pips
        self.ctePips = ctepips

        #Symbol
        self.symbol = symbol

        #Dataframe Results and Perfomance
        self.dfresults = pd.DataFrame()
        self.dfperform = pd.DataFrame
        self.Expectancy = []
        self.Accuracy = []
        self.PLTotal = []
        self.TotalTrades = []
        return

    def pipCandles(self, candlesExp, singleStrategy = False):
        """Computing the Pips for every candle in both ways: LONG and SHORT """

        for i in range(0, candlesExp+1, 1):
            if singleStrategy:
                i = candlesExp
            self.dfprices['PipsLong{}'.format(i)] = (self.dfprices["Close"].shift(-i) - self.dfprices["Open"]) * self.ctePips
            self.dfprices['PipsShort{}'.format(i)] = (self.dfprices["Open"] - self.dfprices["Close"].shift(-i)) * self.ctePips
            self.dfprices['CloseDate{}'.format(i)] = self.dfprices["Date"].shift(-i)
            self.dfprices['CloseTime{}'.format(i)] = self.dfprices["Time"].shift(-i)
            self.dfprices['ClosePrice{}'.format(i)] = self.dfprices["Close"].shift(-i)
            if singleStrategy:
                break
        return

    def smaPeriodPrice(self, price, period, inverse, singleStrategy = False):
        """Calculating SMA with price (open, close, high, low) and period"""

        for i in range(2, period+1 , 1):
            if singleStrategy:
                i=period
            # Rolling create windows/subsets of prices and computes the mean of subset
            self.dfprices[nameIndic + price+'{}'.format(i)] = self.dfprices[price].rolling(window=i).mean()

            #Rounded to 8 Decimals
            self.dfprices[nameIndic + price+'{}'.format(i)] = self.dfprices[nameIndic + price+'{}'.format(i)].round(8)

            # Creating column of Entries
            self.dfprices['ENTRY' + nameIndic + price+'{}'.format(i)] = "NO ENTRY"

            # Filter to identify the LONG Entries
            FilterLong = (self.dfprices["Close"].shift(2) < self.dfprices[nameIndic + price+'{}'.format(i)].shift(2)) \
                         & (self.dfprices["Close"].shift(1) > self.dfprices[nameIndic + price+'{}'.format(i)].shift(1))

            # Filter to identify the SHORT Entries
            FilterShort = (self.dfprices["Close"].shift(2) > self.dfprices[nameIndic + price+'{}'.format(i)].shift(2)) \
                          & (self.dfprices["Close"].shift(1) < self.dfprices[nameIndic + price+'{}'.format(i)].shift(1))

            # Adding Entries to column Entry
            if inverse:
                self.dfprices.loc[FilterLong, 'ENTRY' + nameIndic + price+'{}'.format(i)] = "CORTO"
                self.dfprices.loc[FilterShort, 'ENTRY' + nameIndic + price+'{}'.format(i)] = "LARGO"
            else:
                self.dfprices.loc[FilterLong, 'ENTRY' + nameIndic + price+'{}'.format(i)] = "LARGO"
                self.dfprices.loc[FilterShort, 'ENTRY' + nameIndic + price+'{}'.format(i)] = "CORTO"

            if singleStrategy:
                break


        #print(self.dfprices)
        
        return

    def tradeStrategies(self, price, period, candlesExp):
        """Consolidating all Strategies with different sma and expiration"""

        # Creating Dataframe with consolidated results
        self.dfresults = pd.DataFrame(index=(pd.to_datetime(self.dfprices["Date"]).dt.year).drop_duplicates())

        # Consolidating Trade Strategy for every candle (k) and every period (i)
        for k in range(0, candlesExp + 1, 1):
            for i in range(2, period + 1, 1):

                #Creating Filter to identify the LONG and SHORT Trades
                FiltLongEntries = (self.dfprices['ENTRY' + nameIndic + price+'{}'.format(i)] == "LARGO")
                FiltShortEntries = (self.dfprices['ENTRY' + nameIndic + price+'{}'.format(i)] == "CORTO")

                #Applying Filters on the dfprices and renaming the columns because of PipsLong and PipsShort
                TradesLong = self.dfprices.loc[FiltLongEntries, ("Date", "Time", 'PipsLong{}'.format(k))]
                TradesLong.rename(columns={'PipsLong{}'.format(k): 'PipsCandle{}'.format(k)}, inplace=True)
                TradesShort = self.dfprices.loc[FiltShortEntries, ("Date", "Time", 'PipsShort{}'.format(k))]
                TradesShort.rename(columns={'PipsShort{}'.format(k): 'PipsCandle{}'.format(k)}, inplace=True)

                #Joining the LONG and SHORT Trades and sorting
                Trades = pd.concat([TradesLong, TradesShort])
                Trades.sort_index(inplace=True)

                # Creating column Year
                Trades["Year"] = (pd.to_datetime(Trades["Date"]).dt.year)

                #The Strategy should have at least one trade per year
                if len(self.dfresults.index) == len(Trades.groupby("Year")):
                    # Grouping by Years
                    self.dfresults[nameIndic + price+'{}'.format(i) + 'Cand{}'.format(k)] = \
                        (Trades.groupby("Year")['PipsCandle{}'.format(k)].agg('sum')).values

                    # Performance
                    self.Expectancy.append(Trades['PipsCandle{}'.format(k)].mean())
                    self.PLTotal.append(Trades['PipsCandle{}'.format(k)].sum())
                    PosTrades = Trades[Trades['PipsCandle{}'.format(k)] > 0].shape[0]
                    NegTrades = Trades[Trades['PipsCandle{}'.format(k)] < 0].shape[0]
                    self.Accuracy.append(PosTrades / (PosTrades + NegTrades))
                    self.TotalTrades.append(Trades["Date"].count())

        #print(self.dfresults)
        return

    def performanceStrategies(self):
        """ Getting the perfomance of every Strategy"""

        dfPLTotal = pd.DataFrame(self.PLTotal)
        dfAcc = pd.DataFrame(self.Accuracy)
        dfExp = pd.DataFrame(self.Expectancy)
        dfPosYear = pd.DataFrame((self.dfresults[self.dfresults > 0].count()).values)
        dfTotalTrades = pd.DataFrame(self.TotalTrades)
        self.dfperform = pd.concat([dfPLTotal, dfAcc, dfExp, dfPosYear,dfTotalTrades], axis=1)
        self.dfperform = self.dfperform.T
        self.dfperform.columns = self.dfresults.columns
        indexnames = ["P/LTotal", "Accuracy", "Expectancy", "PosYears", "TotalTrades"]
        self.dfperform.index = indexnames

        ##print(self.dfperform)
        return

    def writeResults(self, price):
        dftotal = pd.concat([self.dfresults, self.dfperform])
        dftotal.T.to_csv(self.symbol+nameIndic+"Results"+price+".csv", sep=',')
        print("STRATEGIES BEST PERFORMANCES")
        print(self.dfperform.idxmax(1))
        print("STRATEGIES WORST PERFORMANCES")
        print(self.dfperform.idxmin(1))
        return

    def writingPatterns(self, price, period, candlesExp):


        # Creating Filter to identify the LONG and SHORT Pattern
        FiltLongEntries =  ((self.dfprices['ENTRY' + nameIndic + price + '{}'.format(period)]).shift(-1) == "LARGO")
        FiltShortEntries = ((self.dfprices['ENTRY' + nameIndic + price + '{}'.format(period)]).shift(-1) == "CORTO")

        # Applying Filters on the dfprices and renaming the columns because of PipsLong and PipsShort
        PatternLong = self.dfprices.loc[FiltLongEntries,("Date", "Time","Open","High","Low","Close")]
        PatternShort = self.dfprices.loc[FiltShortEntries,("Date", "Time","Open","High","Low","Close")]

        # Joining the LONG and SHORT Pattern and sorting
        Pattern = pd.concat([PatternLong, PatternShort])
        Pattern.sort_index(inplace=True)

        #Setting the column position at the beginning
        Pattern["NAMEPATTERN"] = nameIndic + price + str(period) + "Cand" + str(candlesExp)
        cols = Pattern.columns.tolist()
        Pattern = Pattern[[cols[-1]] + cols[:-1]]

        Pattern.to_csv(self.symbol+nameIndic + "Patterns" + price + str(period) + "Cand" + str(candlesExp) + ".csv", sep=',',
                      index=None)

        return

    def singleStrategy(self, price, period, candlesExp, mode):

        self.pipCandles(candlesExp, True)
        self.smaPeriodPrice(price, period, mode, True)
        # Creating Filter to identify the LONG and SHORT Trades
        FiltLongEntries = (self.dfprices['ENTRY' + nameIndic + price + '{}'.format(period)] == "LARGO")
        FiltShortEntries = (self.dfprices['ENTRY' + nameIndic + price + '{}'.format(period)] == "CORTO")

        # Applying Filters on the dfprices and renaming the columns because of PipsLong and PipsShort
        TradesLong = self.dfprices.loc[FiltLongEntries, ("Date", "Time","Open","CloseDate{}".format(candlesExp),\
                                                         "CloseTime{}".format(candlesExp),\
                                                         "ClosePrice{}".format(candlesExp),\
                                                         "PipsLong{}".format(candlesExp))]
        TradesLong.rename(columns={'PipsLong{}'.format(candlesExp): 'PipsCandle{}'.format(candlesExp)}, inplace=True)
        TradesLong["POSITION"] = "LARGO"
        TradesShort = self.dfprices.loc[FiltShortEntries, ("Date", "Time","Open","CloseDate{}".format(candlesExp),\
                                                         "CloseTime{}".format(candlesExp),\
                                                         "ClosePrice{}".format(candlesExp),\
                                                         "PipsShort{}".format(candlesExp))]
        TradesShort.rename(columns={'PipsShort{}'.format(candlesExp): 'PipsCandle{}'.format(candlesExp)}, inplace=True)
        TradesShort["POSITION"] = "CORTO"

        # Joining the LONG and SHORT Trades and sorting
        Trades = pd.concat([TradesLong, TradesShort])
        Trades.sort_index(inplace=True)

        #Setting the column position at the beginning
        cols = Trades.columns.tolist()
        Trades = Trades[[cols[-1]] + cols[:-1]]

        Trades.to_csv(self.symbol+nameIndic+"Strategy" + price + str(period) + "Cand" + str(candlesExp) + ".csv",
                      sep=',', index=None)

        self.writingPatterns(price, period, candlesExp)

        print("Check Files of Strategy and Patterns")

        return

    def simulateStrategies(self, price, period, candlesExpired, mode):
        self.pipCandles(candlesExpired)
        self.smaPeriodPrice(price, period, mode)
        self.tradeStrategies(price, period, candlesExpired)
        self.performanceStrategies()
        self.writeResults(price)

        return


if __name__ == "__main__":

    # create the top-level parser
    parser = argparse.ArgumentParser(prog='SMAPatterns')
    parser.add_argument('--sim', action='store_true',
                        help='Start simulation')
    parser.add_argument('--strg', action='store_true',
                        help='Generate single strategy')
    parser.add_argument('--period', type=int, required=True,
                         help='Periods of SMA to simulate/evaluate')
    parser.add_argument('--candlesexp', type=int, required=True,
                         help='Candles to close Trade')
    parser.add_argument('--price', type=str, required=True,
                         help='Type of Price to use in SMA (open, high, low, close) in lowercase')
    parser.add_argument('--symbol', type=str, required=True,
                         help='Symbol tu evaluate: AUDUSD, EURJPY, ...')
    parser.add_argument('--inv', action='store_true',
                        help='Generate Inverse Trades')


    clargs = parser.parse_args()

    #Selecting constant pips
    symbol = clargs.symbol.upper()
    if symbol.find('JPY',3) == -1: #No String JPY
        ctepips = 10000
    else:
        ctepips = 100

    #Creating SMAAPattern's Object
    sma = SMAPatterns(ctepips, symbol)

    if clargs.sim:
        sma.simulateStrategies(clargs.price.title(), clargs.period, clargs.candlesexp, clargs.inv)
    elif clargs.strg:
        sma.singleStrategy(clargs.price.title(), clargs.period, clargs.candlesexp, clargs.inv)



