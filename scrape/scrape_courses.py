import dryscrape
import sqlalchemy
import time
import re
import os

import numpy as np
import pandas as pd

project_dir = '/Users/mdelhey/rice-scrape/'
YEAR_SCRAPE = '2013'
TERM_SCRAPE = 'Spring'

dbuser = 'mdelhey'
dbname = 'ricedb'
dbhost = 'localhost'

tbl_out = 't_courses_raw2'
tbl_action = 'replace'  # replace / append / fail

f_out = 'data/courses_tmp.csv'

# Set dir; see if we're running a file
os.chdir(project_dir)
try: __file__
except: __file__ = 'repl'

# Create pandas df
data = pd.DataFrame(None, columns=['courseid', 'yearterm', 'year', 'term', 'crn', 'course', 'title', 'faculty', 'meeting', 'credits', 'enrolled', 'raw'])

# set up a web scraping session
sess = dryscrape.Session(base_url = 'http://courses.rice.edu/')

# we don't need images
sess.set_attribute('auto_load_images', False)

# visit courses.rice.edu
sess.visit('/')

# visit full course page
print '[%s] Visiting courses.rice.edu (Year: %s, Term: %s)' % (__file__, YEAR_SCRAPE, TERM_SCRAPE)
if TERM_SCRAPE == 'Fall': term_code = '10'
if TERM_SCRAPE == 'Spring': term_code = '20'
if TERM_SCRAPE == 'Summer': term_code = '30'
p_term = str(int(YEAR_SCRAPE) + 1) + term_code
sess.visit('/admweb/!SWKSCAT.cat?p_action=QUERY&p_term=%s&p_name=STATIC' % p_term)
#sess.render('tmp.png')

# get a list of all crn's
print "[%s] Getting all CRN's" % (__file__)
classes = []
for c in sess.xpath('//*[@id="container"]/div[3]/table/tbody/tr[*]/td[1]/a'):
    classes.append(c.text())
classes = classes[0:10]

# time function
start_time = time.time()

# helper function for try/except
def try_row_scrape(xpath):
    try: x = sess.at_xpath(xpath).text()
    except: x = None
    return x

# Loop through all
print '[%s] Scraping %s classes' % (__file__, str(len(classes)))
for idx,c in enumerate(classes):
    if ((idx % 100) == 0): print '[%s] ... Class %s' % (__file__, str(idx))
        
    # get link, navigate to it
    link = '/admweb/!SWKSCAT.cat?p_action=COURSE&p_term=201510&p_crn=%s' % str(c)
    sess.visit(link)
    
    # grab data: term, course, enrolled, instructors, etc.
    row = { i: None for i in data.columns }
    row['yearterm'] = YEAR_SCRAPE + ' ' + TERM_SCRAPE
    row['term'] = TERM_SCRAPE
    row['year'] = YEAR_SCRAPE
    row['crn'] = c
    row['courseid'] = row['yearterm'] + '_' + str(row['crn'])

    row['course'] = try_row_scrape('//*[@id="container"]/div[3]/div/table/tbody/tr[1]/td[2]')
    row['title'] = try_row_scrape('//*[@id="container"]/div[3]/div/table/tbody/tr[1]/td[3]')
    row['faculty'] = try_row_scrape('//*[@id="container"]/div[3]/div/table/tbody/tr[2]/td[3]')
    row['meeting'] = try_row_scrape('//*[@id="container"]/div[3]/div/table/tbody/tr[3]/td[3]')
    row['credits'] = try_row_scrape('//*[@id="container"]/div[3]/div/table/tbody/tr[1]/td[4]')
    row['enrolled'] = try_row_scrape('//*[contains(text(), "Enrolled")]')
    row['raw'] = try_row_scrape('//*[@id="container"]/div[3]/div')
        
    # append row
    data = data.append(row, ignore_index=True)
    
    
print '[%s] scrape took %s minutes' % (__file__, str((time.time() - start_time)/60))

print '[%s] saving csv to %s' % (__file__, f_out)
data.to_csv(f_out, index=False)

print '[%s] saving (action = %s) to postgres (table = %s)' % (__file__, tbl_action, tbl_out)
rdb_con = sqlalchemy.create_engine('postgresql://%s@%s/%s' % (dbuser, dbhost, dbname))
data.to_sql(tbl_out, rdb_con, if_exists = tbl_action, index = False)
