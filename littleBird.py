#!usr/bin/python3
"""
hw56@iu.edu
"""

from bs4 import BeautifulSoup
import requests
import re
import sre_yield
import time
import random
import json
from datetime import datetime

OUTPUTDIR = "./"
FILE_NAME = "URLs.json"
ERROR = "error_log.json"
REDIRCTIONS = "redirections.json"
DOMAIN = "https://learningenglish.voanews.com"
NULL_WEBSEITS = "null_websites.json"


def ymd2mdy(ymd):
    """
    transfer str '2009/1/2' to str 'January 02, 2009'
    """
    inter = re.match(r'(\d{4})/(\d+)/(\d+)', ymd)
    y = inter.group(1)
    m = inter.group(2)
    d = inter.group(3)
    m_reference = dict(
        [('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
         ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'),
         ('12', 'December')])
    m_n = m_reference[m]
    if len(d) == 1:
        d = '0' + d
    mdy = m_n + ' ' + d + ', ' + y
    return mdy


def candidate_date_generator():
    """
    candidate_dates describe start points, roughly from 1959/1/1 to 2019/12/31
    YYYY:(1959|19[6-9]\d|200\d|201[0-8])
    (M)M/(D)D: (([1-9]|1[0-2])/([1-9]|1[0-9]|2[0-8])|([13-9]|1[0-2])/(29|30)|([13578]|1[02])/31)
    then add 10 leap year with Feb. 29 (since 1959): 1960 1964 1968 1972 1976 1980 1984 1988 1992 1996 2000 2004 2008
    2012 2016
   """
    candidate_dates = list(
        sre_yield.AllStrings(
            r'(200[1-9]|201[0-9])/(([1-9]|1[0-2])/([1-9]|1[0-9]|2[0-8])|([13-9]|1[0-2])/(29|30)|([13578]|1[02])/31)'))
    leap_years = ['2004', '2008', '2012', '2016']
    leap_dates = [year + '/2/29' for year in leap_years]
    candidate_dates += leap_dates

    return candidate_dates


def popnull_and_sort(targets):
    # "result" is a list of dicts
    for dict in targets:
        if dict == {}:
            targets.remove(dict)
        if dict is None:
            targets.remove(dict)
    # pop out dicts have a vacant list as value
    result = [i for i in targets if list(i.values())[0] != []]

    # sort list by the order of dicts' key (ascending)
    # before sorting, let paddle yyyy(m)m(d)d with zeros
    # transfer candidate_date to standard yyyy/mm/dd format

    # use "log" to keep track of possible errors
    errors = []
    for dict in targets:
        formatting = ''
        try:
            formatting = re.match(r'(\d{4})/(\d+)/(\d+)', list(dict.keys())[0])
            yy = formatting.group(1)
            mm = formatting.group(2)
            dd = formatting.group(3)
            if len(mm) == 1:
                mm = '0' + mm
            if len(dd) == 1:
                dd = '0' + dd
            normalized = yy + "/" + mm + "/" + dd
            dict[normalized] = dict.pop(list(dict.keys())[0])
        except:
            errors.append(dict)

    result.sort(key=lambda x: datetime.strptime(list(x.keys())[0], "%Y/%m/%d").timestamp())

    return result, errors


def output_handler(result, file_name):
    with open(OUTPUTDIR + file_name, 'a') as f:
        json.dump(result, f)


def crawler(candidate_dates):
    # cats denote which categories an article belongs to
    cats = dict(AS_IT_IS="/z/3521/",
                ARTS_AND_CULTURE="/z/986/",
                AMERICAN_STORIES="/z/1581/",
                HEALTH_AND_LIFESTYLE="/z/955",
                U_S_HISTORY="/z/979/",
                SCIENCE_AND_TECHNOLOGY="/z/1579/",
                WHATS_TRENDING_TODAY="/z/4652/",
                WORDS_AND_THEIR_STORIES="/z/987/",
                AMERICAS_PRESIDENTS="/z/5091/")
    # redirections document dates pages that redirect the crawler
    # ("Sorry! No content for XXX. See content from before")
    redirections = []
    # targets used to contain desirable voa special english articles in nine categories
    targets = []
    # 用于记录那些不重定向，但是返回一个光秃秃的calendar的网站
    null_websites = []

    for candidate_date in candidate_dates:
        d = dict()
        d[candidate_date] = []
        time.sleep(random.randint(0, 1))
        for cat, sub_domain in cats.items():
            url_send = DOMAIN + sub_domain + candidate_date
            response = requests.get(url_send)
            if not response.history:
                soup = BeautifulSoup(response.content, 'lxml')
                try:
                    anchors = soup.find_all('span', {'class': "date"})
                    # d used to document the day has news
                    # some days may contain no news and give no redirection, so they can be reflected on the results
                    for anchor in anchors:
                        if anchor.get_text() == ymd2mdy(candidate_date):
                            # 这里有个trick：加个判断
                            # 找anchor的上数两个父节点，然后找个父节点的span
                            # 如果第一个返回的不是anchor本身（时间）
                            # 那么这就不是一个文章，而是一个audio或者video
                            if anchor.parent.parent.span == anchor:
                                d[candidate_date].append((anchor.parent.a.attrs['href'], cat,))
                except:
                    null_websites.append({candidate_date: [url_send, cat]})
            else:
                redirections.append({candidate_date: [url_send, cat]})
        if not d[candidate_date]:
            null_websites.append(d)
        else:
            targets.append(d)
    return targets, redirections, null_websites


def main():

    candidate_dates = candidate_date_generator()
    targets_redirctions_nulls = crawler(candidate_dates)

    targets_errors = popnull_and_sort(targets_redirctions_nulls[0])
    redirections = targets_redirctions_nulls[1]
    nulls = targets_redirctions_nulls[2]

    targets = targets_errors[0]
    errors = targets_errors[1]

    # store URLs
    output_handler(targets, FILE_NAME)
    # store redirections
    output_handler(redirections, REDIRCTIONS)
    #store error_log
    output_handler(errors, ERROR)
    # store websites has no information
    output_handler(nulls, NULL_WEBSEITS)


if __name__ == "__main__":
    main()
