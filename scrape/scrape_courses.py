import dryscrape
import time
import re
import os

import numpy as np
import pandas as pd

import sqlalchemy

project_dir = '/Users/mdelhey/rice-scrape/'
TERM_SCRAPE = 'Fall 2014'

dbuser = 'mdelhey'
dbname = 'ricedb'
dbhost = 'localhost'

tbl_out = 't_courses_raw2'
tbl_action = 'replace'  # replace / append / fail

f_out = 'data/courses_tmp.csv'

# Set dir
os.chdir(project_dir)

# Create pandas df
data = pd.DataFrame(None, columns=['term', 'crn', 'course', 'title', 'faculty', 'meeting', 'credits', 'enrolled'])

    # set up a web scraping session
sess = dryscrape.Session(base_url = 'http://courses.rice.edu/')

# we don't need images
sess.set_attribute('auto_load_images', False)

# visit courses.rice.edu
sess.visit('/')
#sess.render('tmp.png')

# visit phil
print '[%s] Visiting courses.rice.edu' % (__file__)
#sess.visit('http://courses.rice.edu/admweb/!SWKSCAT.cat?p_action=QUERY&p_term=201510&p_name=&p_title=&p_instr=&p_subj=PHIL&p_spon_coll=&p_df=&p_ptrm=&p_mode=AND')
# visit full page
sess.visit('/admweb/!SWKSCAT.cat?p_action=QUERY&p_term=201510&p_name=STATIC')

# get a list of all crn's
print "[%s] Getting all CRN's" % (__file__)
classes = []
for c in sess.xpath('//*[@id="container"]/div[3]/table/tbody/tr[*]/td[1]/a'):
    classes.append(c.text())
classes = classes[0:10]

# time function
start_time = time.time()

# Loop through all
print '[%s] Scraping %s classes' % (__file__, str(len(classes)))
for idx,c in enumerate(classes):
    if ((idx % 100) == 0): print '[%s] ... Class %s' % (__file__, str(idx))
        
    # get link, navigate to it
    link = '/admweb/!SWKSCAT.cat?p_action=COURSE&p_term=201510&p_crn=%s' % str(c)
    sess.visit(link)
    
    # grab data: term, course, enrolled, instructors, etc.
    row = { i: None for i in data.columns }
    row['term'] = TERM_SCRAPE
    row['crn'] = c
    
    try: row['course'] = sess.at_xpath('//*[@id="container"]/div[3]/div/table/tbody/tr[1]/td[2]').text()
    except: row['courses'] = None
        
    try: row['title'] = sess.at_xpath('//*[@id="container"]/div[3]/div/table/tbody/tr[1]/td[3]').text()
    except: row['title'] = None
    
    try: row['faculty'] = sess.at_xpath('//*[@id="container"]/div[3]/div/table/tbody/tr[2]/td[3]').text()
    except: row['faculty'] = None
        
    try: row['meeting'] = sess.at_xpath('//*[@id="container"]/div[3]/div/table/tbody/tr[3]/td[3]').text()
    except: row['meeting'] = None
        
    try: row['credits'] = sess.at_xpath('//*[@id="container"]/div[3]/div/table/tbody/tr[1]/td[4]').text()
    except: row['credits'] = None
        
    try: row['enrolled'] = sess.at_xpath('//*[contains(text(), "Enrolled")]').text()
    except: row['enrolled'] = None
        
    # append row
    data = data.append(row, ignore_index=True)
    
    
print '[%s] scrape took %s minutes' % (__file__, str((time.time() - start_time)/60))

print '[%s] saving csv to %s' % (__file__, f_out)
data.to_csv(f_out, index=False)

print '[%s] saving (action = %s) to postgres (table = %s)' % (__file__, tbl_action, tbl_out)
rdb_con = sqlalchemy.create_engine('postgresql://%s@%s/%s' % (dbuser, dbhost, dbname))
data.to_sql(tbl_out, rdb_con, if_exists = tbl_action, index = False)
