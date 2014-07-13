import dryscrape
import time
import re

import numpy as np
import pandas as pd

UserID = 
PIN    =

# Create pandas df
data = pd.DataFrame(None, columns=['crn', 'term', 'course', 'xlist', 'enrolled', 'instructor',
                                   'r_organization', 'r_assignments', 'r_quality', 'r_challenge',
                                   'r_workload', 'r_satisfies', 'r_grade', 'r_pf',
                                   'n_organization', 'n_assignments', 'n_quality', 'n_challenge',
                                   'n_workload', 'n_satisfies', 'n_grade', 'n_pf',
                                   'n_comments', 'comments'])

# set up a web scraping session
sess = dryscrape.Session(base_url = 'http://esther.rice.edu')

# we don't need images
sess.set_attribute('auto_load_images', False)

def login_to_evaluations(UserID, PIN, wait=2):
    # visit esther
    sess.visit('/')
    sleep.time(wait)

    # click on login
    login_link = sess.at_xpath('//*[@id="rice_content_fixed"]/div/h3/a')
    sleep.time(wait)
    login_link.click()

    # login
    UserID_field = sess.at_xpath('//*[@id="UserID"]')
    UserID_field.set(UserID)
    time.sleep(wait)
    
    PIN_field = sess.at_xpath('//*[@id="PIN"]/input')
    PIN_field.set(PIN)
    time.sleep(wait)
    
    UserID_field.form().submit()

    # click on Student Services
    services_link =  sess.at_xpath('//*[contains(text(), "Student Services & Account Information")]')
    time.sleep(wait)
    services_link.click()

    # click on Evaluation Results
    evaluation_link = sess.at_xpath('/html/body/div[3]/table[1]/tbody/tr[7]/td[2]/a')
    time.sleep(wait)
    evaluation_link.click()

    # click on proceed to evaluations
    proceed_link = sess.at_xpath('/html/body/div[3]/table[2]/tbody/tr/td/input[2]')
    time.sleep(wait)
    proceed_link.click()

    return None

login_to_evaluations(UserID, PIN)

# pick statistics
subj_link = sess.at_xpath('//*[@id="crse_menu"]/td[2]/select/option[80]')
subj_link.select_option()

# pick stat310
class_link = sess.at_xpath('//*[@id="crse_menu"]/td[4]/select/option[8]')
class_link.select_option()

# search (submit form)
search_link = sess.at_xpath('//*[@id="includeone"]/table/tbody/tr[5]/td[1]/input')
search_link.click()

# grab data: term, course, enrolled, instructors, etc.
row = { i: None for i in data.columns }
row['crn'] = '20427'
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

    

# Loop through each class
classes = []
for c in sess.xpath('//*[@id="crse_menu"]/td[4]/select/option'):
    a = c
    classes.append(c['value'])

# Loop through each subject
subjects = []
for s in sess.xpath('//*[@id="crse_menu"]/td[2]/select/option'):
    subjects.append(s['value'])
    

sess.render('tmp.png')
