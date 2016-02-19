#sys,os was imported to convert the Absolute Path to Relative Grade
import datetime, sys
import os

#Import Numpy and Pandas
import numpy as np
import pandas as pd

#Import URL Reader Library
import urllib2

#Import Random for Random Sampling
import random

#Import Math and CSV
import math
import csv


#ReadMarketCap File which is the Market Capital and Ticker List
#We don't need the IPO date so we use usecols = (0,1)

def readMarketUniverseFile(file_name, headerRow=0, tickerKey='mktshare', encodingType='gb18030'):
    marketCapUniverse = pd.read_csv(file_name,usecols = (0,1),header=headerRow, encoding=encodingType)
    return marketCapUniverse


#Get Historic Data from Yahoo
#Get CSV from Given Repository
#Calculate all the MScore Variables - Returns, Momentum, Volatility, Reversal
#Merge All this Data in a single DataFrame - DataDictionary
#Try out various Scenarios and Economic Intuition to Judge which Coefficients
#Fit the Scenarios Correctly, coming up with an optimized Linear Programming Problem
#Solution to Fit the Case    

# In Sample for January 2011 - November 2014

# Run the same for out of sample November 2014 - July 2015
# Change the Date Parameters

def get_historic_data(ticker,mktshare,start_date=(2011,1,4),end_date=(2014,11,31)):

    # Construct the Yahoo URL with the correct integer query parameters
    # for start and end dates. Note that some parameters are zero-based!
    yahoo_url = "http://ichart.finance.yahoo.com/table.csv?s=%s&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s" % \
        (ticker, start_date[1] - 1, start_date[2], start_date[0], end_date[1] - 1, end_date[2], end_date[0])
    # Try connecting to Yahoo Finance and obtaining the data
    # On failure, print an error message
    try:
        yf_data = urllib2.urlopen(yahoo_url).readlines()
        # Create the (temporary) Python data structures to store
        # the historical data
        
        date_list = []
        hist_data = [[] for i in range(6)]
        
        # Format and copy the raw text data into datetime objects
        # and floating point values (still in native Python lists)
        for day in yf_data[1:]:  # Avoid the header line in the CSV
            headers = day.rstrip().split(',')
            date_list.append(datetime.datetime.strptime(headers[0],'%Y-%m-%d'))
            for i, header in enumerate(headers[1:]):
                hist_data[i].append(float(header))

        # Create a Python dictionary of the lists and then use that to
        # form a sorted Pandas DataFrame of the historical data
        hist_data = dict(zip(['open', 'high', 'low', 'close', 'volume', 'adj_close'], hist_data))
        masterDataFrame = pd.DataFrame(hist_data, index=pd.Index(date_list)).sort_index()

       
        #Append Market Share to the Dictionary Data
        masterDataFrame['Market Share']= mktshare
       
        #Append Market Share to the Dictionary Data
        masterDataFrame['Market Cap'] = masterDataFrame['Market Share'] * masterDataFrame['adj_close']
        
        #Append StockTicker to Dictionary Data        
        masterDataFrame['Stock'] = ticker
        
        #Append Moving Returns to the Dictionary Data
        returns   = (masterDataFrame['adj_close']-masterDataFrame['adj_close'].shift(1))/masterDataFrame['adj_close'].shift(1)
        
        #Returns
        log_ret   = np.log((masterDataFrame['adj_close']))-np.log((masterDataFrame['adj_close'].shift(1)))
        
        #Momentum
        Momentum  = np.log(masterDataFrame['adj_close'].shift(1)) - np.log(masterDataFrame['adj_close'].shift(5))
        
        #Reversal
        reversal  = np.log(masterDataFrame['adj_close'].shift(20)) - np.log(masterDataFrame['adj_close'].shift(1))
         
        #Volatility
        Volatility       = np.log(pd.rolling_std(log_ret.shift(1),15))
            
        
        #Append all the above calculated Variables to the Master DataFrame masterDataFrame
        masterDataFrame['Returns']=returns
        masterDataFrame['Momentum']= Momentum
        masterDataFrame['Volatility']=Volatility
        masterDataFrame['Reversal'] = reversal

        try:
            headerRow=0

            #Check if the Stock is SZ             
            
            accountingRatios = pd.read_csv('./szss/sz/%s_factor.csv' %ticker,header=headerRow, encoding='gb18030')
            accountingRatios = accountingRatios.set_index('Date')
            
            #Merge the two DataSets
            masterDataFrame = masterDataFrame.merge(accountingRatios,left_index=True,right_index=True)
            
        except Exception, e:
            try:
                #Check if the Stock is SS

                headerRow=0
                accountingRatios = pd.read_csv('./szss/ss/%s_factor.csv' %ticker,header=headerRow, encoding='gb18030')
                accountingRatios = accountingRatios.set_index('Date')                

                #Merge the two DataSets               
                masterDataFrame = masterDataFrame.merge(accountingRatios,left_index=True,right_index=True)
                
            except Exception, e:
                print "CSV File NOT Found"
                pass
            
        #If taking Equal Weight
        #Alternative Approach
        #weight1 =(1/7)
        #weight2 =(1/7)
        #weight3 =(1/7)
        #weight4 =(1/7)
        #weight5 =(1/7)
        #weight6 =(1/7)
        #weight7 =(1/7)  
        
        MScore = 0.1 * masterDataFrame['PB'] + 0.05 * masterDataFrame['PCF'] + 0.1 * masterDataFrame['PE'] + 0.1 * masterDataFrame['PS'] + 0.3 * masterDataFrame['Momentum'] + 0.3 * masterDataFrame['Reversal'] + 0.35 * masterDataFrame['Volatility']
      
        masterDataFrame['MScore'] = MScore
        
        return masterDataFrame
        
