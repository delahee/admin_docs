
import csv
import math
from send_email import *

from reportlab.pdfgen import canvas

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle

from reportlab.platypus import Paragraph,Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-i","--input", help="input tsv")
parser.add_argument("-o","--output", help="output folder")
parser.add_argument("-v","--verbose", help="set verbose",action='store_true')
parser.add_argument("-e","--email", help="send an email with note to author",action='store_true')
parser.add_argument("--iamverysure", help="hints you are really really sure to send thos emails",action='store_true')
args = parser.parse_args()

path = os.getcwd()
# print ("The current working directory is %s" % path)

pdfmetrics.registerFont(TTFont('Roboto-Medium','Roboto-Medium.ttf'))

try:
	os.mkdir(args.output)
except FileExistsError:
	pass
except OSError:
	print ("Creation of the directory %s failed" % path)

testC = canvas.Canvas("tata",bottomup=0)
print(testC.getAvailableFonts ());

tx_css	= "0,40%"
tx_vieil = "6,90%"
tx_csg = "9.2% x 98.25%"
tx_crds = "0.5% x 98.25%"
tx_cafp = "0.35%"

tx_css_pc = 0.40 / 100
tx_vieil_pc = 6.90 / 100
tx_csg_pc = 9.2 / 100 * 98.25 / 100
tx_crds_pc = 0.5 /100 * 98.25 / 100
tx_cafp_pc = 0.35 / 100

