# Command Line Arguments #

-t, --today ; search only today

-q, --quiet ; quiet output

-c, --cacheonly ; search only cache

# Example Usage #

`
user@host:/opt/courtlists$ ./court_lists_process.py
Search mode: pdf documents and cache
Search list: /opt/osint/cso-searchlist.json
Search path: /opt/osint/data/courtlists/
Results path: /opt/osint/data/courtlists_hits/
found 89238 court lists (89193 cached)
FOUND DOE, JOHN in 2019-03-28-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-03-26-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2017-04-17-Justice_Centre_(Judicial)_Provincial.pdf
FOUND DOE, JOHN in 2017-06-19-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-07-12-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-10-02-Downtown_Community_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-10-23-Downtown_Community_Court_Provincial.pdf
FOUND DOE, JOHN in 2018-08-04-Justice_Centre_(Judicial)_Provincial.pdf
FOUND DOE, JOHN in 2019-10-23-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-06-13-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-02-11-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-09-10-Downtown_Community_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-10-15-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-10-12-Justice_Centre_(Judicial)_Provincial.pdf
FOUND DOE, JANE in 2018-08-28-Kelowna_Law_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-02-08-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2018-08-06-Justice_Centre_(Judicial)_Provincial.pdf
FOUND DOE, JOHN in 2019-05-27-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-05-08-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2017-05-01-Victoria_Law_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-03-27-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-09-09-Downtown_Community_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-05-28-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2017-06-18-Justice_Centre_(Judicial)_Provincial.pdf
FOUND DOE, JOHN in 2019-10-24-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-06-27-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JANE in 2019-02-06-Kelowna_Law_Court_Provincial.pdf
FOUND DOE, JOHN in 2018-10-06-Justice_Centre_(Judicial)_Provincial.pdf
FOUND DOE, JOHN in 2019-09-06-Downtown_Community_Court_Provincial.pdf
FOUND DOE, JOHN in 2018-08-08-Downtown_Community_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-11-04-Downtown_Community_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-05-26-Justice_Centre_(Judicial)_Provincial.pdf
FOUND DOE, JOHN in 2018-08-05-Justice_Centre_(Judicial)_Provincial.pdf
FOUND DOE, JOHN in 2019-04-02-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JANE in 2018-08-23-Kelowna_Law_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-04-16-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2017-04-16-Justice_Centre_(Judicial)_Provincial.pdf
FOUND DOE, JOHN in 2019-03-04-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-06-17-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-04-03-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-04-15-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-05-29-Vancouver_Provincial_Court_Provincial.pdf
FOUND DOE, JOHN in 2019-04-09-Vancouver_Provincial_Court_Provincial.pdf
Completed. Searched 89238 files in 75.0 seconds (0.84 msecs average per document)
Error reading 45 files (0.1%)
`