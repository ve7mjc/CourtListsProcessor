#!/usr/bin/python3

import PyPDF2
import glob
import time

from os.path import basename
from datetime import datetime
import hashlib

import json

import os.path
from os import path
from shutil import copyfile

import argparse
import requests

data_path = "/opt/osint/data/courtlists/"
data_path_results = "/opt/osint/data/courtlists_hits/"
search_list_json = "/opt/osint/cso-searchlist.json"
config_path_json = "/opt/osint/config.json"
progress_report_enabled = False
progress_report_secs = 60 * 2
search_cache_only = False
verbose_output = True
search_mode = "ALL" # default to only searching today?
# filename = "2019-11-21_Nanaimo_Law_Court_Provincial_Completed.pdf"

email_configured = False
mailgun_api_key = None
mailgun_domain = None
reports_email_from = None
reports_email_to = None

try:
    with open(config_path_json) as json_config_file:
        if verbose_output: print("configuring via config.json")
        try:
            data = json.load(json_config_file)
            mailgun_api_key = data["mailgun_api_key"]
            mailgun_domain = data["mailgun_domain"]
            reports_email_from = data["reports_email_from"]
            reports_email_to = data["reports_email_to"]
            email_configured = True
        except Exception as e:
            print("error processing config.json",e)
            raise
except:
    pass # not loading a config

def email_reports(report_texts, attachments):

    global mailgun_api_key, reports_email_from, reports_email_to
        
    report_text = ""
    report_text_html = ""
    print(report_texts)
    for hit_text in report_texts:
        report_text = report_text + hit_text + "\r\n"
        report_text_html = report_text_html + hit_text + "<br />"

    return requests.post(
        "https://api.mailgun.net/v3/" + mailgun_domain + "/messages",
        auth=("api", mailgun_api_key),
        files=attachments,
        data={"from": reports_email_from,
              "to": reports_email_to,
              "subject": "CSO HITS (" + str(len(report_texts)) + ")",
              "text": report_text,
              "html": "<html>" + report_text_html + "</html>"})


# initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--today", help="search only today", action="store_true")
parser.add_argument("-q", "--quiet", help="quiet output", action="store_true")
parser.add_argument("-c", "--cacheonly", help="search only cache", action="store_true")
parser.add_argument("-d", "--completed", help="search only completed list", action="store_true")
parser.add_argument("-l", "--daily", help="search only daily list", action="store_true")

args = parser.parse_args() # read arguments from the command line
if args.quiet: 
    verbose_output = False

if args.today:
    search_mode = "TODAY"

search_completed = True
search_daily = True

if args.completed and not args.daily:
    search_daily = False
elif args.daily and not args.completed:
    search_completed = False   

#   current date and time
now = datetime.now()
date_prefix = now.strftime("%Y-%m-%d_")

search_terms = []
with open(search_list_json, 'r') as json_file:
    search_terms = json.load(json_file)
    if len(search_terms) is 0:
        print("WARNING: no search terms specified")
num_search_terms = len(search_terms)

if verbose_output:
    progress_report_enabled = True
    
    if not search_cache_only:
        print("Search mode: pdf documents and cache")
    else:
        print("Search mode: cached text only")
    
    print("Search list:",search_list_json + "; found",num_search_terms,"search terms")
    print("Search path:",data_path)
    print("Results path:",data_path_results)

# case insensitive search; uppercase all search terms
case_insensitive_terms = []
for search_term in search_terms:
    case_insensitive_terms.append(search_term.upper())
    search_terms = case_insensitive_terms

# clear out results path
try:
    os.makedirs(data_path_results)
except:
    pass
for file in os.scandir(data_path_results):
    if file.name.endswith(".pdf"):
        os.unlink(file.path)

#files = glob.glob(data_path + date_prefix + "*Nanaimo*.pdf")

if search_mode is "TODAY": search_date_prefix = date_prefix
else: search_date_prefix = ""

files = []
cache_files = []

