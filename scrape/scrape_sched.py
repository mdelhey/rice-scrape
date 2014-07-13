import dryscrape
import sqlalchemy
import os

import numpy as np
import pandas as pd

project_dir = '/Users/mdelhey/rice-scrape/'
YEAR_SCRAPE = '2013'
TERM_SCRAPE = 'Spring'

dbuser = 'mdelhey'
dbname = 'ricedb'
dbhost = 'localhost'

tbl_out = 't_course_evaluations'
tbl_action = 'replace'  # replace / append / fail

f_out = 'data/evals_tmp.csv'

# Set dir; see if we're running a file
os.chdir(project_dir)
try: __file__
except: __file__ = 'repl'

# get crn's from sql
rdb_con = sqlalchemy.create_engine('postgresql://%s@%s/%s' % (dbuser, dbhost, dbname))
qry = """ select * from t_courses_raw2 where year = '%s' and term = '%s'; """  % (YEAR_SCRAPE, TERM_SCRAPE)
data_courses = pd.read_sql(qry, rdb_con)

# Setup dataframe
data_evals = pd.DataFrame(None, columns=['courseid', 'yearterm', 'year', 'term', 'crn', 'instructor',
                                        'r_organization', 'r_assignments', 'r_quality', 'r_challenge',
                                        'r_workload', 'r_satisfies', 'r_grade', 'r_pf',
                                        'n_organization', 'n_assignments', 'n_quality', 'n_challenge',
                                        'n_workload', 'n_satisfies', 'n_grade', 'n_pf',
                                        'n_comments', 'n_comments'])
data_comments = pd.DataFrame(None, columns=['courseid', 'yearterm', 'year', 'term', 'crn', 'instructor',
                                            'n_comments', 'comment'])

# set up a web scraping session
sess = dryscrape.Session(base_url = 'http://scheduleplanner.rice.edu/')

# we don't need images
sess.set_attribute('auto_load_images', False)

# visit courses.rice.edu
print '[%s] Visiting scheduleplanner.rice.edu' % __file__
sess.visit('/')

# Determine term code
if TERM_SCRAPE == 'Fall': term_code = 10
if TERM_SCRAPE == 'Spring': term_code = 20
if TERM_SCRAPE == 'Summer': term_code = 30
p_term = str(int(YEAR_SCRAPE) + 1) + str(term_code)

# Conver to list
crns = list(data_courses['crn'].astype(int))

def try_row_scrape(xpath):
    try: x = sess.at_xpath(xpath).text()
    except: x = None
    return x

# Loop through crn's and scrape
c = crns[10]
print '[%s] Scraping evaluations for %s classes' % (__file__, str(len(crns)))
for idx,c in enumerate(crns):
    if ((idx % 100) == 0): print '[%s] ... Class %s' % (__file__, str(idx))

    # Generate link, navigate to it
    url = '/wsSchedule/Account/CourseEvals.aspx?H=%s&T=%s' % (str(c), p_term)
    sess.visit(url)

    # Insert basic data
    row = { i: None for i in data_evals.columns }
    row['yearterm'] = YEAR_SCRAPE + ' ' + TERM_SCRAPE
    row['term'] = TERM_SCRAPE
    row['year'] = YEAR_SCRAPE
    row['crn'] = c
    row['courseid'] = row['yearterm'] + '_' + str(row['crn'])

    row['instructor'] = try_row_scrape('//*[@id="lblInstructor"]')

    row['r_organization'] = try_row_scrape('//*[@id="lblClassMean1"]')
    row['n_organization'] = try_row_scrape('//*[@id="lblResponses1"]')
    row['r_assignments'] = try_row_scrape('//*[@id="lblClassMean2"]')
    row['n_assignments'] = try_row_scrape('//*[@id="lblResponses2"]')
    row['r_quality'] = try_row_scrape('//*[@id="lblClassMean3"]')
    row['n_quality'] = try_row_scrape('//*[@id="lblResponses3"]')
    row['r_challenge'] = try_row_scrape('//*[@id="lblClassMean4"]')
    row['n_challenge'] = try_row_scrape('//*[@id="lblResponses4"]')
    row['r_workload'] = try_row_scrape('//*[@id="lblClassMean5"]')
    row['n_workload'] = try_row_scrape('//*[@id="lblResponses5"]')
    row['r_satisfies'] = try_row_scrape('//*[@id="lblClassMean6"]')
    row['n_satisfies'] = try_row_scrape('//*[@id="lblResponses6"]')
    row['r_grade'] = try_row_scrape('//*[@id="lblClassMean7"]')
    row['n_grade'] = try_row_scrape('//*[@id="lblResponses7"]')
    row['r_pf'] = try_row_scrape('//*[@id="lblClassMean8"]')
    row['n_pf'] = try_row_scrape('//*[@id="lblResponses8"]')

    tst = sess.at_xpath('//*[@id="gvEvalsComments"]/tbody').text()
    
    # append row
    data_evals = data_evals.append(row, ignore_index=True)






            
    //*[@id="gvEvalsComments"]/tbody/tr[26]
                                        'r_organization', 'r_assignments', 'r_quality', 'r_challenge',
                                        'r_workload', 'r_satisfies', 'r_grade', 'r_pf',
                                        'n_organization', 'n_assignments', 'n_quality', 'n_challenge',
                                        'n_workload', 'n_satisfies', 'n_grade', 'n_pf',
                                        'n_comments', 'n_comments'])
    
#sess.render('tmp.png')    
#http://scheduleplanner.rice.edu/wsSchedule/Account/CourseEvals.aspx?H=14483&T=201410
