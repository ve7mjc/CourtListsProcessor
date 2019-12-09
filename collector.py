#!/usr/bin/python3

# Collect Adult Criminal Daily Court lists for Provintial and Supreme Law Courts in BC
# Iterate through list of all law court URLs and retrieve latest PDF
# Compare against locally stored document for same date and compare hashes
# Only save if hash differs
#
#   BC CSO format: https://justice.gov.bc.ca/courts/court-lists/criminal/lists/{NAME}.pdf
# Save Format: YYYY-MM-DD_{NAME}.pdf

import urllib.request
from os.path import basename
from datetime import datetime
import hashlib
import traceback
import requests

import os.path
from os import path

import argparse

# initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--quiet", help="quiet output", action="store_true")
parser.add_argument("-c", "--completedonly", help="only completed lists", action="store_true")
parser.add_argument("-d", "--dailyonly", help="only daily lists", action="store_true")
parser.add_argument("-p", "--psclonly", help="only daily lists", action="store_true")
parser.add_argument("-f", "--overwrite", help="force new download, overwrite cache", action="store_true")

args = parser.parse_args() # read arguments from the command line

if args.quiet: verbose_output = False
else: verbose_output = True

include_completed = True
include_daily_list = True
include_pscl = True

if args.dailyonly:
    include_completed = False
    include_pscl = False
if args.completedonly:
    include_daily_list = False
    include_pscl = False
if args.psclonly:
    include_daily_list = False
    include_completed = False

# CONFIG
filesystem_path = "/opt/osint/data/courtlists/"

# adult criminal courts
pac_courts = {
    "100_Mile_House_Law_Court_Provincial",
    "Abbotsford_Provincial_Court_Provincial",
    "Alexis_Creek_Provincial_Court_Provincial",
    "Anahim_Lake_Provincial_Court_Provincial",
    "Ashcroft_Provincial_Court_Provincial",
    "Atlin_Provincial_Court_Provincial",
    "Bella_Bella_Provincial_Court_Provincial",
    "Bella_Coola_Provincial_Court_Provincial",
    "Burns_Lake_Provincial_Court_Provincial",
    "Campbell_River_Law_Court_Provincial",
    "Castlegar_Provincial_Court_Provincial",
    "Chase_Provincial_Court_Provincial",
    "Chetwynd_Provincial_Court_Provincial",
    "Chilliwack_Law_Court_Provincial",
    "Clearwater_Provincial_Court_Provincial",
    "Courtenay_Law_Court_Provincial",
    "Cranbrook_Law_Court_Provincial",
    "Creston_Law_Court_Provincial",
    "Dawson_Creek_Law_Court_Provincial",
    "Dease_Lake_Provincial_Court_Provincial",
    "Downtown_Community_Court_Provincial",
    "Duncan_Law_Court_Provincial",
    "Fernie_Law_Court_Provincial",
    "Fort_Nelson_Law_Court_Provincial",
    "Fort_St_James_Provincial_Court_Provincial",
    "Fort_St_John_Law_Court_Provincial",
    "Fraser_Lake_Provincial_Court_Provincial",
    "Ganges_Provincial_Court_Provincial",
    "Gold_River_Provincial_Court_Provincial",
    "Golden_Law_Court_Provincial",
    "Good_Hope_Lake_Provincial_Court_Provincial",
    "Grand_Forks_Law_Court_Provincial",
    "Hazelton_Provincial_Court_Provincial",
    "Houston_Provincial_Court_Provincial",
    "Hudsons_Hope_Provincial_Court_Provincial",
    "Invermere_Law_Court_Provincial",
    "Justice_Centre_(Judicial)_Provincial",
    "Kamloops_Law_Court_Provincial",
    "Kelowna_Law_Court_Provincial",
    "Kitimat_Law_Court_Provincial",
    "Klemtu_Provincial_Court_Provincial",
    "Kwadacha_Provincial_Court_Provincial",
    "Lillooet_Law_Court_Provincial",
    "Lower_Post_Provincial_Court_Provincial",
    "Mackenzie_Provincial_Court_Provincial",
    "Masset_Provincial_Court_Provincial",
    "McBride_Provincial_Court_Provincial",
    "Merritt_Law_Court_Provincial",
    "Nakusp_Provincial_Court_Provincial",
    "Nanaimo_Law_Court_Provincial",
    "Nelson_Law_Court_Provincial",
    "New_Aiyansh_Provincial_Court_Provincial",
    "New_Westminster_Law_Court_Provincial",
    "North_Vancouver_Provincial_Court_Provincial",
    "Pemberton_Provincial_Court_Provincial",
    "Penticton_Law_Court_Provincial",
    "Port_Alberni_Law_Court_Provincial",
    "Port_Coquitlam_Provincial_Court_Provincial",
    "Port_Hardy_Law_Court_Provincial",
    "Powell_River_Law_Court_Provincial",
    "Prince_George_Law_Court_Provincial",
    "Prince_Rupert_Law_Court_Provincial",
    "Princeton_Law_Court_Provincial",
    "Queen_Charlotte_Provincial_Court_Provincial",
    "Quesnel_Law_Court_Provincial",
    "Revelstoke_Law_Court_Provincial",
    "Richmond_Provincial_Court_Provincial",
    "Robson_Square_Provincial_Court_Provincial",
    "Rossland_Law_Court_Provincial",
    "Salmon_Arm_Law_Court_Provincial",
    "Sechelt_Provincial_Court_Provincial",
    "Sidney_Provincial_Court_Provincial",
    "Smithers_Law_Court_Provincial",
    "Sparwood_Provincial_Court_Provincial",
    "Stewart_Provincial_Court_Provincial",
    "Surrey_Provincial_Court_Provincial",
    "Tahsis_Provincial_Court_Provincial",
    "Terrace_Law_Court_Provincial",
    "Tofino_Provincial_Court_Provincial",
    "Tsay_Keh_Dene_Provincial_Court_Provincial",
    "Tumbler_Ridge_Provincial_Court_Provincial",
    "Ucluelet_Provincial_Court_Provincial",
    "Valemount_Provincial_Court_Provincial",
    "Vancouver_Provincial_Court_Provincial",
    "Vanderhoof_Law_Court_Provincial",
    "Vernon_Law_Court_Provincial",
    "Victoria_Law_Court_Provincial",
    "Violation_Ticket_Centre_Provincial",
    "Western_Communities_Provincial_Court_Provincial",
    "Williams_Lake_Law_Court_Provincial",
    "Campbell_River_Law_Court_Supreme",
    "Chilliwack_Law_Court_Supreme",
    "Courtenay_Law_Court_Supreme",
    "Cranbrook_Law_Court_Supreme",
    "Dawson_Creek_Law_Court_Supreme",
    "Duncan_Law_Court_Supreme",
    "Fort_Nelson_Law_Court_Supreme",
    "Fort_St_John_Law_Court_Supreme",
    "Golden_Law_Court_Supreme",
    "Kamloops_Law_Court_Supreme",
    "Kelowna_Law_Court_Supreme",
    "Nanaimo_Law_Court_Supreme",
    "Nelson_Law_Court_Supreme",
    "New_Westminster_Law_Court_Supreme",
    "Penticton_Law_Court_Supreme",
    "Port_Alberni_Law_Court_Supreme",
    "Port_Hardy_Law_Court_Supreme",
    "Powell_River_Law_Court_Supreme",
    "Prince_George_Law_Court_Supreme",
    "Prince_Rupert_Law_Court_Supreme",
    "Quesnel_Law_Court_Supreme",
    "Rossland_Law_Court_Supreme",
    "Salmon_Arm_Law_Court_Supreme",
    "Smithers_Law_Court_Supreme",
    "Terrace_Law_Court_Supreme",
    "Vancouver_Law_Court_Supreme",
    "Vernon_Law_Court_Supreme",
    "Victoria_Law_Court_Supreme",
    "Williams_Lake_Law_Court_Supreme"
}

