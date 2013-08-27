import os
import time
import tempfile

import cups
import requests
import qrcode
from flask import Flask, url_for, redirect
from werkzeug.contrib.fixers import ProxyFix
from fpdf import FPDF

CUPS = cups.Connection()
PRINTER_NAME = 'ticketprinter'
REST_PASS = 'XXX'

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

app.debug = True 

@app.route("/")
def index():
  return redirect(url_for('static', filename='q.html'))

@app.route("/status")
def status():
  r = requests.get('http://q.foi.hr/rest/info')
  print r.text
  return r.text

@app.route("/request/<int:queue_id>")
def request(queue_id):
  r = requests.get('http://q.foi.hr/restSecure/requestTicket/' + str(queue_id), auth=('rest', REST_PASS))
  data = r.json()

  if 'newTicketValue' in data:
    print_file('Ticket ' + data['newTicketValue'], data)

  return r.text 

def print_file(title, data):
  (f, fname) = tempfile.mkstemp(text=True)
  pdf = FPDF('L', unit='mm', format=(112, 100))
  pdf.add_page()

  pdf.set_font('Arial', '', 8)
  pdf.cell(0, 10, data['newTicketTime'], 0, 1)
  pdf.ln()
  pdf.ln()

  pdf.set_font('Arial', 'B', 128)
  pdf.cell(0, 10, data['newTicketValue'], 0, 1, 'C')

  pdf.set_font('Arial', '', 18)
  pdf.ln()
  pdf.cell(0, 10, data['description'].encode('cp1252', 'ignore'), 0, 1, 'C')

  qr = qrcode.QRCode(box_size=3)
  link = 'http://q.foi.hr/view?id=' + str(data['id'])
  qr.add_data(link)
  qr.make(fit=True)
  img = qr.make_image()
  (qf, qfname) = tempfile.mkstemp(suffix='.png')
  img.save(qfname, 'PNG')
  pdf.image(qfname)

  pdf.set_font('Arial', '', 10)
  pdf.text(47, 87, link)

  pdf.output(fname)

  job = CUPS.printFile(PRINTER_NAME, fname, title, {})
  while job in CUPS.getJobs(which_jobs='not-completed').keys():
    time.sleep(2)

  os.unlink(fname)
  os.unlink(qfname)

if __name__ == "__main__":
  app.run(port=8000)