#Yahoo Finance API Request Over Load, or Stock Not Found Error
    except Exception, e:
            print "Could not download Yahoo data: %s" % e
            pass



#Selet Stocks from the Universe with Top 100 MScore
def selectTopEquities(datadictionary, i, value):
    
    #Create a DataFrame with the given columns Ticker, MScore, Close, Shares
    MScore_DF = pd.DataFrame(columns = ['Ticker','MScore','Close','Shares'])
    MScore_DF['Ticker']= datadictionary.keys()
    #Market Volume is mostly more than 1Billion for all the stocks hence the criterion is dissatisfoed
    
    #Iterate over the DataDic
    j= 0
    for ticker in datadictionary.keys():
        #Check if the Values for MScore, Close ,Shares exists for the given Stock
        try:
            MScore_DF ['MScore'][j] = datadictionary[ticker]['MScore'][i]
            MScore_DF ['Close'][j]  = datadictionary[ticker]['close'][i]
            MScore_DF ['Shares'][j] = value/datadictionary[ticker]['close'][i]    
        except:
            MScore_DF ['MScore'][j] = 0
            MScore_DF ['Close'][j]  = 0
            MScore_DF ['Shares'][j] = 0
        j = j + 1
    
    MScore_DF = MScore_DF.sort('MScore', ascending=False)
    
    MScore_TopEquities = MScore_DF[0:100]

    return MScore_TopEquities



#At every Buy Sell, Calculate the new Portfolio Value    
def calculateNewPortVal(previousPortfolioList, datadictionary, i,frequency):
    
    sumFactor=0
    k=0
    
    #Iterate over the Ticker
    for ticker in previousPortfolioList['Ticker']:
        try:
            sumFactor = sumFactor + (datadictionary[ticker]['close'][i] * previousPortfolioList['Shares'][k])
        except:
            sumFactor = sumFactor + (datadictionary[ticker]['close'][i-frequency] * previousPortfolioList['Shares'][k])
        k= k + 1
        
    return sumFactor        
 
#Sell Equities
def sellEquities(initialPortfolio, equitiesToBeSold, datadictionary, i,frequency):
    
    #Cash Flow Profits
    gain = 0    
    k =0 
    
    initialPortfolio = initialPortfolio.reset_index(drop=True)
    
    for ticker in initialPortfolio['Ticker']:
        if ticker in equitiesToBeSold:
            try:
                currentPrice = datadictionary[ticker]['close'][i]
            except:
                currentPrice = datadictionary[ticker]['close'][i-frequency]
            gain = gain + (currentPrice * initialPortfolio['Shares'][k])
            
            #Delete where No Ticker Exists
            initialPortfolio = initialPortfolio[initialPortfolio['Ticker'] != ticker]
        k = k + 1
    
    return gain, initialPortfolio
    
