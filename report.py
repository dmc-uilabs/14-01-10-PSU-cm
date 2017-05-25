#!/usr/bin/python3

# # Several assets are included with DOME model as .zip files. This will extract them
import os
# import zipfile
# def unzip_directories():

#     directory = os.fsencode('./')

#     for file in os.listdir(directory):
#         filename = os.fsdecode(file)
#         if filename.endswith(".zip"):
#             zip_ref = zipfile.ZipFile(filename, 'r')
#             zip_ref.extractall('./')
#             zip_ref.close()

#             if filename.startswith("TDP"):
#                 os.rename(filename[:-4], "TDPdata")

#             continue
#         else:
#             continue

os.environ["DISPLAY"] = ":0"
# used to unzip files, download TDP data and upload results

with open('in.txt') as f:
    lines = f.readlines()

    inputs = {}

    for line in lines:
        kv = line.rstrip().split("=")
        key = kv.pop(0).strip()
        value = "=".join(kv).strip()
        inputs[key] = value


import filemanagement
filemanagement.download_tdp_data(inputs["inputFile"])
filemanagement.unzip_directories()

from pml import *
import logging
import networkx as nx
from pylab import figure, axes, pie, title, show
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import pdfkit
import datetime
import hashlib
import os.path
import json


AUTH_TOKEN = inputs["authToken"]
CLIENT = "Rolls-Royce"
TDP_NO = "108651"
PART = "AE2100 FCOC Bracket"
MATERIAL = "STEEL"
PREPTS = datetime.datetime.now()
COMPANY = inputs["companyName"]
EXPIRATION = inputs["expireDate"]
CONTACT = inputs["contactInfo"]
COMPANY_URL = "https://portal.opendmc.org/company-profile.php#/profile/"+inputs["companyId"]


def gen_hashes():
    hash_strings = ["the first hash", "the second hash", "number 3", "hash 4", "final 5"]
    for string in hash_strings:
        h = hashlib.new('ripemd160')
        key = string
        print ("set: ")
        for i in range(0,3):
            h.update((str(string)).encode('utf-8'))
            print (str(h.hexdigest()))
            string = str(h.hexdigest())


# create constants.json from VPC string in in.txt
# vpc_json = json.loads(inputs["companyVPC"])
# with open('library/constants.json', 'w') as outfile:
#     json.dump(vpc_json, outfile)

def print_alternatives(alternatives):
    for i, pa in enumerate(alternatives):
        print("    Alternative %d:" % i)
        print("        Cost:", as_dollars(pa["cost"]))
        print("        Time:", as_time(pa["time"]))
        print("        Processes:", pa["selected_processes"])
        print("        Graph: Saved to alternative%d.png" % i)
        as_png(pa["process_graph"], "alternative%d.png" % i)



def gen_tradespace(alternatives, f='tradespace.png', annotate=True):
    X = []
    Y = []
    labels = []

    for alt in alternatives:
        #print (str(alt))
        x = alt['time'].args[0]/3600
        y = alt['cost'].args[0]
        #print (str(x))
        #print (str(y))
        X.append(x)
        Y.append(y)
        #print ("\n\n\n HIIII \n\n\n")
        #print (str(X))
        labels.append("$" + str(int(y)) + "\n" + str(int(x)) + " hours \n(" + str(int(x/24)) + " days)")


    #print (str(X))
    #print (str(Y))
    #print (str(labels))

    plt.xlabel("Time (hours)")
    plt.ylabel("Cost (USD $)")


    plt.scatter(X,Y, marker='o', c='lightblue', s=50, cmap=plt.get_cmap('Spectral'))

#    ax = plt.subplot(111,aspect = 'equal')
#    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

#    plot_margin = 0.55

#    x0, x1, y0, y1 = plt.axis()
#    plt.axis((x0 - plot_margin,
#            x1 + plot_margin,
#            y0 - plot_margin,
#            y1 + plot_margin))

# JAB reserves the right to fiddle around with the colors at a later time ;)
#    fig = plt.figure()
#    fig.patch.set_facecolor('black')
#    ax = plt.subplot()
#    ax.set_facecolor('black')

    if (True==annotate):
        for label, x, y in zip(labels, X, Y):
            plt.annotate(
                label,
                xy=(x, y), xytext=(-15, 15),
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0')
            )



    plt.savefig(f)