# provincial small claim
psc_courts = {
    "Chilliwack_Law_Courts",
    "Duncan_Law_Courts",
    "Kamloops_Law_Courts",
    "Kitimat_Law_Courts",
    "McBride_Provincial_Court",
    "Nanaimo_Law_Courts",
    "New_Westminster_Law_Courts",
    "North_Vancouver_Provincial_Court",
    "Penticton_Law_Courts",
    "Port_Coquitlam_Provincial_Court",
    "Richmond_Provincial_Court",
    "Robson_Square_Provincial_Court",
    "Surrey_Provincial_Court",
    "Vanderhoof_Law_Courts",
    "Victoria_Law_Courts",
    "Western_Communities_Provincial_Court"
}

pscl_prefix = "https://justice.gov.bc.ca/cso/courtLists.do?&"

now = datetime.now() # current date and time
date_prefix = now.strftime("%Y-%m-%d_")

# build list of download urls
remote_documents = []
for accourt in pac_courts:

    # provincial small claims courts
    if include_daily_list:
        remote_documents.append((accourt, "https://justice.gov.bc.ca/courts/court-lists/criminal/lists/" + accourt + ".pdf"))

    if include_completed:
        remote_documents.append((accourt + "_Completed", "https://justice.gov.bc.ca/courts/court-lists/criminal/lists/" + accourt + "_Completed.pdf"))

if include_pscl:
    for psccourt in psc_courts:
        remote_documents.append((psccourt + "_PSCL", "https://justice.gov.bc.ca/cso/courtLists.do?listSelection=" + psccourt + ".pdf&courtType=PSCL"))

if verbose_output:
    print(len(remote_documents),"remote documents in list")

for entry in remote_documents:
    try:
        
        (name,url) = entry
        headers = {'user-agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0'}
        resp = requests.get(url, headers=headers)
        data = resp.content
            
        target_filename = filesystem_path + date_prefix + name + ".pdf" #basename(resp.url)
        
        if verbose_output:
            print("downloaded",target_filename,"-",len(data),"bytes")
        
        # hash the downloaded data
        m = hashlib.sha256()
        m.update(data)
        hash_downloaded = m.hexdigest()
        
        exists = False # until proven otherwise
        
        # if filename exists, open it and compare sha256 hash
        if (path.exists(target_filename)):
            try:
                f = open(target_filename, 'rb')
                m = hashlib.sha256()
                m.update(f.read())
                hash_existing = m.hexdigest()

                if (hash_downloaded == hash_existing):
                    if verbose_output: print("DEBUG:",target_filename,"exists in cache AND hashes match")
                    exists = True
                else:
                    if verbose_output: print("DEBUG:",target_filename,"exists in cache but hashes differ")
                    # assumed exists = False
                
            except Exception as err:
                if verbose_output: print("ERROR: unable to open", target_filename)
                pass # file doesnt exist
        
        # write to disk cache if does not exist or has changed
        if not exists:
            try:
                f = open(target_filename, "wb")
                f.write(data)
                f.close()
            except:
                if verbose_output: print("ERROR: unable to write", target_filename)

    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.read())