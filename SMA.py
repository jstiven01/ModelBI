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
#Constant candles expiration
candlesExpired = 15
#Constant periods indicator
indPeriod = 10
#######################################3

#Read CSV
dfprices = pd.read_csv("EURUSDDaily.csv", header = None)
#Naming Columns
dfprices.columns = ["Date", "Time", "Open", "High", "Low", "Close", "Volume"]

#Computing Pips for every candle
for i in range(0,candlesExpired):
   dfprices['PipsLong{}'.format(i)] = (dfprices["Close"].shift(-i)-dfprices["Open"])*ctePips
   dfprices['PipsShort{}'.format(i)] = (dfprices["Open"]-dfprices["Close"].shift(-i))*ctePips

################################
#Computing mean with OPEN prices
for i in range(2,indPeriod):
    #Rolling create windows/subsets of prices and computes the mean of subset
   dfprices[nameIndic+'Open{}'.format(i)] = dfprices["Open"].rolling(window=i).mean()
   
   #Creating column of Entries
   dfprices['ENTRY'+nameIndic+'Open{}'.format(i)] = "NO ENTRY"
   
   #Filter to identify the LONG Entries
   FilterLong = (dfprices["Close"].shift(2) < dfprices[nameIndic+'Open{}'.format(i)].shift(2)) \
   & (dfprices["Close"].shift(1) > dfprices[nameIndic+'Open{}'.format(i)].shift(1))
   
   #Filter to identify the SHORT Entries
   FilterShort = (dfprices["Close"].shift(2) > dfprices[nameIndic+'Open{}'.format(i)].shift(2)) \
   & (dfprices["Close"].shift(1) < dfprices[nameIndic+'Open{}'.format(i)].shift(1))
   
   #Adding Entries to column Entry
   dfprices.loc[FilterLong,'ENTRY'+nameIndic+'Open{}'.format(i)] = "LARGO"
   dfprices.loc[FilterShort,'ENTRY'+nameIndic+'Open{}'.format(i)] = "CORTO"


################################
#Computing mean with HIGH prices   
for i in range(2,indPeriod):
   dfprices[nameIndic+'High{}'.format(i)] = dfprices["High"].rolling(window=i).mean()
      #Creating column of Entries
   dfprices['ENTRY'+nameIndic+'High{}'.format(i)] = "NO ENTRY"
   
   #Filter to identify the LONG Entries
   FilterLong = (dfprices["Close"].shift(2) < dfprices[nameIndic+'High{}'.format(i)].shift(2)) \
   & (dfprices["Close"].shift(1) > dfprices[nameIndic+'High{}'.format(i)].shift(1))
   
   #Filter to identify the SHORT Entries
   FilterShort = (dfprices["Close"].shift(2) > dfprices[nameIndic+'High{}'.format(i)].shift(2)) \
   & (dfprices["Close"].shift(1) < dfprices[nameIndic+'High{}'.format(i)].shift(1))
   
   #Adding Entries to column Entry
   dfprices.loc[FilterLong,'ENTRY'+nameIndic+'High{}'.format(i)] = "LARGO"
   dfprices.loc[FilterShort,'ENTRY'+nameIndic+'High{}'.format(i)] = "CORTO"


################################
#Computing mean with LOW prices
for i in range(2,indPeriod):
   dfprices[nameIndic+'Low{}'.format(i)] = dfprices["Low"].rolling(window=i).mean()
   
      #Creating column of Entries
   dfprices['ENTRY'+nameIndic+'Low{}'.format(i)] = "NO ENTRY"
   
   #Filter to identify the LONG Entries
   FilterLong = (dfprices["Close"].shift(2) < dfprices[nameIndic+'Low{}'.format(i)].shift(2)) \
   & (dfprices["Close"].shift(1) > dfprices[nameIndic+'Low{}'.format(i)].shift(1))
   
   #Filter to identify the SHORT Entries
   FilterShort = (dfprices["Close"].shift(2) > dfprices[nameIndic+'Low{}'.format(i)].shift(2)) \
   & (dfprices["Close"].shift(1) < dfprices[nameIndic+'Low{}'.format(i)].shift(1))
   
   #Adding Entries to column Entry
   dfprices.loc[FilterLong,'ENTRY'+nameIndic+'Low{}'.format(i)] = "LARGO"
   dfprices.loc[FilterShort,'ENTRY'+nameIndic+'Low{}'.format(i)] = "CORTO"


################################
#Computing mean with CLOSE prices   
for i in range(2,indPeriod):
   dfprices[nameIndic+'Close{}'.format(i)] = dfprices["Close"].rolling(window=i).mean()
      #Creating column of Entries
   dfprices['ENTRY'+nameIndic+'Close{}'.format(i)] = "NO ENTRY"
   
   #Filter to identify the LONG Entries
   FilterLong = (dfprices["Close"].shift(2) < dfprices[nameIndic+'Close{}'.format(i)].shift(2)) \
   & (dfprices["Close"].shift(1) > dfprices[nameIndic+'Close{}'.format(i)].shift(1))
   
   #Filter to identify the SHORT Entries
   FilterShort = (dfprices["Close"].shift(2) > dfprices[nameIndic+'Close{}'.format(i)].shift(2)) \
   & (dfprices["Close"].shift(1) < dfprices[nameIndic+'Close{}'.format(i)].shift(1))
   
   #Adding Entries to column Entry
   dfprices.loc[FilterLong,'ENTRY'+nameIndic+'Close{}'.format(i)] = "LARGO"
   dfprices.loc[FilterShort,'ENTRY'+nameIndic+'Close{}'.format(i)] = "CORTO"

#Consolidating Trade Strategy
FiltLongEntries = (dfprices["ENTRYMAOpen2"]=="LARGO")
FiltShortEntries = (dfprices["ENTRYMAOpen2"]=="CORTO")
TradesLong = dfprices.loc[FiltLongEntries,("Date","Time","PipsLong2")]
TradesLong.rename(columns ={"PipsLong2":"PipsCandle2"}, inplace = True)
TradesShort = dfprices.loc[FiltShortEntries,("Date","Time","PipsShort2")]
TradesShort.rename(columns ={"PipsShort2":"PipsCandle2"}, inplace = True)
Trades = pd.concat([TradesLong,TradesShort])
Trades.sort_index(inplace=True)


#Grouping by Years




