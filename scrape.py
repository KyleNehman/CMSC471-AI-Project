import os
import re
import sys
import time 
import requests
from bs4 import BeautifulSoup

base_url = "https://www.ted.com/talks?sort=newest&q="

shitList = ["RichardPyle_2004.sph", ""]

def str_contains_num(str):
    return any(char.isdigit() for char in str)

def get_all_before_num(str):
    if not str_contains_num(str):
        return str

    ret = ""
    for char in str:
        if not char.isdigit() and char != '_':
            ret += char
        else:
            return ret

    return ret

# Assumes speaker name is between >< 
# e.g. <h4 class="h12 talk-link__speaker">Peter Molyneux</h4>
def get_speaker(str):
    flag = False
    returnVal = ""

    for c in str:
        if flag:
            if c != '<':
                returnVal += c
            else:
                break
        else:
            flag = (c == '>')

    return returnVal

def get_year(filename):
    returnVal = ""

    for c in filename:
        if c.isdigit():
            returnVal += c
        else:
            if returnVal != "":
                break

    return returnVal

def search(filename):
    splitted = re.sub('(?!^)([A-Z][a-z]+)', r' \1', filename).split()
    url_args = ""

    for s in splitted:
        url_args += get_all_before_num(s) + "+"

    url = base_url + str(url_args[0:-1])
    print(filename + "(" + get_year(filename) + ") - " + url)
    req = requests.get(url)

    data = req.text
    soup = BeautifulSoup(data, "html.parser")

    #l = soup.find_all("a", {"class": "ga-link", "data-ga-context": "talks"});
    l = soup.find_all("div", {"class": "media__message"});

    # List of tuples (author, title, year)
    talks = []
    
    for i in l:
        for c in i.contents:    
            num_talks = len(talks)
            line = str(c)
            tup = []
            if num_talks >= 1:
                tup = talks[num_talks - 1]

            #debug
            #print(c)

            # No tuples or need new tuple
            if num_talks == 0 or len(talks[num_talks - 1]) == 3:
                if "speaker" in line:
                    speaker = get_speaker(line)
                    tup = []
                    talks.append([])
                    tup.append(speaker)

            # Has only a name
            elif len(talks[num_talks - 1]) == 1:
                lines = line.split('\n')
                for name in lines:
                    if len(name) > 0 and name[0] != '<':
                        tup.append(name)

            # Needs year after "Posted"
            elif len(talks[num_talks - 1]) == 2:
                posted = False
                for field in line.split("\n"):
                    if posted and field[0] != '<': 
                        tup.append(field)
                        posted = False
                    
                        if str(get_year(filename)) not in field:
                            print("Years dont match")
                            tup = [None]
    
                    elif "Posted" in str(field):
                        posted = True

            # Apparently I can't do this inline. Reason 1932 I dislike python
    
            if tup != []:
                talks = talks[:-1]
                if tup != [None]:
                    talks.append(tup)
    print(talks)
    print("\n")
    sys.stdout.flush()

    return talks

def main():
    count = 0
    for filename in os.listdir("filenames"):
    #for filename in ["MarvinMinsky_2003.sph"]:
        if filename in shitList:
            continue

        whole = ""
        flag = False
        for tup in search(filename):
            if tup != []:
                flag = True
                whole += str(tup) + " "
                
        time.sleep(2)
        if flag:
            count += 1
    print("Count: " + str(count))

main()
