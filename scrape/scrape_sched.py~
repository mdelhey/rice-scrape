import dryscrape
import sqlalchemy
import os
import time
import sys

import numpy as np
import pandas as pd

NetID = 'mjd2'
Password = 'aa7707958159'

project_dir = '/Users/mdelhey/rice-scrape/'
YEAR_SCRAPE = '2013'
TERM_SCRAPE = 'Spring'

dbuser = 'mdelhey'
dbname = 'ricedb'
dbhost = 'localhost'

tbl_out = 't_evaluations_raw'
tbl_action = 'replace'  # replace / append / fail

f_out = 'data/evals_tmp.csv'

# Boilerplate
os.chdir(project_dir)
from helpers import try_row_scrape
from helpers import login_to_sched
try: __file__
except: __file__ = 'repl'

# get crn's from sql
rdb_con = sqlalchemy.create_engine('postgresql://%s@%s/%s' % (dbuser, dbhost, dbname))
qry = """ select * from t_courses_raw2 where year = '%s' and term = '%s'; """  % (YEAR_SCRAPE, TERM_SCRAPE)
data_courses = pd.read_sql(qry, rdb_con)

# Setup dataframe
eval_cols = ['courseid', 'yearterm', 'year', 'term', 'crn', 'instructor', 'r_organization',
             'r_assignments', 'r_quality', 'r_challenge', 'r_workload', 'r_satisfies', 'r_grade',
             'r_pf', 'n_organization', 'n_assignments', 'n_quality', 'n_challenge', 'n_workload',
             'n_satisfies', 'n_grade', 'n_pf', 'raw_title', 'raw_comments']
data_evals = pd.DataFrame(None, columns=eval_cols)

#comment_cols = ['courseid', 'yearterm', 'year', 'term', 'crn', 'instructor', 'n_comments', 'comment']
#data_comments = pd.DataFrame(None, columns=comment_cols)

# set up a web scraping session
sess = dryscrape.Session(base_url = 'http://scheduleplanner.rice.edu/')

# we don't need images
sess.set_attribute('auto_load_images', False)

# visit courses.rice.edu
print '[%s] Visiting scheduleplanner.rice.edu' % __file__
sess.visit('/')

# visit arbitrary page to login
print '[%s] Logging in to scheduleplanner' % __file__
login_to_sched(NetID, Password, sess)

# Determine term code
if TERM_SCRAPE == 'Fall':
    p_term = str(int(YEAR_SCRAPE) + 1) + '10'
if TERM_SCRAPE == 'Spring':
    p_term = str(int(YEAR_SCRAPE)) + '20'
if TERM_SCRAPE == 'Summer':
    p_term = str(int(YEAR_SCRAPE)) + '30'

# Conver to list
crns = list(data_courses['crn'].astype(int))
crns = crns[0:25]

# time scrape
start_time = time.time()

# Loop through crn's and scrape
print '[%s] Scraping evaluations for %i classes' % (__file__, len(crns))
for idx,c in enumerate(crns):
    if ((idx % 50) == 0): print '[%s] ... Class %i' % (__file__, idx)

    # Generate link, navigate to it
    url = '/wsSchedule/Account/CourseEvals.aspx?H=%s&T=%s' % (c, p_term)
    #print url
    sess.visit(url)
    #sess.render('tmp.png')

    # Insert basic data
    row = { i: None for i in data_evals.columns }
    row['yearterm'] = YEAR_SCRAPE + ' ' + TERM_SCRAPE
    row['term']     = TERM_SCRAPE
    row['year']     = YEAR_SCRAPE
    row['crn']      = c
    row['courseid'] = row['yearterm'] + '_' + str(row['crn'])

    row['instructor']     = try_row_scrape('//*[@id="lblInstructor"]', sess)
    row['r_organization'] = try_row_scrape('//*[@id="lblClassMean1"]', sess)
    row['n_organization'] = try_row_scrape('//*[@id="lblResponses1"]', sess)
    row['r_assignments']  = try_row_scrape('//*[@id="lblClassMean2"]', sess)
    row['n_assignments']  = try_row_scrape('//*[@id="lblResponses2"]', sess)
    row['r_quality']      = try_row_scrape('//*[@id="lblClassMean3"]', sess)
    row['n_quality']      = try_row_scrape('//*[@id="lblResponses3"]', sess)
    row['r_challenge']    = try_row_scrape('//*[@id="lblClassMean4"]', sess)
    row['n_challenge']    = try_row_scrape('//*[@id="lblResponses4"]', sess)
    row['r_workload']     = try_row_scrape('//*[@id="lblClassMean5"]', sess)
    row['n_workload']     = try_row_scrape('//*[@id="lblResponses5"]', sess)
    row['r_satisfies']    = try_row_scrape('//*[@id="lblClassMean6"]', sess)
    row['n_satisfies']    = try_row_scrape('//*[@id="lblResponses6"]', sess)
    row['r_grade']        = try_row_scrape('//*[@id="lblClassMean7"]', sess)
    row['n_grade']        = try_row_scrape('//*[@id="lblResponses7"]', sess)
    row['r_pf']           = try_row_scrape('//*[@id="lblClassMean8"]', sess)
    row['n_pf']           = try_row_scrape('//*[@id="lblResponses8"]', sess)
    row['raw_title']      = try_row_scrape('//*[@id="lblTitle"]', sess)
    row['raw_comments']   = try_row_scrape('//*[@id="gvEvalsComments"]/tbody', sess)
    
    # append row
    data_evals = data_evals.append(row, ignore_index=True)


print '[%s] scrape took %.2f minutes' % (__file__, (time.time() - start_time)/60)

print '[%s] saving csv to %s' % (__file__, f_out)
data_evals.to_csv(f_out, index=False)

print '[%s] saving (action = %s) to postgres (table = %s)' % (__file__, tbl_action, tbl_out)
rdb_con = sqlalchemy.create_engine('postgresql://%s@%s/%s' % (dbuser, dbhost, dbname))
data_evals.to_sql(tbl_out, rdb_con, if_exists = tbl_action, index = False)