#Buy Equities
def buyEquities(initialPortfolio, equitiesToBeBought, datadictionary, i, portfolioFactor):
    #Cash Flow Profits
    loss = 0    
    
    initialPortfolio = initialPortfolio.reset_index(drop=True)
    for ticker in equitiesToBeBought:
        
        #Calculate all the Current Values
        currentPrice = datadictionary[ticker]['close'][i]
        shares = portfolioFactor/currentPrice
        loss = loss + portfolioFactor
        temp = [ticker,currentPrice,shares]
        
        #Assign to the End
        initialPortfolio.loc[len(initialPortfolio)] = temp
        
    return loss, initialPortfolio

#Rebalance
def rebalance(initialPortfolio, datadictionary, i, portfolioFactor):
    
    initialPortfolio = initialPortfolio.reset_index(drop= True)
    j=0    
    lossInRebalance = 0
    gainInRebalance = 0
    
    for ticker in initialPortfolio['Ticker']:
       currentPrice = initialPortfolio['Close'][j]
       oldShares = initialPortfolio['Shares'][j]
       
       new_shares = portfolioFactor/currentPrice
       diff = new_shares - oldShares
       
       if diff > 0:
           lossInRebalance = lossInRebalance + diff *currentPrice
           temp = [ticker, currentPrice, new_shares]
           initialPortfolio.loc[j] = temp

       if diff < 0:
           gainInRebalance = gainInRebalance + abs(diff)*currentPrice
           temp = [ticker, currentPrice, new_shares]
           initialPortfolio.loc[j] = temp
           
       else: pass
       j=j+1
   
    return lossInRebalance, gainInRebalance, initialPortfolio


#Output Generator
def solutionMaker(portfolioValueCurrent,transaction,profit,i,frequency):
    csvlist = []
    header = ["Time","Portfolio Value", "Transaction Value", "Sharpe", "Profit/Loss", "One-Period Return", "Moving Average"]
    csvlist.append(header)
    j=0
    
    periodicreturns = []
    returns=0
    movingavg=0
    sharpe =0
    md = 0
    highestPortVal = portfolioValueCurrent[0]
    
    for m in portfolioValueCurrent:
       #If at the First Scenario No RATIOS are Available
        if j!=0:
            returns=(m-portfolioValueCurrent[j-1])/portfolioValueCurrent[j-1]
            periodicreturns.append(returns)
            standard = np.std(periodicreturns)
            movingavg = np.mean(periodicreturns)
            sharpe = (np.mean(periodicreturns)-0.03)/standard
        else:
            periodicreturns.append(returns)
            pass
        if m>highestPortVal:
            highestPortVal=m
            
        dd = (highestPortVal-m)/highestPortVal
        if dd>md:
            md=dd
        #Put it in the CSV Row
        row = [i,portfolioValueCurrent[j],transaction[j],sharpe,profit[j],returns, movingavg]
        
        #Increase the Frequency        
        i = i + frequency
        
        #Append the whole Row in CSV
        csvlist.append(row)
        
        j=j+1
    
    #Append the Maximum Dropdown --- Minimum Value
    csvlist.append(["Maximum Drawdown:",md])
    return csvlist
        

