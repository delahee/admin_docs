# Import smtplib for the actual sending function
import json
import smtplib
import ssl
import os
import pathlib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def fcase(str):
	return str[0].upper() + str[1:].lower()
	
def makeFieldFusion(name,txt):
	if "*|FNAME|*" in txt:
		if( name == None):
			print("*|FNAME*| detected, expecting a name to split")
			return False
		else:
			fname = name.split(" ")[0]
			fname = fcase(fname)
			if( fname == None):
				print("invalid fname cancelling "+fname)
				return False
			txt = txt.replace("*|FNAME|*", fname)
	return txt

#leaving subject and body empty will cause SPAM flagging
def send_email(name, to, subject, body_txt, body_path = None, attachment_path=None, login="", pasw="", server="smtp.gmail.com",
			   port=465):
	msg = MIMEMultipart('html')
	
	if body_path != None:
		body_txt = open(body_path, "r", encoding="utf-8").read()
	
	body_txt = makeFieldFusion(name,body_txt)
	msg.attach(MIMEText(body_txt, "plain"))
	
	# me == the sender's email address
	# you == the recipient's email address
	msg['Subject'] = subject
	msg['From'] = login
	msg['To'] = to
	msg.add_header("X-Priority",str(1))
	
	# Send the message via our own SMTP server.
	# s = smtplib.SMTP('smtp.headbang.club')
	
	# We assume that the file is in the directory where you run your Python script from
	if attachment_path != None:
		attachment = open(attachment_path, "rb")
		# The content type "application/octet-stream" means that a MIME attachment is a binary file
		part = MIMEBase("application", "octet-stream")
		part.set_payload(attachment.read())
		encoders.encode_base64(part)
		part.add_header(
			"Content-Disposition",
			f"attachment; filename= { os.path.basename(attachment_path)}",
		)
		msg.attach(part)
	
	# transaction
	
	context = context = ssl.create_default_context() if (port != 25) else None
	
	with smtplib.SMTP_SSL(server, port, context=context) as s:
		s.login(login, pasw)
		s.helo("headbang.club")
		s.send_message(msg)
		return True
	return False

#for gmail/gsuite
#enable two steps
#create an app password
#use the right email server
#in gsuite admin check the "keep all messages" otherwise the emails won't be kept in "sent"
#be extra careful, DO NOT LEAVE TEST EMAILS IN SPAM, unspam them otherwise you'll contaminate your own spam scores
#check out : https://www.samlogic.net/articles/reduce-spam-score.htm

def test_params():
	to = "david.elahee@gmail.com"
	subject = "test email 0"
	body_txt = "my body my soul but why the fk am i writin this!"
	#body_path = "email_body.txt"
	body_path=None
	attachment_path = "Roboto-Medium.ttf"
	
	login = "delahee@headbang.club"
	pasw = "ratatapoumratapoum"
	server = 'smtp-relay.gmail.com'
	port = 465
	
	send_email(to=to, subject=subject, body_txt=body_txt, body_path=body_path, attachment_path=attachment_path, login=login, pasw=pasw,
			   server=server, port=port)
	
def test_file():
	to = "david.elahee@gmail.com"
	subject = "test email 1"
	body_txt = "my body my soul"
	attachment_path = "Roboto-Medium.ttf"
	
	params = json.load(open( "gmail.json",encoding="utf-8"))
	login = params["login"]
	pasw = params["password"]
	server = params["server"]
	port = params["port"]
	
	send_email(to=to, subject=subject, body_txt=body_txt, attachment_path=attachment_path,
			   login=login, pasw=pasw,
			   server=server, port=port)
	
if __name__ == "__main__":
	print("testing email sending")
	test_file()