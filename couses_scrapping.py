# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 16:08:24 2020

@author: TARIQ
"""
import time
import re
import os
from selenium import webdriver

USERNAME = "uername@email.com"
password = "password"
COURSENAME= "SQL + Tableau + Python"
COURSE_FOLDER = "c:/courseFolder"
SITE_URL='https://www.coursesSite.com'
#SITE_URL_COURSE="https://365datascience.teachable.com"
START_SECTION_NUM=-1##### to get all videos
START_LECTURE_NUM=-1
END_SECTION_NUM=-1
END_LECTURE_NUM=-1

INDEX_START=0   ## Calculated based on te n SECTION_NUM AND LECTURE_NUM
INDEX_END=0

##initDriver to intiate the engine and direct the browser to the course page
def initDriver():
    driver = webdriver.Chrome()
    #365datascience.com
    driver.get(SITE_URL)
    loginCourse=driver.find_element_by_xpath("//*[@id='menu-main-nav-1']/li[6]/ul/li[2]/a")
    driver.get(loginCourse.get_attribute("href"))
    time.sleep(10)
    driver.find_element_by_xpath('//*[@id="user_email"]').send_keys(USERNAME)
    driver.find_element_by_xpath('//*[@id="user_password"]').send_keys(password)
    driver.find_element_by_xpath('//*[@id="new_user"]/div[3]/input').click()
    driver.find_element_by_xpath('//*[@id="search-courses"]').send_keys(COURSENAME)
    driver.find_element_by_xpath('//*[@id="search-course-button"]').click()
    time.sleep(5)
    course = driver.find_element_by_xpath("//div[@class='row']/a")
    course_link=course.get_attribute("href")
    driver.get(course_link)
    
    return driver

############getMetadata to get list of sections and lectures for the course.
def getMetadata(driver):
    INDEX_START=0   ## Calculated based on te n SECTION_NUM AND LECTURE_NUM
    INDEX_END=0
    CURRENT_INDEX = 0
    sections = driver.find_elements_by_xpath('/html/body/div[2]/div[@class="row"]')
    metadata=[]
    section_index = 0
    for sec in sections:
        lectures_index = 0
        sec.find_element_by_xpath('//div/div[@class="section-title"]')
        title=sec.text
        title=title.split('\n')
        refined_title=[c for c in title[0] if c!='"']
        title_new="".join(refined_title)
        section_Folder = title_new
        videos_secs=sec.find_elements_by_tag_name("li")
                
        for vid in videos_secs:
            lecture = vid.find_element_by_tag_name("a")
            part_url=lecture.get_attribute("href")
            lecture_title = lecture.find_element_by_class_name("lecture-name").text
            metadata.append([str(section_index)+"_"+section_Folder,str(lectures_index)+"_"+lecture_title,part_url])
            #print(metadata)
            if(section_index == (START_SECTION_NUM-1) and lectures_index == (START_LECTURE_NUM-1)):
                INDEX_START = CURRENT_INDEX
                print("INDEXSTART: "+str(INDEX_START))
            
            if(section_index == (END_SECTION_NUM-1) and lectures_index == (END_LECTURE_NUM-1)):
                INDEX_END = CURRENT_INDEX
                print("INDEXEND: "+str(INDEX_END))
                
            lectures_index+=1
            CURRENT_INDEX+=1
            
            
            
            
        section_index+=1

        #print(metadata)
        
     
    return (metadata,INDEX_START,INDEX_END)


##########3 saveVideos for saving the videos using the metadata form the previous function.
def saveVideos(driver,metadata,INDEX_START,INDEX_END):
    print("Start_Index: "+str(INDEX_START)+",End_Index: "+str(INDEX_END))
    if(START_SECTION_NUM==-1 or START_LECTURE_NUM == -1 or END_SECTION_NUM == -1 or END_LECTURE_NUM == -1):
        metadata_subset=metadata
    else:
        metadata_subset=metadata[INDEX_START:(INDEX_END+1)]
        
    for meta in metadata_subset:
        #print(meta[0]+","+meta[1])
        driver.get(meta[2])
        try:
            #section_name=meta[0].replace(" ","_").replace(":","_").replace("?","_")
            #file_name=meta[1].replace(" ","_").replace(":","_")+".mp4"
            pattern=re.compile("[^\\w]")
            section_name = pattern.sub("_",meta[0])
            file_name=(pattern.sub("_",meta[1]))+".mp4"
            if(os.path.isdir(COURSE_FOLDER+"/"+section_name)==False):
                os.mkdir(COURSE_FOLDER+"/"+section_name)
            
            print(COURSE_FOLDER+"/"+section_name+"/"+file_name)
            
            attachs = driver.find_elements_by_xpath('//a[@class="download"]')
            print(attachs)
            for att in attachs:
                link = att.get_attribute("href")
                attachfilename = att.get_attribute("data-x-origin-download-name")
                print(attachfilename+" "+link)
                os.system('curl '+link+' --output '+COURSE_FOLDER+'/"'+section_name+'/'+attachfilename+'"')
            
            elem=driver.find_element_by_class_name("attachment-wistia-player")
            videoId=elem.get_attribute("data-wistia-id")
            videoURL="https://fast.wistia.net/embed/iframe/"+videoId
            driver.get(videoURL)
        
            scripts=driver.find_elements_by_tag_name("script")
            code = scripts[4].get_attribute("innerHTML")
            pp=re.compile("(https://embed-ssl.wistia.com/deliveries/\\w+\.bin)")
            res = pp.search(code)
            url=res.group(0)

            os.system('curl '+url+' --output '+COURSE_FOLDER+'/"'+section_name+'/'+file_name+'"')
        except Exception as e:
            print("Exception in Section: ("+meta[0]+") and Lecture: ("+meta[1]+")"+" URL: "+meta[2]+" ,"+str(e))
            with open(COURSE_FOLDER+"/Error.log", "a") as myfile:
                myfile.write("Section: ("+meta[0]+") and Lecture: ("+meta[1]+")"+" URL: "+meta[2]+"\r\n")


        
    
    
   
#driver = initDriver()
#metadata,index_start,index_end = getMetadata(driver)    
    
def main():
    driver = initDriver()
    metadata,index_start,index_end = getMetadata(driver)
    saveVideos(driver, metadata,index_start,index_end)
    driver.close()


if __name__ == '__main__':
    main()


