#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 30 08:23:54 2018

@author: jstiven01
"""

import pandas as pd
import numpy as np

#######################################
##### CONSTANTS########################
#Constant pips
ctePips =10000
#Constant Indicator
nameIndic = "MA"
#Constant Filename
filename = "EURUSDDaily.csv"
#Constant candles expiration
candlesExpired = 3
#Constant periods indicator
indPeriod = 7
#######################################

class SMAPatterns():

    def __init__(self):
        '''Initializing Attributes'''

        self.dfprices = pd.read_csv("../data/"+filename, header=None)
        # Naming Columns
        self.dfprices.columns = ["Date", "Time", "Open", "High", "Low", "Close", "Volume"]

        self.dfresults = pd.DataFrame()
        self.dfperform = pd.DataFrame
        self.Expectancy = []
        self.Accuracy = []
        self.PLTotal = []
        self.TotalTrades = []
        return

    def pipCandles(self, candlesExp):
        """Computing the Pips for every candle in both ways: LONG and SHORT """

        for i in range(0, candlesExp):
            self.dfprices['PipsLong{}'.format(i)] = (self.dfprices["Close"].shift(-i) - self.dfprices["Open"]) * ctePips
            self.dfprices['PipsShort{}'.format(i)] = (self.dfprices["Open"] - self.dfprices["Close"].shift(-i)) * ctePips
        return

    def smaPeriodPrice(self, price, period):
        """Calculating SMA with price (open, close, high, low) and period"""

        for i in range(2, period):
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
            self.dfprices.loc[FilterLong, 'ENTRY' + nameIndic + price+'{}'.format(i)] = "LARGO"
            self.dfprices.loc[FilterShort, 'ENTRY' + nameIndic + price+'{}'.format(i)] = "CORTO"
        #print(self.dfprices)
        
        return

    def tradeStrategies(self, price, period, candlesExp):
        """Consolidating all Strategies with different sma and expiration"""

        # Creating Dataframe with consolidated results
        self.dfresults = pd.DataFrame(index=(pd.to_datetime(self.dfprices["Date"]).dt.year).drop_duplicates())

        # Consolidating Trade Strategy for every candle (k) and every period (i)
        for k in range(0, candlesExp):
            for i in range(2, period):

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

                # Grouping by Years
                Trades["Year"] = (pd.to_datetime(Trades["Date"]).dt.year)
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
        dftotal.to_csv("SMAResults"+price+".csv", sep=',')
        print("STRATEGIES BEST PERFORMANCES")
        print(self.dfperform.idxmax(1))
        print("STRATEGIES WORST PERFORMANCES")
        print(self.dfperform.idxmin(1))
        return

    def singleStrategy(self, price, period, ):
        return


if __name__ == "__main__":
    sma = SMAPatterns()
    sma.pipCandles(candlesExpired)
    sma.smaPeriodPrice("Open",indPeriod)
    sma.tradeStrategies("Open",indPeriod,candlesExpired)
    sma.performanceStrategies()
    sma.writeResults("Open")

