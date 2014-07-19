import dryscrape
import re
import sys
import os

import numpy as np
import pandas as pd

sys.path.append('scrape')
from helpers import login_to_evaluations

UserID = 'S01149891'
PIN    = 'aaa12051992'

project_dir = '/Users/mdelhey/rice-scrape/'
YEAR_SCRAPE = '2013'
TERM_SCRAPE = 'Spring'

# Boilerplate
os.chdir(project_dir)
try: __file__
except: __file__ = 'repl'

# Create pandas df
data_evals = pd.DataFrame(None, columns=['crn', 'term', 'course', 'xlist', 'enrolled', 'instructor',
                                   'r_organization', 'r_assignments', 'r_quality', 'r_challenge',
                                   'r_workload', 'r_satisfies', 'r_grade', 'r_pf',
                                   'n_organization', 'n_assignments', 'n_quality', 'n_challenge',
                                   'n_workload', 'n_satisfies', 'n_grade', 'n_pf',
                                   'n_comments', 'comments'])

# set up a web scraping session
sess = dryscrape.Session(base_url = 'http://esther.rice.edu')

# OPPTIONS: no images, pretend to be firefox
sess.set_header('User-Agent', 'Chrome/36.0.1985.67')
sess.set_attribute('auto_load_images', False)

# Login & navigate to the right page
print '[%s] Visiting esther.rice.edu (Year: %s, Term: %s)' % (__file__, YEAR_SCRAPE, TERM_SCRAPE)
login_to_evaluations(UserID, PIN, sess, wait = 4)

sess.render('tmp.png')

# Loop through each subject/class
departs = []
classes = []
a = sess.xpath('//*[@id="crse_menu"]/td[2]/select/option')[1]

for d in sess.xpath('//*[@id="crse_menu"]/td[2]/select/option'):
    #departs.append(d['text'])
    departs.append(d.text())
    d.select_option()
    # Loop through each class
    c = sess.xpath('//*[@id="crse_menu"]/td[4]/select')[0]
    for c in sess.xpath('//*[@id="crse_menu"]/td[4]/select'):
        classes.append(c.text())
        # search (submit form)
        search_link = sess.at_xpath('//*[@id="includeone"]/table/tbody/tr[5]/td[1]/input')
        search_link.click()
        # grab data: term, course, enrolled, instructors, etc.
        row = { i: None for i in data_evals.columns }
        row['term'] = sess.at_xpath( '//*[@id="%s_p"]/td[1]/table/tbody/tr[1]/td[2]' % row['crn']).text()
        row['course'] = sess.at_xpath('//*[@id="%s_p"]/td[1]/table/tbody/tr[2]/td[2]' % row['crn']).text()
        row['enrolled'] = sess.at_xpath('//*[@id="%s_p"]/td[1]/table/tbody/tr[3]/td[2]' % row['crn']).text()
        row['instructor'] = sess.at_xpath('//*[@id="%s_p"]/td[1]/table/tbody/tr[4]/td[2]' % row['crn']).text()
        row['r_organization'] = sess.at_xpath('//*[@id="chart_%s_1_means"]' % row['crn']).text()
        row['n_organization'] = sess.at_xpath('//*[@id="chart_%s_1_response_total"]' % row['crn']).text()






# Loop through comments
num_comments_str = sess.at_xpath('//*[@id="20427"]/tbody/tr[6]/td/table/tbody/tr/td[3]').text()
num_comments = int(re.findall(r'[0-9]+', num_comments_str)[0])

comments = []
for cm in range(num_comments):
    cm_path = '//*[@id="comment_%s_%s"]' % (crn, str(cm + 1))
    cm_time_path = '//*[@id="comment_time_%s_%s"]' % (crn, str(cm + 1))
    tup = (sess.at_xpath(cm_time_path).text(), sess.at_xpath(cm_path).text())
    comments.append(tup)


# pick statistics
subj_link = sess.at_xpath('//*[@id="crse_menu"]/td[2]/select/option[80]')
subj_link.select_option()

# pick stat310
class_link = sess.at_xpath('//*[@id="crse_menu"]/td[4]/select/option[8]')
class_link.select_option()




    

    

sess.render('tmp.png')
