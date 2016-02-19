This a MultiFactor Trading Strategy implemented in Python using Pandas and Numpy.

Functions,

get_historic_data(ticker, start_date, end_date)
-----------------------------------------------

Input - Ticker Name,
		Start Date,
		End Date


Get all the Data from 
- Yahoo Finance API
- CSV's given, SS,SZ Files
- Computed Metrics
- Moving Metrics

- Compute the MScore for every Equity on the given day of Trading

Merge into a Single DataFrame DataDictionary which it returns.


selectTopEquities(datadictionary, i, value)
--------------------------------------------
Input - DataDictionary, 
		Time Scenario, 
		Value

Subsets the Data depending on the MScores and sorts the Top 100 Data

Returns Top 100 Equities on basis of MScore Values.


calculateNewPortVal(previousPortfolioList, datadictionary, i,frequency)
------------------------------------------------------------------------
Input - PreviousPortfolioList,
		DataDictionary,
		Time Scenario,
		Frequency of Trading

-Calculate the new value of the old pprtfolio

Returns the new value of the old portfolio

sellEquities(initialPortfolio, equitiesToBeSold, datadictionary, i,frequency)
-----------------------------------------------------------------------------
Input - Initial Portfolio,
		Equities To Be Sold,
		DataDictionary,
		Time Scenario,
		Frequency

- Calculate the Equities to be sold and the gain from them

Returns the Gain and the new portfolio

buyEquities(initialPortfolio, equitiesToBeBought, datadictionary, i, portfolioFactor)
---------------------------------------------------------------------
Input - Initial Portfolio,
		EquitiesToBuy,
		DataDictionary,
		TimeScenario,
		PortfolioFactor

- Calculae the Equities to Be Bought and loss from them.

Returns the Portfolio and loss from the data.

rebalance(initialPortfolio, datadictionary, i, portfolioFactor)
---------------------------------------------------------------
Input - initialPortfolio, 
		DataDictionary,
		Time Scenario,
		PortfolioFactor

- Depending on whether to rebalance or not take decisions on weight of the
  holding portfolio whether to buyor sell.

- Returns the loss in Rebalance, Gain in Rebalance, and the Updated Portfolio

solutionMaker(portfolioValueCurrent,transaction,profit,i,frequency)
--------------------------------------------------------------------
Input - portfolio Current Value,
		Transaction Costs,
		Profits,
		Time Scenario,
		Frequency

- Prepare the input for the CSV Writer

Returns the csvlist to be written to the CSV in he main file
