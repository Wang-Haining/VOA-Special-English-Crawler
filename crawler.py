#!usr/bin/python3
"""
hw56@iu.edu
"""


from bs4 import BeautifulSoup
import urllib.request
from urllib.request import urlopen
import re
import sre_yield
import time
import random
import json
import argparse
from datetime import datetime


def check_redirect(url):
    """
    determine whether the website redirects my request
    """
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko')
    response = urllib.request.urlopen(req)
    new_url = response.geturl()
    return new_url


def ymd2mdy(ymd):
    """
    transfer str '2009/1/2' to str 'January 02, 2009'
    """
    inter = re.match(r'(\d{4})/(\d+)/(\d+)', ymd)
    y = inter.group(1)
    m = inter.group(2)
    d = inter.group(3)
    m_reference = dict([('1','January'), ('2','February'), ('3','March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
                        ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'),
                        ('12', 'December')])
    m_n = m_reference[m]
    if len(d) == 1:
        d = '0' + d

    mdy = m_n + ' ' + d + ', ' + y

    return mdy


def candidate_date_handler():
    """

    candidate_dates describe start points, roughly from 1959/1/1 to 2019/12/31
    YYYY:(1959|19[6-9]\d|200\d|201[0-8])
    (M)M/(D)D: (([1-9]|1[0-2])/([1-9]|1[0-9]|2[0-8])|([13-9]|1[0-2])/(29|30)|([13578]|1[02])/31)
    then add 10 leap year with Feb. 29 (since 1959): 1960 1964 1968 1972 1976 1980 1984 1988 1992 1996 2000 2004 2008
    2012 2016
   """

    candidate_dates = []
    leap_dates = []
    candidate_dates = list(
        sre_yield.AllStrings(
        r'(1959|19[6-9]\d|200\d|201[0-8])/(([1-9]|1[0-2])/([1-9]|1[0-9]|2[0-8])|([13-9]|1[0-2])/(29|30)|([13578]|1[02])/31)'))
    leap_years = ['1960', '1964', '1968', '1972', '1976', '1980','1984', '1988', '1992', '1996', '2000', '2004', '2008',
     '2012', '2016']
    leap_dates = [year + '/2/29' for year in leap_years]
    candidate_dates += leap_dates

    return candidate_dates


def popnull_and_sort(result):
    # "result" is a list of dicts
    for dict in result:
        if dict == {}:
            result.remove(dict)
    # pop out dicts have a vacant list as value
    result = [i for i in result if list(i.values())[0] != []]

    # sort list by the order of dicts' key (ascending)
    # befor sorting, let paddle yyyy(m)m(d)d with zeros
    # transfer candidate_date to standard yyyy/mm/dd format

    for dict in result:
        formatting = ''
        formatting = re.match(r'(\d{4})(\d+)(\d+)', list(dict.keys())[0])
        yy = formatting.group(1)
        mm = formatting.group(2)
        dd = formatting.group(3)
        if len(mm) == 1:
            mm = '0' + mm
        if len(dd) == 1:
            dd = '0' + dd
        normalized = yy + "/" + mm + "/" + dd
        dict[normalized] = dict.pop(list(dict.keys())[0])

    result.sort(key=lambda x: datetime.strptime(list(x.keys())[0], "%Y/%m/%d").timestamp())

    return result


def output_handler(result, outputdir):
    """

    """
    output = json.dumps(result)
    with open(outputdir, 'a') as f:
        json.dump(output, f)



def crawler():

    candidate_dates = candidate_date_handler()
    # nothing_dates document dates pages that redirect the scrawler
    # ("Sorry! No content for XXX. See content from before")
    nothing_dates = []
    # targets used to contain desired voa special english articles
    # ("Every day Grammar" and other 13 types of articles URLs are documented as a list)
    targets = []

    for candidate_date in candidate_dates:
        time.sleep(random.randint(0, 3))
        url_send = 'https://learningenglish.voanews.com/z/952/' + candidate_date
        url_detect = check_redirect(url_send)
        if url_send == url_detect:
            html = urlopen(url_send)
            soup = BeautifulSoup(html, 'lxml')
            anchors = soup.find_all('span', {'class': "date"})
            # d used to document the day has news
            # some days may contain no news and give no redirection, so they can be reflected on the results
            d = dict()
            d[candidate_date] = []
            for anchor in anchors:
                if anchor.get_text() == ymd2mdy(candidate_date):
                    d[candidate_date].append(anchor.parent.a.attrs['href'])
            targets.append(d)

        else:
            nothing_dates.append({candidate_date: [url_send, url_detect]})

    return [targets, nothing_dates]


def main():

    parser = argparse.ArgumentParser(description="Let's crawl VOA Special English.")
    parser.add_argument('-o', action='store', help='Path to output directory')
    args = vars(parser.parse_args())

    outputdir = args['o']

    results = crawler()
    # here, I won't print the redirections, they are stored in results[1]
    output_handler(popnull_and_sort(results[0]), outputdir)

if __name__ == "__main__":

    main()







