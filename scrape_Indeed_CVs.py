#!/usr/bin/env python

from urllib import request
from bs4 import BeautifulSoup
import sys
import sqlite3
import os
import argparse

BASE_SEARCH_URL = 'http://www.indeed.com/resumes?'
BASE_CV_URL = 'http://www.indeed.com'
class Jobs_model(): #{{{1
    def __init__(self,url): #{{{2
        '''Jobs Model class. Parses Jobs from indeed.co.uk and saves info.'''

def find_jobs(): #{{{1
    '''Get first n jobs from indeed.co.uk.
        If an arg isn't' needed, use 'None' instead.'''

class CV_model(): #{{{1
    # TODO: Section header either None or dict style 'header:','content'
    # TODO: Having one DV per CV is a stupid idea. How do I have a DB full
    # of CVs?
    def __init__(self,url): #{{{2
        '''CV Model class. Parses CV from indeed.co.uk and saves info.'''
        # create a SQLite3 database named with url id
        self.source_url = url
        page = request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        resume = soup.find(id='resume_body')
        self.intro_para = resume.find(id='basic_info_row')

        self.work_exp = resume.find(id='work-experience-items')
        self.edu_list = resume.find(id='education-items')
        self.additional_info = resume.find(id='additionalinfo-section')

        id = self.source_url.split('/r/')[1]
        name = ['CV_',id,'.db']
        DB_name = "".join(name)
        self.sqlite3_connect = sqlite3.connect(DB_name)
        self.sqlite3_cursor = self.sqlite3_connect.cursor()

    def print_intro(self): #{{{2
        self.sqlite3_cursor.execute('''CREATE TABLE intro
                                    (name text, content text)''')
        text = (self.intro_para.text,)
        self.sqlite3_cursor.execute("INSERT INTO intro VALUES ('Introduction',?)",text)
        self.sqlite3_connect.commit()
    def print_education(self): #{{{2
        self.sqlite3_cursor.execute('''CREATE TABLE edu
                                    (title text, school text, dates text)''')
        for item in self.edu_list: # insert a ROW per item
            title = item.find('p','edu_title').text
            text = item.find('div','edu_school').text
            dates = item.find('p','edu_dates').text
            #info = [repr(title),repr(text),repr(dates)]
            info = [(title),(text),(dates)]
            self.sqlite3_cursor.execute("INSERT INTO edu VALUES (?,?,?)",info)
        self.sqlite3_connect.commit()
    def print_additional(self): #{{{2
        self.sqlite3_cursor.execute('''CREATE TABLE addition
                                    (content text)''')
        try:
            text = (self.additional_info.text,)
        except AttributeError:
            pass
        else:
            self.sqlite3_cursor.execute("INSERT INTO addition VALUES (?)", text)
            self.sqlite3_connect.commit()
    def print_work_exp(self): # {{{2
        self.sqlite3_cursor.execute('''CREATE TABLE work_exp
                                        (title text, company text, dates text)''')
        for item in self.work_exp:
            try:
                title = item.find('p','work_title').text
                company = item.find('div','work_company').text
                dates = item.find('p','work_dates').text
            except AttributeError:
                pass
            else:
                info = [(title),(company),(dates)]
                self.sqlite3_cursor.execute("INSERT INTO work_exp VALUES (?,?,?)", info)
        self.sqlite3_connect.commit() # }}}2

def save_CV(url): #{{{1
        CV = CV_model(url)
        CV.print_intro()
        CV.print_education()
        CV.print_work_exp()
        CV.print_additional()
        CV.sqlite3_connect.close()

def find_CVs(n, job_desc, location, save ): #{{{1
    '''Get first n CVs from indeed.co.uk.
        If an arg isn't needed use 'None' instead.'''
    search_terms = [BASE_SEARCH_URL,'q=',job_desc,'&l=',location]
    cv_search_url = "".join(search_terms)
    page = request.urlopen(cv_search_url)
    soup = BeautifulSoup(page, 'html.parser')

    content = soup.findAll('div','sre-content')

    for cv in content[:n]: # print search results
        print('='*10)
        id = cv.find('a','app_link')['href']
        join = [BASE_CV_URL,id]
        url = "".join(join)
        print(url)
        for child in cv.children:
            print(child.text)
        print('='*10)

        if save == 'True':
            save_CV(url)

    #TODO: store found items in vars and convert to unicode.
    # Then print or store in SQL.


def main(): #{{{1
    '''URL has to be from indeed.co.uk of a CV.'''

    parser = argparse.ArgumentParser(description='Search URLs from indeed.co.uk'\
            ' and save them into SQLite3 database.')
    #TODO: find way to have url as an optional positional arg
    #parser.add_argument('url', help='Store a single CV in SQLite3 CV.db.')

    parser.add_argument('-u', '--url', help='Get a single CV from url')
    parser.add_argument('-S', '--search', help='Search first n CVs using search params',
            nargs=3, metavar=('n','job_desc','location'))
    parser.add_argument('--save', help='Adding the save flag will store results'\
            'to CV.db SQLite3 database.', action='store_true')

    #TODO: add a 4th optional arg to the search opt if poss
    # else just add an avoidURLs option.
    args = parser.parse_args()
    if args.url: #Get and Save single CV data from url
        save_CV(args.url)

    if args.search:
        find_CVs(int(args.search[0]),args.search[1],args.search[2],str(args.save))

if __name__ == '__main__':
    main()
