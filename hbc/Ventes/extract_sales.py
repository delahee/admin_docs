import csv
import json
import argparse
from os import listdir
from os.path import isfile, join
import os
from datetime import datetime
import pycountry
import locale
import sys
locale.setlocale(locale.LC_ALL, 'en_US')


global sum_euro; 
global sum_euro_fixed_fee; 
global sum_usd; 

global nbUnits;
global nbFixedFee;

global do_pid; 
global do_steam; 
global do_itch;

do_pid=True;
do_steam=True;
do_itch=True;

sum_euro_fixed_fee = 0.0
sum_euro = 0.0;
sum_usd = 0.0;

nbFixedFee = 0
nbUnits = 0;

global fixed_fee_ops
fixed_fee_ops = []

country = "China"
start_year = "31/12/2015"
end_year = "31/12/2020"

parser = argparse.ArgumentParser()

parser.add_argument('-i','--input')
parser.add_argument('-itch-only',action="store_true")
parser.add_argument('-pid-only',action="store_true")
parser.add_argument('-steam-only',action="store_true")

for arg in sys.argv:
	
	if arg == "-itch-only":
		do_steam=False
		do_pid=False
	elif arg == "-pid-only":
		do_steam=False
		do_itch=False
	elif arg == "-steam-only":
		do_itch=False
		do_pid=False

args = parser.parse_args()

if( args.input != None):
	with open(args.input,"r") as jInputFile:
		js = json.load(jInputFile)
		print(js)
		if( js["country"]!= None):
			country = js["country"];
		
		if (js["start"] != None):
			start_year = js["start"];
		
		if (js["end"] != None):
			end_year = js["end"];

date_start = datetime.strptime(start_year,"%d/%m/%Y");
date_end = datetime.strptime(end_year,"%d/%m/%Y");

print("period start>"+date_start.strftime("d: %d m: %m y:%Y"));
print("period end>"+date_end.strftime("d: %d m: %m y:%Y"));
print("country "+country);


def parse_steam():
	global sum_euro; 
	global sum_usd; 
	global nbUnits;
	global nbFixedFee;
	steamfilepath = os.path.dirname(os.path.realpath(__file__)) + "/Steam";
	print( steamfilepath );
	onlyfiles = [("Steam/"+f) for f in listdir(steamfilepath) if isfile(join(steamfilepath, f)) and os.path.splitext(f)[1] == ".csv" and "Country" in f]
	for path in onlyfiles:
		spl = path.split("_");
		month = spl[1];
		#print( month );
		year = spl[2].split(".")[0];
		#print( year );
		filedate = datetime.strptime( month+" "+year, "%B %Y");
		#print("date>"+filedate.strftime("d: %d m: %b y:%Y"));
		if filedate < date_start:
			#print("skipped")
			continue
		if filedate > date_end:
			#print("skipped")
			continue
		print("using " + path);
		
		with open(path) as csvfile:
			reader = csv.reader(csvfile)
			next(reader);
			next(reader);
			next(reader);
			next(reader);
			for row in reader:
				if len(row):
					if( ( (row[0]==country) or (country == "*") ) and (row[1]=="Double Kick Heroes - Original Sound Track (251103)" or row[1]=="Double Kick Heroes (152600)") ):
						#print(row);
						line_usd = float(row[4]);
						line_units = int(float(row[3]));
						sum_usd += line_usd;
						nbUnits += line_units;
						#print("Found "+str(line_units)+" units ( $"+str(line_usd)+") to add");
				
if do_steam:				
	parse_steam();

def parse_itch():
	global sum_euro; 
	global sum_usd; 
	global nbUnits;
	global nbFixedFee;
	itchfilepath = os.path.dirname(os.path.realpath(__file__)) + "/Itch/purchases.csv";
	print( "Using "+itchfilepath );
	with open(itchfilepath) as csvfile:
		reader = csv.reader(csvfile)
		line_desc = next(reader);
		
		currency_index = line_desc.index('currency');
		country_code_index = line_desc.index('country_code');
		date_index = line_desc.index('created_at');
		payout_index = line_desc.index('payout');
		amount_delivered = line_desc.index('amount_delivered');
		amount = line_desc.index('amount');
		
		for row in reader:
			if len(row):
				if( row[1]=="Double Kick Heroes" ):
					localDate = datetime.strptime(row[date_index],"%Y-%m-%d %H:%M:%S %Z");
					if localDate < date_start: 	
						continue
					if localDate > date_end:	
						continue
					line_usd = float(row[amount]);
					line_eur = float(row[amount]);
					currency = row[currency_index];
					country_code = row[country_code_index];
					localCountry = pycountry.countries.get(alpha_2=country_code)
					if country != '*':
						if localCountry != country :
							continue
					if( currency == "USD" ):
						sum_usd += line_usd;
					elif( currency == "EUR" ):
						sum_euro += line_eur;
					else :
						print("unknown currency "+currency)
					line_units = 1;
					nbUnits += line_units;
					#print("Found "+str(line_units)+" units ( "+str(line_usd)+" "+currency+" ) to add");
				

