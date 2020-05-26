import requests
import bs4
import time
import csv
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import selenium.webdriver.support.ui as ui
import pandas as pd
import logging

logging.basicConfig(level = logging.DEBUG, format ='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.ERROR)
                    
driver_location = '''[PATH]\chromedriver.exe'''

sched_list = []
rows_count = 0

print('getScheduleData()')

#--- STEP 1: SCRAPE COURSE SCHEDULE DATA ---#
def getScheduleData():
    st1 = 1
    fn1 = 6
    diff = 5
    diff_div_140 = 28

    #program begins and this runs 14 times
    for i in range(1,diff_div_140):
        browser = webdriver.Chrome(driver_location)
        url= 'COURSE SCHEDULE URL'
        browser.get(url)
        time.sleep(5)
        logging.critical('10 second wait complete. Homepage should be loaded.')
        try:
            logging.critical('Loop #%s' % (i))
            #select Fall term
            session_pick = browser.find_element_by_css_selector('body > div.pagebodydiv > form > table > tbody > tr:nth-child(2) > td:nth-child(2) > select > option:nth-child(3)')
            ActionChains(browser).key_down(Keys.CONTROL).click(session_pick).key_up(Keys.CONTROL).perform()
            time.sleep(1)
            
            #deselect the first subject
            class_pick = browser.find_element_by_css_selector('body > div.pagebodydiv > form > table > tbody > tr:nth-child(2) > td:nth-child(4) > select > option:nth-child('+str(1)+')')
            ActionChains(browser).key_down(Keys.CONTROL).click(class_pick).key_up(Keys.CONTROL).perform()
            time.sleep(1)

            #select five subjects
            for subnum in range(st1, fn1):
                if subnum == st1:
                    class_pick = browser.find_element_by_css_selector('body > div.pagebodydiv > form > table > tbody > tr:nth-child(2) > td:nth-child(4) > select > option:nth-child('+str(subnum)+')')
                    ActionChains(browser).key_down(Keys.CONTROL).click(class_pick).key_up(Keys.CONTROL).perform()
                    time.sleep(.1)
                elif subnum == fn1:
                    class_pick = browser.find_element_by_css_selector('body > div.pagebodydiv > form > table > tbody > tr:nth-child(2) > td:nth-child(4) > select > option:nth-child('+str(subnum)+')')
                    ActionChains(browser).key_down(Keys.CONTROL).click(class_pick).key_up(Keys.CONTROL).perform()
                    time.sleep(.1)
                else:
                    class_pick = browser.find_element_by_css_selector('body > div.pagebodydiv > form > table > tbody > tr:nth-child(2) > td:nth-child(4) > select > option:nth-child('+str(subnum)+')')
                    ActionChains(browser).key_down(Keys.SHIFT).click(class_pick).key_up(Keys.SHIFT).perform()
                    time.sleep(.1)
##                logging.critical('selected %s' %(subnum))
            time.sleep(1)

            logging.critical('Last class picked was %s' % (class_pick.text))

            st1 = st1 + diff
            fn1 = fn1 + diff
            logging.critical('start is now %s and finish is %s' %(st1, fn1))    
            #go
            time.sleep(1)
            logging.critical('about to click')
            nowGo = browser.find_element_by_css_selector('body > div.pagebodydiv > form > center > input[type=submit]:nth-child(2)')
            time.sleep(1)
            nowGo.click()
            
            logging.critical('clicked go, 5 second wait')

            #load courses
            time.sleep(5)
            logging.critical('5 second wait complete, begin count')

            #get max rows
            logging.critical('max rows check')
            rows_count = browser.execute_script("return document.getElementsByTagName('tr').length")
            print(rows_count)

            #check subjects
            logging.critical('subject check')
            subject = browser.find_element_by_css_selector('body > div.pagebodydiv > table:nth-child(6) > tbody > tr:nth-child(3) > td:nth-child(2) > font')
            print(str(len(subject.text.split())-1)+' - '+str(subject.text))

            #scrape data
            for i in range(rows_count):

                sched_dict = {}

                try:
                    #get class name
                    class_name = browser.find_element_by_css_selector('body > div.pagebodydiv > table:nth-child(8) > tbody > tr:nth-child('+str(i)+') > td:nth-child(6) > font > small')
                    sched_dict['className'] = class_name.text
                                
                    #get Course Number
                    CRN_number = browser.find_element_by_css_selector('body > div.pagebodydiv > table:nth-child(8) > tbody > tr:nth-child('+str(i)+') > td:nth-child(3) > a > font > u > small')
                    sched_dict['courseNum'] = CRN_number.text

                    #get class capacity
                    class_capacity = browser.find_element_by_css_selector('body > div.pagebodydiv > table:nth-child(8) > tbody > tr:nth-child('+str(i)+') > td:nth-child(16) > font > small')
                    sched_dict['seatCapacity'] = class_capacity.text

                    #get primary prof
                    prof_name = browser.find_element_by_css_selector('body > div.pagebodydiv > table:nth-child(8) > tbody > tr:nth-child('+ str(i)+') > td:nth-child(14) > font > small')
                    sched_dict['primaryProf'] = prof_name.text

                    #append to master list (sched_list)
                    sched_list.append(sched_dict)

                #show % complete
                    if i == round(rows_count/4):
                        print('25%')
                    elif i == 1:
                        print('0%')
                    elif i == round(rows_count/2):
                        print('50%')
                    elif i == round(rows_count*.75):
                        print('75%') 
                    else:
                        continue

                except:
                    if i == round(rows_count/4):
                        print('25%')
                    elif i == 1:
                        print('0%')
                    elif i == round(rows_count/2):
                        print('50%')
                    elif i == round(rows_count*.75):
                        print('75%')    
                    else:
                        continue

            logging.critical('loop complete')
            browser.quit()
        except:
            logging.critical('loop didn\'t work')
            browser.quit()
            continue

    print('your list is saved as \'sched_list')
    print('to clean your list, use cleanUpScheduleList()')
    return sched_list

#--- STEP 2: CLEAN COURSE SCHEDULE DATA AND OUTPUT TO DATAFRAME---#
dfsched_list = pd.DataFrame()
def cleanUpScheduleList(sched_list = sched_list):
    #Convert to df then convert capacity to numeric
    df = pd.DataFrame(sched_list)
    df["seatCapacity"] = pd.to_numeric(df["seatCapacity"])

    #Group profs and class and count classes
    sum_df = df.groupby(['primaryProf','className']).agg({'seatCapacity': 'sum', 'courseNum': 'count'})

    #Reset index and rename Columns
    sum_df = sum_df.reset_index()
    sum_df.rename(columns={'seatCapacity': 'Total_Seats', 'courseNum': 'Total_Classes'}, inplace=True)

    #Seperate out primaryProf
    sum_df = sum_df.join(sum_df['primaryProf'].str.split(',', expand=True))
    sum_df.rename(columns={0: 'LastName', 1: 'FirstName'}, inplace=True)

    #Eliminate Empty Prof First Name Courses
    sum_df = sum_df[sum_df.FirstName.notnull()]

    #Overwrite outside of function
    global dfsched_list
    dfsched_list = dfsched_list.append(sum_df)
    
    print('dfsched_list has ' + str(len(dfsched_list)) + 'rows.')
    

#--- STEP 3: GET FACULTY DIRECTORY INFORMATION, CLEAN THE DATA, OUTPUT TO DATAFRAME ---#
direct_list = []
dfdirect_list = pd.DataFrame()
def goDirectory():
    browser = webdriver.Chrome(driver_location)
    url='DIRECTORY URL'
    browser.get(url)
    time.sleep(1)

    #Faculty Only
    faculty_dropdown = browser.find_element_by_css_selector('#content > form > table > tbody > tr:nth-child(1) > td > select')
    faculty_dropdown.click()

    faculty_select = browser.find_element_by_css_selector('#content > form > table > tbody > tr:nth-child(1) > td > select > option:nth-child(2)')
    faculty_select.click()
    time.sleep(.1)

    #clickgo
    searchit = browser.find_element_by_css_selector('#content > form > table > tbody > tr:nth-child(8) > td > input[type=submit]:nth-child(2)')
    searchit.click()

    phonelist = []
    for i in range(1,2279):
        direct_dict ={}
        
        #Loading bar
        logging.critical(i)
        
        #get phone number
        try:
            prof_phone_elem = browser.find_element_by_css_selector('#content > div > div:nth-child(3) > table > tbody > tr:nth-child('+str(i)+') > td:nth-child(3) > a')
        except:
            prof_phone_elem = browser.find_element_by_css_selector('#content > div > div:nth-child(3) > table > tbody > tr:nth-child('+str(i)+') > td:nth-child(3)')

        prof_phone = prof_phone_elem.text
        #add area code
        if prof_phone == 'N/A':
            continue
        elif prof_phone[0] == '(':
            continue
        else:
            prof_phone = '(210) '+prof_phone
        
        #continue if it's not a duplicate
        if (prof_phone == 'N/A' or prof_phone not in phonelist):           

            #get phone cont'd
            phonelist.append(prof_phone) #add to stored duplicate list
            direct_dict['profPhone'] = prof_phone #add to direct_list
            
            #get department
            prof_dept = browser.find_element_by_css_selector('#content > div > div:nth-child(3) > table > tbody > tr:nth-child('+str(i)+') > td:nth-child(2)')
            direct_dict['department'] = prof_dept.text

            #get name
            prof_name = browser.find_element_by_css_selector('#content > div > div:nth-child(3) > table > tbody > tr:nth-child('+str(i)+') > td:nth-child(1) > a')
            direct_dict['profFullName'] = prof_name.text
            #split first/last into new columns
            fullName = prof_name.text.split(', ')[::-1]
            firstname = fullName[0]
            firstnameletter = firstname[0]+'.'
            lastname = fullName[1]
            direct_dict['firstName'] = firstname
            direct_dict['firstNameLetter'] = firstnameletter
            direct_dict['lastName'] = lastname
            
            #get title
            prof_title = browser.find_element_by_css_selector('#content > div > div:nth-child(3) > table > tbody > tr:nth-child('+str(i)+') > td:nth-child(1) > span')
            direct_dict['profTitle'] = prof_title.text
            
            #get email
            if (' ' not in firstname and ' ' not in lastname): #no space in first or last name
                prof_email = firstname+'.'+lastname+'EMAIL DOMAIN SUFFIX'
            elif (' ' in firstname and ' ' not in lastname): #only first name space
                prof_email = firstname.split(' ',1)[0]+'.'+lastname+'EMAIL DOMAIN SUFFIX'
            else: #scrape the email from the link
                #get prof's unique url link
                emailURL = prof_name.get_attribute('href')
                # Open a new window
                browser.execute_script("window.open('');")
                # Switch to the new window and open URL B
                browser.switch_to.window(browser.window_handles[1])
                browser.get(emailURL)
                time.sleep(.1)
                # Scrape and store the email
                scraped_email = browser.find_element_by_css_selector('#main > div > div:nth-child(2) > div.col-md-9.directory > div > table > tbody > tr:nth-child(6) > td > a')
                prof_email = scraped_email.text
                # Close the tab with URL B
                browser.close()
                # Switch back to the first tab with URL A
                browser.switch_to.window(browser.window_handles[0])
            
            direct_dict['profEmail'] = prof_email

            #add to main list
            direct_list.append(direct_dict)

        #if it's a duplicate keep looping
        else:
            continue
    
    #Convert to df then save as df
    df = pd.DataFrame(direct_list)
    global dfdirect_list
    dfdirect_list = dfdirect_list.append(df)
    
    print('Scraped '+str(len(dfdirect_list))+'names. Your df is saved as \'dfdirect_list')
    return dfdirect_list[:10], dfdirect_list.keys()

#--- STEP 4: (LEFT) MERGE TWO DATAFRAMES TO GIVE COURSE INFO FOR EACH PROF, OUTPUT CSV ---#
def leftjoin_export (dfdirect_list = dfdirect_list, dfsched_list = dfsched_list, filename = 'List Final.csv'):
    left = dfdirect_list
    right = dfsched_list

    #create column with same name syntax as schedule name
    left['primaryProf'] = left[['lastName', 'firstNameLetter']].apply(lambda x: ', '.join(x[x.notnull()]), axis = 1)

    leftjoin = pd.merge(left,right,on='primaryProf',how='inner')

    clean = leftjoin.reset_index()
    clean = clean.drop(['firstNameLetter', 'LastName', 'FirstName'], axis=1)

    #sort by Total_Seats, then sum the Total_Seats and the Total_Classes and comma out the className. Rename className to className (in descending order)
    clean = clean.sort_values('Total_Seats').reset_index()
    clean = clean.groupby(['profEmail']).agg({'Total_Seats': 'sum', 'Total_Classes': 'sum',
                                                'className': ', '.join,
                                                'profPhone':'first', 'department':'first', 'profFullName':'first', 'firstName':'first',
                                                'lastName':'first', 'profTitle':'first'})

    clean.rename(columns={'className': 'className (in descending order)'}, inplace=True)

    #convert to csv
    clean.to_csv(filename, encoding='utf-8')

    return clean
