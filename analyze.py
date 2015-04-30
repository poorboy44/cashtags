## this script merges cashtag counts with stock prices and produces scatterplots

import pandas as pd
from yahoo_finance import Share

df=pd.DataFrame()
with open('out1.txt') as f:
	line_num=0
	for line in f:
		line_num+=1
		#if line_num>10:
		#	break
		try:
			raw=eval(line) #list
			ticker = raw[0]
			counts = raw[1]["results"] #list of dicts
			raw_df=pd.DataFrame(counts)
			raw_df['ticker']=ticker[1:].upper()
			df=df.append(raw_df)
		except:
			continue

df['dt']=pd.to_datetime(df['timePeriod'], '%y%m%d0000')
df['ticker']
df=df[['ticker', 'dt', 'count']]


cashtags = df['ticker'].unique()
min_date=str(df['dt'].min().date())
max_date=str(df['dt'].max().date())

all_stock=pd.DataFrame()
for i in cashtags:
	try:
		stock_data=Share(i).get_historical(str(min_date), str(max_date))
		dt_price = [{'dt':pd.to_datetime(i['Date']),'ticker':i['Symbol'],'price': i['Close']} for i in stock_data]
		raw_stock = pd.DataFrame(dt_price)
		all_stock=all_stock.append(raw_stock)
	except:
		continue

all_stock.to_csv('stock_prices.csv')

## merge counts and prices
merged_data = pd.merge(all_stock, df, on=['dt', 'ticker'], how='outer')
merged_data=merged_data.sort(['ticker', 'dt'])
merged_data.to_csv('tweet_volume_and_stock_prices.csv')

## calc returns and merge back on
#if merged_data:
merged_data=pd.read_table('tweet_volume_and_stock_prices.csv', sep=',')
md1=merged_data.dropna()
md1=md1.drop('Unnamed: 0', 1)
#md1=md1.set_index(['ticker', 'dt'])
logret = lambda x: np.log(x/x.shift(1))
grouped = md1.groupby(['ticker']).transform(logret) #returns a DF
grouped.columns=['logpriceret', 'logcountret'] 
md2=pd.concat([md1, grouped], axis=1) #merge back together
md3 = md2.replace([np.inf, -np.inf], np.nan).dropna()
md3 = md3[ (md3['logpriceret']<3) & (md3['logpriceret']>-3)  & (md3['logcountret']<3) & (md3['logcountret']>-3)  ]



#overall scatter plot
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
def plotit(md3, *args):
	if len([args]) == 0:
		ticker='all'
	elif len([args])==1:
		md3=md3[md3.ticker.isin(args)]
	plt.scatter(md3['logcountret'], md3['logpriceret'])
	plt.xlabel('logcountret')
	plt.ylabel('logpriceret')
	plt.savefig('../public_html/' + ticker + '.pdf') 
	plt.close()

plotit(md3, "all_data")
plotit(md3, "TWTR")
plotit(md3, "AAPL")
plotit(md3, "GOOG")
plotit(md3, "AMZN")
plotit(md3, "FB")
plotit(md3, "LNKD")