#Main Function
if __name__ == '__main__':
   

   marketkey ='mktshare'
   ticker_file = './ticker_universe.csv'
   encodingType= 'gb18030'
   headerRow = 0
   
   #Retrieve the Market List and Ticker List.
   marketlist =  readMarketUniverseFile(ticker_file, headerRow, marketkey, encodingType)
   
   #Iterate over the Market List DataFrame
   for i in range(len(marketlist)):
       
       temp = marketlist["ticker"][i]

       if "SH" in temp:    
           #Replace SH by SS
           marketlist["ticker"][i] = marketlist["ticker"][i].replace("SH","SS") 

       else:
   
           pass

   for i in range(len(marketlist)):
       marketlist["mktshare"][i] = float(marketlist["mktshare"][i].replace(",",""))

   # Number of Stocks in the Universe
   subsetData = random.sample(range(2784), 1000)
   datadictionary={}
   
   for i in subsetData:
      
       try:
            pDataFrame = get_historic_data(marketlist['ticker'][i],marketlist['mktshare'][i])
            datadictionary[marketlist['ticker'][i]] = pDataFrame
       except:
            pass

   #First Iteration from 0-19 reduced as it generates Nan and Null values for most of the variables.   
   i=20
   firstiteratei = i
   #Frequency of trading and rebalancing  every 20 days
   frequency = 20
   
   #Initial Portfolio Value  - $10000000 which can be converted into RMB (Chinese Currency)
   portfolioValue = 10000000
   
   #Number of Sample to be Chosen
   k = 100
   
   selectTopMScoreEquities = selectTopEquities(datadictionary, i, (portfolioValue/k))

   #Select Top100 Equities with Highest MScore   
   initialPortfolio = selectTopMScoreEquities
   initialPortfolio = initialPortfolio.drop('MScore',1)
   
   #initialPortfolio = initialPortfolio.drop('MScore',1)
   portfolioValuelist =[]
   portfolioValuelist.append(portfolioValue)
   
   #Maintain Proit Loss List
   profitlist = []
   profitlist.append(-portfolioValue-portfolioValue*0.001)
      
   
   #Transaction Cost List
   transactionValue = []
   transactionValue.append(portfolioValue*0.001)
    

   # Average Run time of the stocks in the last 4 years - > 250 Working Days * 4 years = 1000 Days
   
   while i <1001:
    
       #Assign Current Portfolio as Old Portfolio       
       oldportfolioValue = portfolioValue
       
       #Rebalance Every 20 Days
       i=i+20
       
       #Drop Index and Reinitiate the List with the Previous List.
       previousPortfolioList = initialPortfolio
       previousPortfolioList = previousPortfolioList.reset_index(drop=True)
       
       #Calculate the new Portfolio Values
       sumFactor = calculateNewPortVal(previousPortfolioList, datadictionary, i,frequency)
       portfolioValue=sumFactor
       
       selectTopMScoreEquities = selectTopEquities(datadictionary, i,(portfolioValue/k))

       #Start Rebalancing
       
       #Join Operation to Slice the Data from the Two Data Frames to get the Equities to Sell
       equitiesToBeSold = list(set(previousPortfolioList['Ticker']) - set(selectTopMScoreEquities['Ticker']))
       
       #Match the Portfolio and Sell the Equities non existent in the current scenario 
       #And existent in the past scenario       
       gain, initialPortfolio = sellEquities(initialPortfolio, equitiesToBeSold, datadictionary, i,frequency)
    
       #Join Operation to Slice the Data from the Two Data Frames to get the Equities to Buy
       equitiesToBeBought = list(set(selectTopMScoreEquities['Ticker']) - set(previousPortfolioList['Ticker']))
       
       #Match the Portfolio and Buy the Equities non existent in the past scenario and 
       #existent in the past scenario         
       
       loss, initialPortfolio = buyEquities(initialPortfolio, equitiesToBeBought, datadictionary, i, (portfolioValue/k))
       
       
       #Rebalance the Holding Stocks
       #Equities that exists in both the DataSets
       lossInRebalance, gainInRebalance, initialPortfolio = rebalance(initialPortfolio, datadictionary, i, (portfolioValue/k))
      

       #New Portfolio Value      
       portfolioValuelist.append(portfolioValue)
       
       #Calculate the Total Transaction Cost
       transactioncost = (abs(gain)+abs(loss)+abs(lossInRebalance)+abs(gainInRebalance))*0.001
       transactionValue.append(transactioncost)

       #Update the Profit Lists
       profit = portfolioValue-oldportfolioValue-transactioncost
       profitlist.append(profit)


   #Write all the Output Metrics to the CSV Generator and Output the Performance Measures and
   #BackTesting Metrics
   dataSet = solutionMaker(portfolioValuelist,transactionValue,profitlist,firstiteratei,frequency)
   with open('results.csv', 'wb') as filecsv:
       writeToFile = csv.writer(filecsv, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
       for row in dataSet:
           writeToFile.writerow(row)
   filecsv.close()  