def validate_auth(auth_token):
    hash_strings = ["the first hash", "the second hash", "number 3", "hash 4", "final 5"]
    for string in hash_strings:
        h = hashlib.new('ripemd160')
        key = string
        for i in range(0,3):
            h.update((str(string)).encode('utf-8'))
            string = str(h.hexdigest())
            if (auth_token==string):
                fname = "/tmp/" + string
                if (os.path.isfile(fname)):
                    print ("File exists!")
                    return False
                else:
                    print ("valid token!")
                    file = open(fname, 'w')
                    file.write("0")
                    file.flush()
                    file.close()
                    return True

    return False


def err_out(message):
    #read error-template-pt1.html
    file = open('report-templates/error-template-pt1.html', 'r')
    final_html = file.read()
    final_html = final_html + "<h1>" + message + "~</h1>\n"
    file.close
    file = open('report-templates/error-template-pt2.html', 'r')
    final_html = final_html + file.read()
    file.close

    file = open('report-templates/error-template.html', 'w')
    file.write(final_html)
    file.flush()
    file.close

    os.system("xvfb-run -- /usr/bin/wkhtmltopdf 'report-templates/error-template.html' 'report.pdf'")
    #pdfkit.from_file('report-templates/error-template.working.html', 'report.pdf')
    quit()

if (False==validate_auth(AUTH_TOKEN)):
    err_out("Invalid Authorization - no report generated")




# Scan the library/ folder and its subfolders for __init__.pml files, which are
# executed to initialize the PML "database"
auto_register("library")

# Load the eBOM.xml file
# path = r"examples/engine_assembly"
# file = os.path.join(path, "eBOM.xml")
# file = r"examples/simpleExample.xml"

def return_tdp_xml():
    tdp_path = "TDPdata"
    directory = os.fsencode('./'+tdp_path)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".xml"):
            return tdp_path+"/"+filename
        else:
            continue

file = return_tdp_xml()

process_graph = load_ebom(file, build_quantity=50)

# Expand the process graph using the PML models
expand_graph(process_graph)

# # Save graph as image
as_png(process_graph, "full-graph.png")

# def upload_report():
#     import time
#     timestamp = int(time.time())

#     with open('credentials.json') as json_data:
#         d = json.load(json_data)
#         access_key = d['accessKeyId']
#         secret_key = d['secretAccessKey']

#     from boto.s3.connection import S3Connection
#     conn = S3Connection(access_key, secret_key)

#     bucket = conn.get_bucket('psubucket01')

#     from boto.s3.key import Key
#     k = Key(bucket)
#     file_name = str(timestamp)+'report.pdf'
#     k.key = file_name
#     k.set_contents_from_filename('./report.pdf')

#     return file_name

