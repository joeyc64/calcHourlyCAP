#!/usr/bin/env python3

import sys, time, logging, requests
import csv
from datetime import datetime

def is_leap_year(year):
    """Determine whether a year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# loads the "H0 Standardlastkurve" used by aWattar
# creates a dictionary for timestamps with the H0 value
def readH0( year ):
    logging.info("readH0 for "+str(year) )
    h0_dict={}
    isLeap = is_leap_year(year)
    #print( isLeap) 
    with open('h0-awattar.csv') as csvdatei:
        csv_reader_object = csv.reader(csvdatei, delimiter=';')
        for row in csv_reader_object:
            skip=False
            if( not isLeap and row[0][5:7]=="02" and row[0][8:10]=="29" ):
                skip=True
            if( not skip ):
                row[0]=str(year)+row[0][4:]
                d = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
                h0=float(row[1])
                h0_dict[d]=h0
                #print( d, h0)
    return h0_dict

#gets an Array of datetime and prices
def getHourlyPrices48h(region, vat = 1):
    aPrices=[]

    logging.info("Query aWATTar for new pricing...")
    timestamp = int(time.time()/86400)*86400-3600
    # get market price from today (whole day) and future
    r = requests.get('https://api.awattar.' + str(region) + '/v1/marketdata?start=' + str(timestamp*1000)+
        "&end="+str((timestamp+3*86400)*1000))
    j = r.json()["data"]
    for i in j:
        dt = datetime.fromtimestamp(i["start_timestamp"]/1000)
        p = round(i["marketprice"] / 10 * vat ,2)   # convert from Eur/MWh to Cent/kWh plus x% VAT
        logging.info( dt.strftime("%Y-%m-%d %H = ")+str(p) )
        #print( dt.strftime("%Y-%m-%d %H = ")+str(p) )
        aPrices.append([ dt,p ])
    return aPrices

def getHourlyPricesH0(region='de'):
    region = region.lower()
    if region == 'at':
        vat = 1.2
    elif region == 'de':
        vat = 1.19
    else:
        raise ValueError('Region must be at or de')

    print("Berechnung der HOURLY-CAP Preise von aWattar." + region)
    sumPricesH0=0
    sumH0=0
    aPrices=getHourlyPrices48h(region, vat)
    priceH0_dict={}
    h0_dict=readH0( aPrices[0][0].year )
    i=0
    while i<len(aPrices) :
        price=aPrices[i]
        sumPricesH0+=price[1]*h0_dict[price[0]]
        sumH0+=h0_dict[price[0]]
        lastDay=aPrices[i][0].day
        logging.info( str(lastDay)+", sum+="+str(price[1])+"*"+str(h0_dict[price[0]]) )
        i=i+1
        #print( i, len(aPrices) )
        if i==len(aPrices) or aPrices[i][0].day!=lastDay: # last element or end of day?
            # then calc avrg.H0 price of day
            priceH0_dict[lastDay]=sumPricesH0/sumH0
            logging.info( str(lastDay)+", priceH0="+str(priceH0_dict[lastDay]) )
        if i<len(aPrices) and aPrices[i][0].day!=lastDay : # not last element, then prepare for next day
            sumPricesH0=0
            sumH0=0
            h0_dict=readH0( aPrices[i][0].year )  # recalc complete dict in case year changes
            logging.info("reset sum")
    # now create new price array with only the current and future hours
    aNewPrices=[]
    for price in aPrices:
        if price[0]>=datetime.now() or (price[0].day==datetime.now().day and price[0].hour==datetime.now().hour):
            priceDiff=price[1] - priceH0_dict[price[0].day] # "good" prices are negative
            if priceDiff>0 :
                priceDiff=0
            print( price[0].strftime("%Y-%m-%d %H = ")+str(price[1])+", "+"{:.2f}".format(priceH0_dict[price[0].day])+", "+"{:.2f}".format(priceDiff) )
            #print( price[0], price[1], priceH0_dict[price[0].day], priceDiff )
            aNewPrices.append( [price[0], price[1], priceDiff] )
    return aNewPrices


if __name__ == '__main__':
    getHourlyPricesH0('de')
