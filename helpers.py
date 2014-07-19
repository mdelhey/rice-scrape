def try_row_scrape(xpath, sess):
    try: x = sess.at_xpath(xpath).text()
    except: x = None
    return x

def login_to_sched(NetID, Password, sess, wait=3):
    import time

    # Visit arbitrary page to init login page
    sess.visit('/wsSchedule/Account/CourseEvals.aspx?H=21560&T=201420')

    # Login using givin credentials
    NetID_field = sess.at_xpath('//*[@id="username"]')
    NetID_field.set(NetID)
    time.sleep(wait)
    Password_field = sess.at_xpath('//*[@id="password"]')
    Password_field.set(Password)
    time.sleep(wait)
    login_button = sess.at_xpath('//*[@id="fm1"]/div[4]/input[4]')
    login_button.click()

    return None


def login_to_evaluations(UserID, PIN, sess, wait=2):
    import time, sys
    
    # visit esther
    sess.visit('/')
    time.sleep(wait)

    # click on login
    login_link = sess.at_xpath('//*[@id="rice_content_fixed"]/div/h3/a')
    time.sleep(wait)
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
    try: services_link.click()
    except: sys.exit("""Couldn't click services link. Likely a bad login.""")

    # click on Evaluation Results
    evaluation_link = sess.at_xpath('//*[contains(text(), "Course and Instructor Evaluation Results")]')
    time.sleep(wait)
    evaluation_link.click()

    # click on proceed to evaluations
    proceed_link = sess.at_xpath('/html/body/div[3]/table[2]/tbody/tr/td/input[2]')
    time.sleep(wait)
    proceed_link.click()

    return None
