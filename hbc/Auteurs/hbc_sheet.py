from reportlab.pdfgen import canvas

from reportlab.lib import colors
from reportlab.lib import utils
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle,LineStyle

from reportlab.platypus import Paragraph,Table, TableStyle,Spacer,Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class Sheet:
	c = None
	filename = ""
	SL = None
	
	top = 29.7*cm
	def __init__(self, filename):
		pdfmetrics.registerFont(TTFont('Roboto-Medium', 'Roboto-Medium.ttf'))
		self.filename = filename
		c = self.c = canvas.Canvas(filename)
		c.setFont("Roboto-Medium", 24);
		self.SL = ParagraphStyle('dflt');
		
		
	def addTitle(self, title, y ):
		S = ParagraphStyle('dflt',alignment=1);
		P = Paragraph(title, S);
		w, h = P.wrap(300, 50);
		P.drawOn(self.c, 21*cm * 0.5 - w * 0.5, y)
	
	def addHbcHeader(self):
		c = self.c; top = self.top
		
		S = ParagraphStyle('dflt-right');
		S.alignment = 2;
		
		img = utils.ImageReader('logoHD.png')
		iw, ih = img.getSize()
		aspect = ih / float(iw)
		
		width = 200
		I = Image('logoHD.png',width=width, height=(width * aspect))
		w, h = I.wrap(200, 50);
		I.drawOn(self.c,  14 *cm, top - h - 1*cm)
		
		P = Paragraph(	"<strong>HEADBANG CLUB</strong><br/>"
					  	+"15 RUE FERDINAND BUISSON<br/>"
						+"16160 GOND-PONTOURE<br/>CHARENTE - FRANCE<br/>"
						+"VAT - FR63824464127<br/>"
						+"TEL - +33 (0)6 63 92 55 96<br/>"
						+"bm@headbang.club / business@headbang.club", S);
		w,h = P.wrap(300, 50);
		P.drawOn(self.c, 21*cm - w - 0.5 * cm, self.top - h - 4*cm);
		pass
		
	def makeClient(self,literal,x,y):
		S = ParagraphStyle('dflt-left');
		P = Paragraph(literal, S);
		w, h = P.wrap(300, 50);
		P.drawOn(self.c, x, y);
		pass
	
	def addPara(self,literal,x,y):
		S = ParagraphStyle('dflt-left');
		P = Paragraph(literal, S);
		w, h = P.wrap(600, 100);
		P.drawOn(self.c, x,y);
		pass
	
	def addLine(self):
		pass
	
	def end(self):
		c = self.c
		
		c.showPage()
		c.save()
		pass
	
	def addGrid(self,elems, w , h, x , y):
		c = self.c
		T = Table(elems, 8 * cm, rowHeights= 0.8 * cm);
		ts = TableStyle([
			('TOPPADDING', (0, 0), (-1, -1), 10),
			('BOTTOMPADDING', (0, 0), (-1, -1), 10),
			('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
			('GRID', (0, 0), (-1, -1), 0, colors.black)
		])
		T.setStyle(ts);
		T.wrapOn(c, w,h);
		T.drawOn(c, x, y);

def testReport():
	sheet = Sheet("my_report.pdf")
	sheet.addHbcHeader()
	sheet.makeClient("pavé du destinataire")
	sheet.addTitle("RELEVE DE VENTES - DOUBLE KICK HEROES")
	sheet.addGrid(
		[
			[ "projet -  types", "somme_brut €"],
			["",""],
			["Côtisation à précompter", ""],
			["CSS  tx_css", " 66 €"],
			["Vieillesse  tx_vieil", " 66 €"],
			["CSG  tx_csg", " 66 €"],
			["CRDS  tx_crds", " 66 €"],
			["CDFP  tx_cafp", " 66 €"],
			["", ""],
			["Net à payer par l'entreprise", " 66 €"]
		], 300 , 200, 3 * cm, 12*cm)
	sheet.addTitle("ESTIMATION DE ROYAUTE - TRIBUTE OF BLOOD - GOROD", -12*cm)
	sheet.addGrid(
		[
			["projet -  types", "somme_brut €"],
			["", ""],
			["Côtisation à précompter", ""],
			
			["Net à payer par l'entreprise", " 66 €"]
		], 300, 200, 3 * cm, 5 * cm)
	
	sheet.addPara("Estimation sur la base de calcul : <br/> Revenue par unité : 95 unité * 0.015c / unité / par titre",0,3*cm)
	sheet.addPara("Revenue flat master : 85000 * 8,4% / (1 / 58 titre ) ",0,2*cm)
	sheet.addPara("Revenue flat author + publishing : 85000 * 8,4% / par titre",0,1*cm)
	sheet.addPara("Revenue flat publishing : 85000 * 8,4% / par titre",0,0*cm)
	sheet.end()

if __name__ == "__main__":
	print("testing report writer")
	testReport()
	print("finished")
	quit(0)