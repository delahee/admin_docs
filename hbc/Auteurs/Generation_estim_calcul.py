
import csv
import math
import hbc_sheet
from hbc_sheet import *
import json
from send_email import *

from reportlab.pdfgen import canvas

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle,LineStyle

from reportlab.platypus import Paragraph,Table, TableStyle,Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-i","--input", help="input tsv")
parser.add_argument("-o","--output", help="output folder")
parser.add_argument("-v","--verbose", help="set verbose",action='store_true')
args = parser.parse_args()

path = os.getcwd()

def readMonetaryVal(ht):
	ht = ht.replace("€", "")
	ht = ht.replace(",", ".")
	ht = ht.replace(" ", "")
	ht = ht.replace(" ", "")
	return float(ht)

def readMonetaryValI(ht):
	ht = ht.replace("€", "")
	ht = ht.replace(",", ".")
	ht = ht.replace(" ", "")
	ht = ht.replace(" ", "")
	return int(ht)


def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor

with open(args.input,encoding='utf-8') as fd:
	rd = csv.reader(fd, delimiter="\t", quotechar='"',)
	line = next(rd);
	
	steam_lic = 0
	itch_lic = 0
	pid_lic = 0
	nb_title = 58
	flat_rev = 0
	
	
	line_idx = 1
	while( line[0] != "do process"):
		if( line_idx == 7): steam_lic = readMonetaryValI(line[2])
		if( line_idx == 8): itch_lic = readMonetaryValI(line[2])
		if( line_idx == 9): pid_lic = readMonetaryValI(line[2])
		if( line_idx == 16): flat_rev = readMonetaryVal(line[2])
		line = next(rd);
		line_idx = line_idx + 1
		
	total_lic = steam_lic + pid_lic + itch_lic
	
	fline = line
	line = next(rd)
	
	idx = 0
	for e in fline:
		print(e)
		idx = idx + 1
		
	if( not os.path.exists(args.output)):
		os.mkdir(args.output)

	lm = 0.5 * cm
	while(line!=None):
		val_flat = readMonetaryVal(line[12]);
		val_units_gross = readMonetaryVal(line[7]);
		val_units_net = readMonetaryVal(line[13]);
		val_total = readMonetaryVal(line[14]);
		val_advance_unit = readMonetaryVal(line[10]);

		title = line[2]
		rights = line[15]
		entity = line[5]
		val_ppu = line[6]
		
		tr_val_units_gross = truncate(val_units_gross, 2)
		tr_val_units_net = truncate(val_units_net, 2)
		tr_val_flat = truncate(val_flat, 2)
		tr_val_total = truncate(val_total, 2)
		tr_val_advance_unit = truncate(val_advance_unit, 2)
		
		foutname = args.output + "/" + line[2] + "_" + line[5] + ".pdf"
		sheet = Sheet(foutname)
		sheet.addHbcHeader()
		
		if( line[1]=='fr'):
			sheet.makeClient("Ayant droit : <strong>"+entity+"</strong>",lm, 25*cm)
			sheet.addPara("Sortie définitive du jeu : Aout 2020",0.5*cm,24*cm)
			sheet.addPara("Période : Avril 2018 - 31 Aout 2020",0.5*cm,23.5*cm)
			sheet.addPara("Titre : "+ title,0.5*cm,23*cm)
			sheet.addPara("Date d'émission : 28 Septembre 2020", 0.5 * cm, 22.5 * cm)
			
			sheet.addTitle("<strong>Opérations</strong>",21.5*cm )
			sheet.addGrid(
				[
					["Distribution à l'unité",""],
					["Steam - Licences", str(steam_lic)+" unités"],
					["PID - Licences", str(pid_lic)+" unités"],
					["Itch - Downloads", str(itch_lic)+" unités"],
					["TOTAL",str(steam_lic+pid_lic+itch_lic)+" unités"],
					["",""],
					["Opérations en Flat Rate", ""],
					["Xbox Gamepass Partie 1", str(flat_rev)+"€ Brut Preneur"]
				], 300, 200, 2.55 * cm, 14.5 * cm)
			sheet.addTitle("<strong>Estimations</strong>", 13.5 * cm)
			sheet.addGrid(
				[
					["Revenue de la redevance à l'unité ", ""],
					["Redevance par unité ", str(val_ppu)+" €/u"],
					["Montant ", str(tr_val_units_gross)+" €"],
					["Avance courante", str(tr_val_advance_unit)+" €"],
					["A verser", str(tr_val_units_net)+" €"],
					["", ""],
					["Revenue de la redevance 'Flat Rate' ", ""],
					["A verser", str(tr_val_flat)+" €"],
					["", ""],
					["TOTAL A NOUS FACTURER", str(tr_val_flat+tr_val_units_net) + " €"],
				], 200, 200, 2.55 * cm, 5 * cm)
			
			cy = 4;
			sheet.addPara("<strong>Bases de calculs des estimations :</strong>", lm, cy * cm); cy -= 1.0
			sheet.addPara("Revenues 'par unités'  : "+str(total_lic)+" unités x "+val_ppu+" € / par unité / par titre", lm, cy * cm);cy -= 0.5
			
			curY = cy * cm;
			
			strExplFlat = " * 8,4% / par titre / 58 titres"
			if( rights == "master"):
				sheet.addPara("Revenue 'flat rate' // master : " + str(flat_rev) + strExplFlat, lm, curY)
			elif( rights == "author+publishing+master"):
				sheet.addPara("Revenue 'flat rate' // author + publishing + master : " + str(flat_rev) + strExplFlat+" x 2", lm,
					curY)
			elif (rights == "author"):
				sheet.addPara(
					"Revenue 'flat rate' // author : " + str(flat_rev) + " " + strExplFlat + " x 0.5", lm,
					curY)
			elif( rights == "author+publishing"):
				sheet.addPara("Revenue 'flat rate' // author + publishing : "+str(flat_rev)+" "+strExplFlat, lm, curY)
			elif ( rights == "publishing"):
				sheet.addPara("Revenue 'flat rate' // publishing : "+str(flat_rev)+strExplFlat+" x 0.5", lm, curY)
			sheet.addPara("Titre disponibles au moins sur les plateformes listées ici : http://dkh.rocks", 0.5*cm, 1*cm)
			sheet.addPara("En cas de questions ou de clarification ou d'erreurs, n'hésitez pas à nous contacter", 0.5*cm, 0.5*cm)
		else:
			sheet.makeClient("Right holder : <strong>" + entity+"</strong>", lm, 25 * cm)
			sheet.addPara("Game's final release : August 2020", 0.5 * cm, 24 * cm)
			sheet.addPara("Period : April 2018 - 31 august 2020", 0.5 * cm, 23.5 * cm)
			sheet.addPara("Title : " + title, 0.5 * cm, 23 * cm)
			sheet.addPara("Report date : 28 September 2020", 0.5 * cm, 22.5 * cm)
			
			sheet.addTitle("<strong>Operations</strong>", 21.5 * cm)
			sheet.addGrid(
				[
					["'Per unit' distribution", ""],
					["Steam - Licences", str(steam_lic) + " units"],
					["PID - Licences", str(pid_lic) + " units"],
					["Itch - Downloads", str(itch_lic) + " units"],
					["TOTAL", str(steam_lic + pid_lic + itch_lic) + " units"],
					["", ""],
					["'Flat Rate' Operations", ""],
					["Xbox Gamepass Part 1", str(flat_rev) + "€ Taker's Gross"]
				], 300, 200, 2.55 * cm, 14.5 * cm)
			sheet.addTitle("<strong>Estimations</strong>", 13.5 * cm)
			sheet.addGrid(
				[
					["'Per unit' royalty amount", ""],
					["Royalty per unit ", str(val_ppu) + " €/u"],
					["Amount ", str(tr_val_units_gross) + " €"],
					["Current advance ", str(tr_val_advance_unit) + " €"],
					["To be paid ", str(tr_val_units_net) + " €"],
					["", ""],
					["'Flat Rate' royalty amount", ""],
					["To be paid", str(tr_val_flat) + " €"],
					["", ""],
					["TOTAL TO BILL US", str(tr_val_flat+tr_val_units_net) + " €"],
				], 200, 200, 2.55 * cm, 5 * cm)
			
			cy = 4;
			sheet.addPara("<strong>Calculus :</strong>", lm, cy * cm);
			cy -= 1.0
			sheet.addPara(
				"'Per unit' royalty  : " + str(total_lic) + " units x " + val_ppu + " € / per unit / per title", lm,
				cy * cm);
			cy -= 0.5
			
			curY = cy * cm;
			
			strExplFlat = " * 8,4% / per title / 58 titles"
			if (rights == "master"):
				sheet.addPara("'flat rate' royalty // master : " + str(flat_rev) +" €"+ strExplFlat, lm, curY)
			elif (rights == "author+publishing+master"):
				sheet.addPara(
					"'flat rate' royalty // author + publishing + master : " + str(flat_rev) +" €"+ strExplFlat + " x 2", lm,
					curY)
			elif (rights == "author"):
				sheet.addPara(
					"'flat rate' royalty // author + publishing : " + str(flat_rev) + " € " + strExplFlat + " x 0.5", lm,
					curY)
			elif (rights == "publishing"):
				sheet.addPara("'Flat rate' royalty // publishing : " + str(flat_rev)+" €" + strExplFlat + " x 0.5", lm, curY)
			
			sheet.addPara("Game available at least on the platforms listed here : http://dkh.rocks", 0.5 * cm,
						  1 * cm)
			sheet.addPara("If you have questions or we made an error, don't hesitate to reach out.",
						  0.5 * cm, 0.5 * cm)
		sheet.end()
		line = next(rd,None)
		if line[0]=="END":
				break
			
print("finished")
quit(0)
		
