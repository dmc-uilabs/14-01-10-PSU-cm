#!/usr/bin/python3

import pdfkit

options = { 'quiet': '' }


#pdfkit.from_file('report-template.html', 'report.pdf', options=options, css='report.css')
pdfkit.from_file('report-template.html', 'report.pdf', options=options)