if do_itch :
	parse_itch();

def threeToMonth(lit):
	monthNum = -1  
	switcher = {
		"JAN":0,  
		"FEB":1,  
		"MAR":2,  
		"APR":3,  
		"MAY":4,  
		"JUN":5,  
		"JUL":6,  
		"AUG":7,  
		"SEP":8,  
		"OCT":9,  
		"NOV":10, 
		"DEC":11, 
	}
	return switcher.get(lit);

def parse_pid():
	locale.setlocale(locale.LC_ALL, 'fr_FR')
	
	global sum_euro; 
	global sum_usd; 
	global sum_euro_fixed_fee; 
	global nbUnits;
	global nbFixedFee;
	global fixed_fee_ops
	pidfilepath = os.path.dirname(os.path.realpath(__file__)) + "/Plugin";
	print( pidfilepath );
	onlyfiles = [("Plugin/"+f) for f in listdir(pidfilepath) if isfile(join(pidfilepath, f)) and os.path.splitext(f)[1] == ".csv"]
	onlyfiles.sort()
	for path in onlyfiles:
		print("using " + path);
		dateSegment = path.split("invoice-claim-")[1].split(".csv")[0];
		monthNum = threeToMonth( dateSegment.split("-")[1] );
		localDate = datetime.strptime( dateSegment.split("-")[0] + " "+ str(monthNum+1),"%Y %m");
		if localDate < date_start: 	
			#print("skipped"); 
			continue
		if localDate > date_end:	
			#print("skipped"); 
			continue
		with open(path) as csvfile:
			reader = csv.reader(csvfile)
			line_desc = next(reader);
			gross_idx = line_desc.index('Total Purchase Price');
			soldin_idx = line_desc.index('Sold in');
			channel_idx = line_desc.index('Channel');
			
			#print(soldin_idx);
			qty_idx = line_desc.index('Qty');
			for row in reader:
				if len(row):
					if( row[0]=="Double Kick Heroes" ):
						strQty = row[qty_idx];
						if( (strQty != "-") or ( not row[channel_idx].startswith("Microsoft") ) ): 
							gross = locale.atof(row[gross_idx]);
							net = gross * 0.8;
							
							if(strQty == '-'):
								qty = 1
							else:
								qty = int(locale.atof(strQty));
						
							lcountry=row[channel_idx].split("(")[1];
							if( country ):
								lcountry=lcountry.split(")")[0];
							if( country != '*' and country != lcountry ):
								continue
								
							line_units=qty;
							line_eur=net;
							nbUnits += line_units;
							sum_euro+=gross;
							lcountry=row[channel_idx].split('(')[1];							
							#print("Found "+str(line_units)+" units "+str(line_eur)+"€ to add");
						else:
							gross = locale.atof(row[gross_idx]);
							lcountry=row[channel_idx].split("(")[1];
							if( country ):
								lcountry=lcountry.split(")")[0];
							if( country != '*' and country != lcountry ):
								continue
							sum_euro_fixed_fee += gross;
							nbFixedFee += 1
							fixed_fee_ops.append( row );
					if( row[0]=="Sales Total"):
						strQty = row[qty_idx];
						if( strQty == "-" ): strQty = "1";
						print("PID MONTHLY TOTAL UNITS "+strQty)
				
	locale.setlocale(locale.LC_ALL, 'en_US')	
	
if do_pid:
	print("inspecting PID sales")
	parse_pid();

print("\nDOUBLE KICK HEROES\n");
if( country == "*"):
	print("Overall Net Sales");
else :
	print("Overall Net Sales for territory :"+country+"");
print("Period :"+date_start.strftime("%c") +" to "+date_end.strftime("%c")+"\nUSD : "+ locale.currency(sum_usd,True)+ "\n GROSS EUR "+str(sum_euro)+"€ \nUnits: "+str(nbUnits));
if( nbFixedFee>0):
	print("Fixed fee ops")
	print("nb:"+str(nbFixedFee)+" gross:"+str(sum_euro_fixed_fee));
for r in fixed_fee_ops:
	print("Names : "+str(r[2])+" gross:"+str(r[5]) )
	
			