# Validate the graph by ensuring routings exist
if validate_graph(process_graph):


    #############################################
    # Header page
    #############################################
    file = open('report-templates/report-template-pt1.html', 'r')
    final_html = file.read()
    final_html = final_html + '<center><h1 style="color: white"><b>Manufacturability Report for ' + CLIENT + " TDP NO. " + TDP_NO + "</b></h1></center>" + '<center><font style="color:white">Prepared at ' + str(PREPTS) + '</font></center>'
    file.close()

    file = open('report-templates/report-template-pt2.html', 'r')
    final_html = final_html + file.read()
    file.close()

    final_html = final_html + """
                  <tr>
			  <td width="30%%">
	          		<img src="../TDPdata/iso_capture.png" style="width:100%%" alt="picture of iso_capture.png">
			  </td>
			  <td width="60%%" align="center">
            			<h5 class="w3-opacity"><b>Client: %(CLIENT)s</b></h5>
            			<h5 class="w3-opacity"><b>Part: %(PART)s</b></h5>
            			<h5 class="w3-opacity"><b>Preferred material: %(MATERIAL)s</b></h5>
	  		</td>
		  </tr>
		  <tr>
			  <td colspan="2">
				  <h5 class="w3-opacity"><b>Prepared For:</b> %(COMPANY)s</h5>
				  <h5 class="w3-opacity"><b>Prepared at:</b> %(PREPTS)s</h5>
				  <h5 class="w3-opacity"><b>Good for:</b> Cost analysis and quote good until %(EXPIRATION)s</h5>
                                  <h5 class="w3-opacity"><b>Company Profile:</b> %(COMPANY_URL)s</h5>
				  <h5 class="w3-opacity"><b>Contact %(CONTACT)s for questions</h5>
			  </td>
                  </tr>
                  """ % locals()

    file = open('report-templates/report-template-pt3.html', 'r')
    final_html = final_html + file.read()
    file.close()

    #############################################
    # cheapest config
    #############################################
    (total_cost, selected_processes) = find_min(process_graph, weight="cost")
    minimum_graph = create_subgraph(process_graph, selected_processes)
    total_time = sum_weight(minimum_graph, weight="time")
    total_cost = float("{0:.2f}".format(total_cost.args[0]))
    total_time = float("{0:.2f}".format(total_time.args[0]/3600))

    # print("total cost")
    # print(total_cost)
    # print(type(total_cost.args[0]).round(2))

    final_html = final_html + """

        <div class="w3-container" style="float:left; width:33%%"> <h5 class="w3-opacity"><b>Cheapest:</b></h5> <table cellspacing='0'> <!-- cellspacing='0' is important, must stay --> <!-- Table Header --> <thead> <tr>
			<th colspan="3">%(total_cost)s and %(total_time)s lead time</th>
		</tr> <tr> <th>Category</th> <th>Cost</th> <th>Uncertainty</th> </tr> </thead> <!-- Table Header --> <!-- Table Body --> <tbody> <tr> <td>Labor</td> <td>Unavailable</td> <td>Unavailable</td> </tr><!-- Table Row --> <tr class="even"> <td>Materials</td> <td>Unavailable</td> <td>Unavailable</td> </tr><!-- Darker Table Row --> <tr> <td>Overhead</td> <td>Unavailable</td> <td>Unavailable</td> </tr> <tr class="even"> <td>Fee</td> <td>Unavailable</td> <td>Unavailable</td> </tr>
		<tr>
			<td><b>Total</b></td>
			<td><b>$%(total_cost)s</b></td>
			<td><b>Unavailable</b></td>
		</tr> </tbody> <!-- Table Body --> </table> </div>
                """ % locals()

    #############################################
    # fastest config
    #############################################
    (total_time, selected_processes) = find_min(process_graph, weight="time")
    minimum_graph = create_subgraph(process_graph, selected_processes)
    total_cost = sum_weight(minimum_graph, weight="cost")
    total_cost = float("{0:.2f}".format(total_cost.args[0]))
    total_time = float("{0:.2f}".format(total_time.args[0]/3600))

    final_html = final_html + """

        <div class="w3-container" style="float:left; width:33%%"> <h5 class="w3-opacity"><b>Fastest:</b></h5> <table cellspacing='0'> <!-- cellspacing='0' is important, must stay --> <!-- Table Header --> <thead> <tr>
			<th colspan="3">%(total_cost)s and %(total_time)s lead time</th>

		</tr> <tr> <th>Category</th> <th>Cost</th> <th>Uncertainty</th> </tr> </thead> <!-- Table Header --> <!-- Table Body --> <tbody> <tr> <td>Labor</td> <td>Unavailable</td> <td>Unavailable</td> </tr><!-- Table Row --> <tr class="even"> <td>Materials</td> <td>Unavailable</td> <td>Unavailable</td> </tr><!-- Darker Table Row --> <tr> <td>Overhead</td> <td>Unavailable</td> <td>Unavailable</td> </tr> <tr class="even"> <td>Fee</td> <td>Unavailable</td> <td>Unavailable</td> </tr>

		<tr>
			<td><b>Total</b></td>
			<td><b>$%(total_cost)s</b></td>
			<td><b>Unavailable</b></td>
		</tr> </tbody> <!-- Table Body --> </table> </div>
                """ % locals()


    #############################################
    # balanced config
    #############################################


  #   (cp_time, selected_processes) = find_min(process_graph, weight=lambda n : 0.5*n.cost/dollars + 0.5*n.time/days)
  #   (cp_cost, selected_processes) = find_min(process_graph, weight=lambda n : 0.5*n.cost/dollars + 0.5*n.time/days)
  #   minimumGraph = create_subgraph(process_graph, selected_processes)
  #   total_time = cp_time
  #   total_cost = cp_cost

  #   final_html = final_html + """
  #       <div class="w3-container" style="float:left; width:33%%"> <h5 class="w3-opacity"><b>Balanced:</b></h5> <table cellspacing='0'> <!-- cellspacing='0' is important, must stay --> <!-- Table Header --> <thead> <tr>
		# 	<th colspan="3">%(total_cost)s and %(total_time)s lead time</th>
		# </tr> <tr> <th>Category</th> <th>Cost</th> <th>Uncertainty</th> </tr> </thead> <!-- Table Header --> <!-- Table Body --> <tbody> <tr> <td>Labor</td> <td>Unavailable</td> <td>Unavailable</td> </tr><!-- Table Row --> <tr class="even"> <td>Materials</td> <td>Unavailable</td> <td>Unavailable</td> </tr><!-- Darker Table Row --> <tr> <td>Overhead</td> <td>Unavailable</td> <td>Unavailable</td> </tr> <tr class="even"> <td>Fee</td> <td>Unavailable</td> <td>Unavailable</td> </tr>
		# <tr>
		# 	<td><b>Total</b></td>
		# 	<td><b>%(total_cost)s</b></td>
		# 	<td><b>Unavailable</b></td>
		# </tr> </tbody> <!-- Table Body --> </table> </div>
  #               """ % locals()


    #############################################
    # gen tradespace
    #############################################
    #print ("\n\n\n---ALLLL----\n\n\n")
    all_alternatives = generate_alternatives(process_graph, weights=("cost", "time"))
    #print_alternatives(all_alternatives)
    gen_tradespace(all_alternatives, 'all-alternatives', annotate=False)

    #print ("\n\n\n---PAAARRREEETTTOOOOSSSS----\n\n\n")
    all_alternatives = generate_alternatives(process_graph, weights=("cost", "time"))
    pareto_alternatives = pareto(all_alternatives, weights=("cost", "time"))
    #print_alternatives(pareto_alternatives)
    gen_tradespace(pareto_alternatives, 'pareto-alternatives.png')

    file = open('report-templates/report-template-pt4.html', 'r')
    final_html = final_html + file.read()
    file.close()


    #############################################
    # manufacturability
    #############################################
    final_html = final_html + "<ul>"

    #manufacturability feedback
    for feedback in MFG_FEEDBACK:
        final_html = final_html + "<li>" + str(feedback) + "</li>"

    final_html = final_html + "</ul>"


    #############################################
    # finish file
    #############################################
    file = open('report-templates/report-template-pt5.html', 'r')
    final_html = final_html + file.read()
    file.close()

    #############################################
    # write out html file and convert to pdf
    #############################################
    file = open('report-templates/report-template.html', 'w')
    file.write(final_html)
    file.flush()
    file.close()

    os.system("xvfb-run -a -- /usr/bin/wkhtmltopdf 'report-templates/report-template.html' 'report.pdf'")
    # pdfkit.from_file('report-templates/report-template.html', 'report.pdf')

    final_name = filemanagement.upload_report()

    # reportTemplate=open('report-templates/report-template.html').readlines()
    # reportTemplateString=""
    #
    # reportCSS=open('report-templates/report.css').readlines()
    # reportCSSString="<style>"
    #
    # for n,line in enumerate(reportTemplate):
    #     reportTemplateString+=line.rstrip()
    #
    # for y,line in enumerate(reportCSS):
    #     reportCSSString+=line.rstrip()
    #
    # reportCSSString+="</style>"

    # outputs = "outputs="+str(inputs)
    outputs= "\noutputFile="+final_name
    outputTemplate = "\noutputTemplate=<h3>Report uploaded to: <a href=\"https://s3.amazonaws.com/psubucket01/"+final_name+"\">https://s3.amazonaws.com/psubucket01/"+final_name+"</a>"

    target = open("out.txt", 'w')
    target.write(outputs+outputTemplate)
    target.close

else:
    err_out("Not manufacturable with this production center - no report generated")
    #print()
    #print("Process graph is invalid - No routing exists")
