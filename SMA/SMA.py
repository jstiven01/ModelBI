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
candlesExpired = 3
#Constant periods indicator
indPeriod = 7
#Constants round Decimal
rounddec=5
#######################################3

#Read CSV
dfprices = pd.read_csv("../data/EURUSDDaily.csv", header = None)
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
   dfprices[nameIndic+'Open{}'.format(i)] = dfprices[nameIndic+'Open{}'.format(i)].round(rounddec)
   
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


#Creating Dataframe with consolidated results
dfresults = pd.DataFrame(index =(pd.to_datetime(dfprices["Date"]).dt.year).drop_duplicates())
Expectancy= []
Accuracy = []
PLTotal = []
PositiveYears = []
#Consolidating Trade Strategy
for k in range(0,candlesExpired):
    for i in range(2,indPeriod):
        FiltLongEntries = (dfprices['ENTRY'+nameIndic+'Open{}'.format(i)]=="LARGO")
        FiltShortEntries = (dfprices['ENTRY'+nameIndic+'Open{}'.format(i)]=="CORTO")
        TradesLong = dfprices.loc[FiltLongEntries,("Date","Time",'PipsLong{}'.format(k))]
        TradesLong.rename(columns ={'PipsLong{}'.format(k):'PipsCandle{}'.format(k)}, inplace = True)
        TradesShort = dfprices.loc[FiltShortEntries,("Date","Time",'PipsShort{}'.format(k))]
        TradesShort.rename(columns ={'PipsShort{}'.format(k):'PipsCandle{}'.format(k)}, inplace = True)
        Trades = pd.concat([TradesLong,TradesShort])
        Trades.sort_index(inplace=True)
    
        #Grouping by Years
        Trades["Year"]= (pd.to_datetime(Trades["Date"]).dt.year)
        dfresults[nameIndic+'Open{}'.format(i)+'Cand{}'.format(k)] = \
        (Trades.groupby("Year")['PipsCandle{}'.format(k)].agg('sum')).values
        
        #Performance
        Expectancy.append(Trades['PipsCandle{}'.format(k)].mean())
        PLTotal.append(Trades['PipsCandle{}'.format(k)].sum())
        PosTrades = Trades[Trades['PipsCandle{}'.format(k)]>0].shape[0]
        NegTrades = Trades[Trades['PipsCandle{}'.format(k)]<0].shape[0]
        Accuracy.append(PosTrades/(PosTrades+NegTrades))


dfPLTotal = pd.DataFrame(PLTotal)
dfAcc = pd.DataFrame(Accuracy)
dfExp =  pd.DataFrame(Expectancy)
dfPosYear = pd.DataFrame((dfresults[dfresults>0].count()).values)
dfperform = pd.concat([dfPLTotal, dfAcc, dfExp, dfPosYear], axis= 1)
dfperform = dfperform.T
dfperform.columns = dfresults.columns
indexnames = ["P/LTotal", "Accuracy", "Expectancy", "PosYears"]
dfperform.index = indexnames

#Best performance
dfperform.idxmax(1)

#Coding for a single Strategy
FiltLongEntries = (dfprices['ENTRY'+nameIndic+'Open{}'.format(2)]=="LARGO")
FiltShortEntries = (dfprices['ENTRY'+nameIndic+'Open{}'.format(2)]=="CORTO")
TradesLong = dfprices.loc[FiltLongEntries,("Date","Time",'PipsLong{}'.format(0))]
TradesLong.rename(columns ={'PipsLong{}'.format(0):'PipsCandle{}'.format(0)}, inplace = True)
TradesShort = dfprices.loc[FiltShortEntries,("Date","Time",'PipsShort{}'.format(0))]
TradesShort.rename(columns ={'PipsShort{}'.format(0):'PipsCandle{}'.format(0)}, inplace = True)
Trades = pd.concat([TradesLong,TradesShort])
Trades.sort_index(inplace=True)

Trades["Year"]= (pd.to_datetime(Trades["Date"]).dt.year)


TradesLong["Year"]= (pd.to_datetime(TradesLong["Date"]).dt.year)
TradesLong[TradesLong["Year"]==2014]["PipsCandle0"].sum()

TradesShort["Year"]= (pd.to_datetime(TradesShort["Date"]).dt.year)
TradesShort[TradesShort["Year"]==2014]["PipsCandle0"].sum()

Trades["Date"].count()
