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

data_path = "/opt/osint/data/courtlists/"
data_path_results = "/opt/osint/data/courtlists_hits/"
search_list_json = "/opt/osint/cso-searchlist.json"
progress_report_enabled = False
progress_report_secs = 60 * 2
search_cache_only = False
verbose_output = True
search_mode = "ALL" # default to only searching today
# filename = "2019-11-21_Nanaimo_Law_Court_Provincial_Completed.pdf"

# initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--today", help="search only today", action="store_true")
parser.add_argument("-q", "--quiet", help="quiet output", action="store_true")
parser.add_argument("-c", "--cacheonly", help="search only cache", action="store_true")

args = parser.parse_args() # read arguments from the command line
if args.quiet: 
    verbose_output = False

if args.today:
    search_mode = "TODAY"

#   current date and time
now = datetime.now()
date_prefix = now.strftime("%Y-%m-%d_")

if verbose_output:
    progress_report_enabled = True
    
    if not search_cache_only:
        print("Search mode: pdf documents and cache")
    else:
        print("Search mode: cached text only")
    
    print("Search list:",search_list_json)
    print("Search path:",data_path)
    print("Results path:",data_path_results)

search_terms = []
with open(search_list_json, 'r') as json_file:
    search_terms = json.load(json_file)
    if len(search_terms) is 0:
        print("WARNING: no search terms specified")

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
if search_mode is "TODAY":
    files = glob.glob(data_path + date_prefix + "*.pdf")
    cache_files = glob.glob(data_path + date_prefix + "*.pdf.text")
else:
    files = glob.glob(data_path + "*.pdf")
    cache_files = glob.glob(data_path + "*.pdf.text")

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

            pdfFileObj = open(file, "rb")
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            num_pages = pdfReader.numPages

            doc_text = ""
            for page in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(page)
                doc_text += pageObj.extractText()

            if doc_text:
                f = open(file + ".text", "w")
                f.write(doc_text)
                f.close()

        else:

            f = open(file + ".text", "r")
            doc_text = f.read()
            f.close()

            # search document
            for search_term in search_terms:
                if search_term[0] is not '-':
                    if search_term in doc_text.upper():
                        hits_files.append(file)
                        try:
                            copyfile(file, data_path_results + search_term + "-" + os.path.basename(file))
                            print("FOUND",search_term,"in", os.path.basename(file))
                        except Exception as e:
                            print("ERROR: unable to copy file",e)

    except Exception as e:
        num_files_errors += 1
        if verbose_output:
            # print("ERROR reading",file,e)
            pass

job_duration_secs = time.time()-time_startjob
percent_read_errors = (num_files_errors/current_filenum) * 100
if verbose_output:
    print("Completed. Searched",current_filenum,"files in",round(job_duration_secs,1),"seconds (" + str(round((job_duration_secs/current_filenum)*1000,2)) + " msecs average per document)")
    if (num_files_errors):
        print("Error reading",num_files_errors,"files (" + str(round(percent_read_errors,1)) + "%)")