def readMonetaryVal(ht):
	ht = ht.replace("€", "")
	ht = ht.replace(",", ".")
	ht = ht.replace(" ", "")
	ht = ht.replace(" ", "")
	return float(ht)

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
	idx = 0;
	auteur_idx = 0;
	auteur_infos_idx = 0;
	client_idx = 0;
	date_idx = 0;
	numero_idx = 0;
	types_idx = 0;
	somme_brut_idx = 0;
	tx_css_idx=0
	tx_vieil_idx=0
	tx_csg_idx=0
	tx_crds_idx=0
	tx_cafp_idx=0
	tva_idx=0
	
	line_desc = next(rd)
	projet_idx = line_desc.index("projet")
	auteur_idx = line_desc.index("auteur")
	auteur_infos_idx = line_desc.index("auteur_infos")
	client_idx = line_desc.index("client")
	date_idx = line_desc.index("date")
	numero_idx = line_desc.index("numero")
	somme_brut_idx = line_desc.index("somme brut")
	#tx_css_idx = line_desc.index("tx css")
	#tx_vieil_idx = line_desc.index("tx vieil")
	#tx_csg_idx = line_desc.index("tx csg")
	#tx_crds_idx = line_desc.index("tx crds")
	#tx_cafp_idx = line_desc.index("tx cafp")
	tva_idx = line_desc.index("tva")
	types_idx = line_desc.index("types")
	email_idx = line_desc.index("email")
	
	rowIdx = 0
	lockfile = args.input.replace(".tsv", ".sent");
	are_email_sent=False
	
	for row in rd:
		projet = row[projet_idx];
		rowIdx = rowIdx + 1
		#print("eval line "+str(rowIdx))
		if( projet == ""):
			#print("skipping line")
			continue
		if (projet == "EOF"):
			break
		if (projet == "END"):
			break
		#print("p:"+projet)
		auteur = row[auteur_idx];
		auteur_infos = row[auteur_infos_idx];
		client = row[client_idx];
		date = row[date_idx];
		numero = row[numero_idx];
		types = row[types_idx];
		somme_brut = row[somme_brut_idx];
		#tx_css=row[tx_css_idx];
		#tx_vieil=row[tx_vieil_idx];
		#tx_csg=row[tx_csg_idx];
		#tx_crds=row[tx_crds_idx];
		#tx_cafp=row[tx_cafp_idx];
		tva=row[tva_idx]
		email=row[email_idx]
		
		def reformat(str):
			return str.replace("\\n","<br/>");
			
		auteur_infos = reformat( auteur_infos );
		client = reformat( client );
		
		#print(auteur_infos);
		
		auteur_file = auteur.replace(" ","_").replace("é","e").replace("ê","e").replace("è","e").replace("ô","o")
		#print(auteur_file);
		filename = args.output +"/"+auteur_file +"_"+ date.replace("/","_") +".pdf";
		c = canvas.Canvas(filename,bottomup=0)
		
		curY = 2*cm
		
		#author
		c.setFont("Roboto-Medium",24);
		c.drawString(1*cm, 1*cm, auteur)
		c.setFont("Roboto-Medium",16);
		SL=ParagraphStyle('dflt');
		P=Paragraph(auteur_infos,SL)
		w,h = P.wrap(400, 50)
		P.drawOn(c,1*cm,curY);
		curY+= 3*cm
		
		#number & date
		PNum=Paragraph("Notes d'auteur·ice/artiste : "+numero+"<br/>Date : "+date,SL)
		PNum.wrap(400, 50)
		PNum.drawOn(c,1*cm,curY);
		curY += 1.23*cm
		
		#project
		PProj = Paragraph("Projet : "+projet , SL)
		PProj.wrap(200, 50)
		PProj.drawOn(c, 1 * cm, curY);
		curY += (5+1.23) * cm
		
		#client headbang
		S=ParagraphStyle('dflt-right');
		S.alignment = 2;
		P=Paragraph(client,S);
		w,h = P.wrap(200, 50);
		P.drawOn(c,21*cm - w - 1*cm,2*cm);
		sb = float(somme_brut.replace(",", "."))
		net_sum = sb - (sb * tx_css_pc + sb * tx_vieil_pc + sb * tx_csg_pc + sb * tx_crds_pc + sb * tx_cafp_pc)
		
		darr= [
		[ projet+" -  "+types, somme_brut+" €"],
		
		["",""],
		["Côtisation à précompter", ""],
		["CSS " + tx_css, str(truncate(sb * tx_css_pc, 2))+"€"],
		["Vieillesse " + tx_vieil, str(truncate(sb * tx_vieil_pc, 2))+"€"],
		["CSG " + tx_csg, str(truncate(sb * tx_csg_pc, 2))+"€"],
		["CRDS " + tx_crds, str(truncate(sb * tx_crds_pc, 2))+"€"],
		["CDFP " + tx_cafp, str(truncate(sb * tx_cafp_pc, 2))+"€"],
		["", ""],
		["Net à payer par l'entreprise", str(truncate(net_sum, 2)) +"€"]
		]
		
		darr.reverse()
		data = ( darr )
		T = Table(data,8*cm,rowHeights=1*cm);
		ts = TableStyle( [
			('TOPPADDING', (0, 0), (-1, -1), 10),
			('BOTTOMPADDING', (0, 0), (-1, -1), 10),
			('GRID',(0,0),(-1,-1),0,colors.black)
		] )
		T.setStyle( ts );
		T.wrapOn(c,18*cm, 18*cm);
		T.drawOn(c, 1*cm,curY);
		curY+= 13*cm
		
		PNum = Paragraph("Côtisation diffuseur de 1.1% à régler à l'URSSAF Artiste-Auteur", SL)
		PNum.wrap(600, 50)
		PNum.drawOn(c, 1 * cm, curY);
		curY += 1.23 * cm
		
		PNum = Paragraph(tva, SL)
		PNum.wrap(200, 50)
		PNum.drawOn(c, 1 * cm, curY);
		curY += 1.23 * cm
		
		c.showPage();
		c.save();
		idx = idx + 1;
		
		print("auteur's note created at " + filename)
		
		if( args.email ):
			print("***********************************")
			print("preparing email to "+email)
			with open("email_body.txt", encoding="utf-8") as body_file, open("email_subject.txt", encoding="utf-8") as subject_fd, open("gmail.json", encoding="utf-8") as g_params:
				
				if( os.path.isfile(lockfile)):
					print(".sent file for this tsv already exists, are you really sure you want to send again to "+args.input)
					quit()
				
				params = json.load(g_params)
				to = email
				subject = subject_fd.read()
				attachment_path = filename
				body = body_file.read()
				login = params["login"]
				pasw = params["password"]
				server = params["server"]
				port = params["port"]
				
				#perform fusion first for better checks
				body = makeFieldFusion(auteur, body)
				
				print("email almost ready")
				print("to:" + to)
				print("subject:" + subject)
				print("body:" + body)
				print("attachment:" + attachment_path)
				print("via:" + login)
				
				
				if( args.iamverysure ):
					#this confirm is actually important because it allows to simulate non bot-ish delay for sending and ensure triple checking everything
					confirm = input("[c]Confirm sending or anything else to quit: ")
					if confirm == 'c' :
						if send_email(
								name=auteur,to=to, subject=subject, body_txt=body, attachment_path=attachment_path, login=login, pasw=pasw, server=server, port=port):
							print("done.")
							are_email_sent = True
						else:
							print("failed")
							are_email_sent = False
							break
					else:
						print("quitting because email sending NOT confirmed ")
						quit(1)
				else:
					print("quitting because no very sure (pass iamverysure argument) ")
					are_email_sent = False
					continue
					
	if( args.email and are_email_sent):
		print("writing .sent file")
		fd = open(lockfile,"w")
		fd.write(str(rowIdx))
		fd.flush()
		fd.close()
		print(".sent file written")
		
print("finished")
quit(0)
		