# pull all files from OS into lists
files = glob.glob(data_path + search_date_prefix + "*.pdf")
cache_files = glob.glob(data_path + search_date_prefix + "*.pdf.text")

# iterate through and weed out what we dont want
newFiles = []
for i in range(len(files)):
    should_pass = True
    if (not search_completed) and ("Completed" in files[i]):
        should_pass = False
    if (not search_daily) and ("Completed" not in files[i]):
        should_pass = False
    if (search_mode == "TODAY") and (date_prefix not in files[i]):
        should_pass = False
    if should_pass: 
        newFiles.append(files[i])
files = newFiles

total_files = len(files)
total_cached_files = len(cache_files)
hits_files = []

print("found",total_files,"court lists (" + str(total_cached_files) + " cached)")
if (not total_cached_files) and (not total_files):
    print("WARNING: Found no documents to search!")
    sys.exit(True)

time_startjob = time.time()
time_lastreport = time.time()

# cache search results to documents

current_filenum = 0
num_files_errors = 0
num_files_copied = 0
num_search_hits = 0
search_hit_documents = []
search_hit_texts = []
for file in files:

    # Progress Report
    current_filenum += 1
    if progress_report_enabled and ((time.time() - time_lastreport) > progress_report_secs):
        time_lastreport = time.time()
        progress = round((current_filenum/total_files)*100,1)
        ete = ((time_lastreport - time_startjob) / (current_filenum)) * (total_files-current_filenum)
        print(current_filenum,"/",total_files,"-",str(progress)+"%","ETE:",round(ete/60,1))

    try:

        # look for cached text first
        if (file + ".text") not in cache_files and not search_cache_only:
    
            # we assume the file exists at this point as it is contained in
            # a list obtained through a directory listing
            try:
                pdfFileObj = open(file, "rb")
                pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
                num_pages = pdfReader.numPages

                doc_text = ""
                for page in range(pdfReader.numPages):
                    pageObj = pdfReader.getPage(page)
                    doc_text += pageObj.extractText()

            except Exception as e:
                doc_text = "CORRUPTED"
                print("Error reading",file,e)

            try:
                if doc_text:
                    f = open(file + ".text", "w")
                    f.write(doc_text)
                    f.close()
            except Exception as e:
                print("unable to write cache file",file + "text")
                print(e)


        else:

            f = open(file + ".text", "r")
            doc_text = f.read()
            f.close()

            # search document
            for search_term in search_terms:
                if search_term[0] is not '-':
                    if search_term in doc_text.upper():
                        hits_files.append(file)
                        num_search_hits += 1
                        search_hit_text = "FOUND " + search_term + " in " + os.path.basename(file)
                        if verbose_output: print(search_hit_text)
                        search_hit_texts.append(search_hit_text)
                        search_hit_documents.append((file, search_term + "-" + os.path.basename(file))) # prepare for email
                        try:
                            copyfile(file, data_path_results + search_term + "-" + os.path.basename(file))
                            num_files_copied += 1
                        except Exception as e:
                            print("ERROR: unable to copy file",e)

    except Exception as e:
        num_files_errors += 1
        if verbose_output:
            print("ERROR reading",file,e)
            pass


job_duration_secs = time.time()-time_startjob
percent_read_errors = (num_files_errors/current_filenum) * 100
if verbose_output:
    print("Completed. Searched",current_filenum,"files for",num_search_terms,"search terms in",round(job_duration_secs,1),"seconds (" + str(round((job_duration_secs/current_filenum)*1000,2)) + " msecs average per document)")
    print("Found",num_search_hits,"hits; copied",num_files_copied,"files")
    if (num_files_errors):
        print("Error reading",num_files_errors,"files (" + str(round(percent_read_errors,1)) + "%)")

if email_configured and len(search_hit_documents):
    if verbose_output: print("emailing documents..")
    attachments = []
    for (doc_file,doc_name) in search_hit_documents:
        attachments.append(("attachment", (doc_name, open(doc_file,"rb").read())))
    email_reports(search_hit_texts, attachments)
    if verbose_output: print("done..")
