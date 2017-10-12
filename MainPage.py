#This program is dedicated to the main_page structure of our bot
#on_chat_message and on_callback query are used for dealing with two different types of messages by the user
#The reply keyboard is always present for easy use and three buttons are present for main functions
#The rest choices are presented by inline keyboard buttons
#After the user enters their course code and index, their personal information will be stored as local csv file for future reference
#Our bot can tell them the information for the next lesson (lesson name, time, location and directions)
#Our bot can generate users timetable as .jpg format to be dowenloaded and refered to depending on users' preferences
#Our bot also provides feedback platforms for our self-improvements
#We utilise many external websites including NTU MAP, NTU COURSE SEARCHER for users' better experiences
#We take into consideration as many as irrugularities as we can think of to avoid program failure
###################################################################################################################################### 

import sys
import time
import threading
import random
import telepot
import datetime
import NTULessonScheduleExtractor
from NTULessonScheduleExtractor import Courses
from pprint import pprint
import numpy as np
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
from Global_variables import *
from LessonScheduler import Users
from Lab_full import Find_labname

def on_chat_message(msg):    #Deals with text type message sent by the user
    content_type, chat_type, chat_id = telepot.glance(msg)   # Get chat_id, content_type, chat_type from the user's input
    print('Chat:', content_type, chat_type, chat_id)     # To check chat_id, content_type, chat_type from the user's in terminal
    
    del course_registered_saved[:]
    course_code_registered_saved = Users(chat_id).getCourseCodeRegistered()
    for i in range(0, len(course_code_registered_saved)):
            course_registered_saved.append(course_code_registered_saved[i])
            course_registered_saved.append(int((Users(chat_id).getCourseIndexRegistered())[i]))
    #Update global variables (course_code_registered_saved) and (course_registered_saved) by exacting data from our local file and create a new list for later use
    #First one contains only course codes of the user. Second one contains both course code and course code index in the format of a list with [str,int,str.int....]

    print (course_registered_saved)
    global current_state
    print (current_state)
    #for program testing and updating

    if current_state == 1:        
    #To indicate the user now is at the main_page layer
        if content_type != 'text':
            bot.sendMessage(chat_id, "Wow is it a foreign language? I don't understand! Can say again?")
            return
        # Verify the content_type, the message sent by the user must be of content type 'text'. If other characters are entered, reminders are sent. 

        if msg['text'] == 'Next Lesson':
        	#Enter the main function of "Next Lesson"
            #print (Users(chat_id).gotLessonLater())
            if Users(chat_id).gotLessonLater():
                Location = str(Users(chat_id).getNextLessonLoc())
                #Check if the user has lessons later
                #Update the location of the next lesson into local variable
            
                if 'LAB' in str(Users(chat_id).getNextLessonType()):    #Check if next lesson is a lab
                    if len(Find_labname(Location)) == 1:
                        Full_Location_Name = (Find_labname(Location))[0]
                        link = 'http://maps.ntu.edu.sg/m?q='+ Full_Location_Name + '&font=m&sch_btn=Search'
                        markup = InlineKeyboardMarkup(inline_keyboard=[
                            [dict(text='Direction', url = link)],
                        ])
                        bot.sendMessage(chat_id, Users(chat_id).message(),reply_markup = markup)
                    #if only one full lab name is found for the abbreviation entered, create a URL button
                    #search the direction of the lab on the website by self-filling the labname for the user

                    elif len(Find_labname(Location)) == 0:
                        link = 'http://maps.ntu.edu.sg/m?q='+ Location + '&font=m&sch_btn=Search'
                        markup = InlineKeyboardMarkup(inline_keyboard=[
                            [dict(text='Direction', url = link)],
                        ])
                        bot.sendMessage(chat_id, Users(chat_id).message(),reply_markup = markup)
                    #If no full lab name is found, give the user the chance to see the results on the webpage themselves
                    #Reminds the user of the possible wrong abbreviation he enters

                    else:
                        bot.sendMessage(chat_id, Users(chat_id).message())
                        global labname_list
                        labname_list = list(Find_labname(Location))
                        print (labname_list)
                        markup = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text= labname, callback_data= labname) for labname in labname_list[0:2]],
                            [InlineKeyboardButton(text= labname, callback_data= labname) for labname in labname_list[2:4]],
                            [InlineKeyboardButton(text= labname, callback_data= labname) for labname in labname_list[4:6]],
                            [InlineKeyboardButton(text= labname, callback_data= labname) for labname in labname_list[6:8]],
                            [InlineKeyboardButton(text= labname, callback_data= labname) for labname in labname_list[8:10]],
                            [InlineKeyboardButton(text= labname, callback_data= labname) for labname in labname_list[10:12]],
                            [InlineKeyboardButton(text= labname, callback_data= labname) for labname in labname_list[12:14]],
                            ])
                        bot.sendMessage(chat_id, 'Please select the lab you want to go',reply_markup = markup)
                    #If multiple full labnames are searched, incooperate inline keyboard buttons to display all the possible locations
                    #Gives the user the choice to choose which lab he wants to go
                    #Use query function later for the specif lab chosen

                else:
                    link = 'http://maps.ntu.edu.sg/m?q='+ Location + '&font=m&sch_btn=Search'
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Direction', url=link)],
                    ])
                    bot.sendMessage(chat_id, Users(chat_id).message(),reply_markup = markup)
                #if next lesson is not a lab, there is a high change it can be searched on the NTU MAP SITE
                #Directly helps user fill up the location name and search it on the MAP website

            elif Users(chat_id).generateTimetableinJpeg() != True:
                bot.sendMessage(chat_id, text = "Hmmm... We cannot find your information in our database. Seems like you haven't tell us what course you have yet. Please go to Settings to tell us!")
            #Check if the user has information in our data base

            else:
                bot.sendMessage(chat_id, Users(chat_id).message())
            #Tells user he dose not have anymore lesson if the user finishes his lesson today.
            #No direction link is shown

        elif msg['text'] == 'Timetable':    #Enter the second funtion of timetable
            Users(chat_id).storeInfoToCSV(course_registered_saved)
            #Update all the courses the users registered into his specific csv file in our local data base
            print (Users(chat_id).generateTimetableinJpeg())
            if Users(chat_id).generateTimetableinJpeg() == True:
                path = 'Database/user_timetable_info/'
                path = path + str(chat_id) + '/'+ 'Timetable.jpg'
                bot.sendMessage(chat_id, text = 'Generating Timetable! Hang on there, our bot is hard at work! (Tip: If you do not like the design of the timetable, you can keep clicking on the Timetable button until you get your favourite one!)')
                bot.sendDocument(chat_id, open(path,'rb'))
            #Check if the timetable can be generated or not.
            #Bot send message as well as JPG file document if the timetable is available for user to view and download
            else:
            	bot.sendMessage(chat_id, text = "Hmmm... We cannot find your information in our database. Seems like you haven't tell us what course you have yet. Please go to Settings to tell us!")
            #Remind the user of adding in courses if no information is found in his/her csv file

        elif msg['text'] == 'Settings':    #Enter the third function of Settings

            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[0:3]],
                [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[3:6]],
                [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[6:9]],
                [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[9:12]],
                [dict(text='+', callback_data = '+')],
                [dict(text='Delete all', callback_data='Delete all')],
                [dict(text='Feedback', callback_data='Feedback')],
                ])
            bot.sendMessage(chat_id, 'Click on the course code to delete it. \nClick on + to add your course. \nClick on Delete All to delete all course. \nClick on Feedback to tell us your opinions on our bot.',reply_markup = markup)
            # Go to settings page where users can delete unwanted courses, add courses and write feedback to the bot developer

        else:
            markup = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='Next Lesson')],
                [KeyboardButton(text='Timetable'), KeyboardButton(text='Settings')]
            ])
            bot.sendMessage(chat_id, text="??Hey, welcome to 'Can Pon or Not'! I can tell you all information about your next lesson, show you your timetable so that you know when to chill and when to study hard! \n??Click on settings to store your timetable if this is your first time seeing me!", reply_markup=markup)
            #Greet the user again if none of the three main functions are used.

    elif current_state == 5:
    	#This enters the adding course_name layer to avoid confusion and intersection with the main_page layer
        if msg['text'] in course_code_registered_saved:
            bot.sendMessage(chat_id, 'The course has been added to your timetable previously.')
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[0:3]],
                [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[3:6]],
                [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[6:9]],
                [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[9:12]],
                [dict(text='+', callback_data = '+')],
                [dict(text='Delete all', callback_data='Delete all')],
                [dict(text='Feedback', callback_data='Feedback')],
            ])
            bot.sendMessage(chat_id, 'Click on the course code to delete it. \nclick on + to add your course. \nClick on Delete All to delete all course. \nClick on Feedback to tell us your opinions on our bot.',reply_markup = markup)
            # Check if the user's input of course code is already in the list.
            # If True, that means the user keyed in a repeated course and will be asked to perform other action instead.

        elif msg['text'] == 'Settings' or msg['text'] == 'Timetable' or msg['text'] == 'Next Lesson':
            markup = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='Next Lesson')],
                [KeyboardButton(text='Timetable'), KeyboardButton(text='Settings')]
            ])
            bot.sendMessage(chat_id, text='You have exited the add course page. What else can I do for you?', reply_markup=markup)
            current_state = 1
            #To exit the add_course page if the user presses any of the three main function reply keyboard buttons
            #Return to main_page layer

        elif isinstance(Courses(msg['text']).getCourseIndexList(),list) == True and len(msg['text']) == 6:
            if Courses(msg['text']).dataframeNumberChecker() != True:
                global course_index_input
                del course_index_input[:]
                global course_code_input
                del course_code_input[:]
                course_code_input.append(msg['text'])
                course_index_input.extend(Courses(msg['text']).getCourseIndexList())
                #if the course code entered is valid, make use of two temporary variables for recording course code and course index input
                #update the key in contents of the user to these two variables for later display purporses

                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[0:3]],
                    [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[3:6]],
                    [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[6:9]],
                    [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[9:11]],
                    [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[11:14]],
                    [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[14:17]],
                    [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[17:20]],
                    [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[20:23]],
                    [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[23:26]],
                    [InlineKeyboardButton(text= "I don't know", callback_data= "I don't know")],
                    ])

                bot.sendMessage(chat_id, 'Choose the class index of your lesson',reply_markup = markup)
                #Display to the user all the course indexes available on the inlinekeyboardbuttons
                #Use query function later for the index_number the user has chose

        else:
            bot.sendMessage(chat_id, 'You have entered an invalid course code. Please check again and re-enter!')
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[0:3]],
                [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[3:6]],
                [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[6:9]],
                [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[9:12]],
                [dict(text='+', callback_data = '+')],
                [dict(text='Delete all', callback_data='Delete all')],
                [dict(text='Feedback', callback_data='Feedback')],
            ])
            bot.sendMessage(chat_id, 'Click on the course code to delete it. \nclick on + to add your course. \nClick on Delete All to delete all course. \nClick on Feedback to tell us your opinions on our bot.',reply_markup = markup)
            #If the user has entered an invalid course code, an reminder will be sent to him to check his course code

    elif current_state == 7:
    	#The main layer of feedback function
        Users(chat_id).storeFeedbackToCSV(msg['text'])
        current_state = 1
        bot.sendMessage(chat_id,"Thank you for your feedback!!! ")
        #Let users write feedback to us to store in the local csv file
        #Return to the main_page layer after finishing

    else:
        markup = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='Next Lesson')],
            [KeyboardButton(text='Timetable'), KeyboardButton(text='Settings')]
        ])
        bot.sendMessage(chat_id, text="??Hey, welcome to 'Can Pon or Not'! I can tell you all information about your next lesson, show you your timetable so that you know when to chill and when to study hard! \n??Click on settings to store your timetable if this is your first time seeing me!", reply_markup=markup)
    #Display the custome keyboard when the user keys in anything random

def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback query:', query_id, from_id, query_data)
    del course_registered_saved[:]
    course_code_registered_saved = Users(from_id).getCourseCodeRegistered()
    for i in range(0, len(course_code_registered_saved)):
            course_registered_saved.append(course_code_registered_saved[i])
            course_registered_saved.append(int((Users(from_id).getCourseIndexRegistered())[i]))
    print (course_registered_saved)
    #Get query_id, from_id, query_data from inline keyboard
    #Update the course_registered and course_code_registered

    if str(query_data) in labname_list:
        link = 'http://maps.ntu.edu.sg/m?q=' + query_data + '&font=m&sch_btn=Search'
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text='Direction', url=link)],
        ])

        bot.sendMessage(from_id, 'Here is the direction to '+ query_data ,reply_markup = markup)
    #With reference to the direction function
    #if query data is a full labname after the user has chosen where he wants to go
    #Direction link will be set

    elif query_data in course_code_registered_saved:
        location_number = int(course_registered_saved.index(query_data))
        respected_index = course_registered_saved[location_number + 1]
        course_registered_saved.remove(respected_index)
        course_registered_saved.remove(query_data)
        course_code_registered_saved.remove(query_data)
        print (course_registered_saved)
        Users(from_id).storeInfoToCSV(course_registered_saved)
        #if the user clicks on the course code in the setting menue, which means he wants to delete this certain course
        #Make changes to the global variable and update it the the user's respective csv file

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[0:3]],
            [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[3:6]],
            [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[6:9]],
            [InlineKeyboardButton(text= coursename, callback_data= coursename) for coursename in course_code_registered_saved[9:12]],
            [dict(text='+', callback_data = '+')],
            [dict(text='Delete all', callback_data='Delete all')],
            [dict(text='Feedback', callback_data='Feedback')],
            ])
        del course_registered_saved[:]
        bot.sendMessage(from_id, 'Your selected course has been deleted!',reply_markup = markup)
        #Display the new course code registered after deleting

    elif query_data == 'Delete all':
        del course_code_registered_saved[:]
        del course_registered_saved[:]
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text='+', callback_data = '+')],
            [dict(text='Delete all', callback_data = 'Delete all')],
            [dict(text='Feedback', callback_data='Feedback')],
            ])
        bot.sendMessage(from_id, 'All courses are deleted!',reply_markup = markup)
        Users(from_id).storeInfoToCSV(course_registered_saved)
    #In the Setting menu, when the user clicks on 'Delete all', all courses will be deleted
    #A setting menu without any course will be displayed to the user
    #Updates will be made the the user's csv file

    elif query_data == '+':
        bot.sendMessage(from_id, 'Please key in the course code (e.g. CZ1003) you want to add.')
        global current_state
        current_state = 5
    #In the Setting menu, when the user clicks on '+', he/she will be prompted to the add course layer by updating current_state value

    elif query_data == 'Feedback':
        bot.sendMessage(from_id, 'Please give us your feedback!')
        current_state = 7
    # In the Setting menu, when the user clicks on 'Feedback', he/she will enter the feedback layer

    elif query_data == "I don't know":
        Courses(course_code_input[0]).getwebpagePNG()
        path = 'Database/webpage_screenshot/'
        path = path + str(course_code_input[0]) + '.png'
        bot.sendMessage(from_id, "It's okay! We got you there! Just hang on before we show you the information of all course indexes!")
        bot.sendPhoto(from_id, open(path,'rb'))
        #Store the course_index summary page into the local data
        #Display the summary page to the user for them to better recall their course index, which saves them trouble

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[0:3]],
            [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[3:6]],
            [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[6:9]],
            [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[9:11]],
            [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[11:14]],
            [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[14:17]],
            [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[17:20]],
            [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[20:23]],
            [InlineKeyboardButton(text= index_number, callback_data= index_number) for index_number in course_index_input[23:26]],
            ])

        bot.sendMessage(from_id, 'Choose the class index of your lesson',reply_markup = markup)
        #Display to the user all the course indexes available on the inlinekeyboardbuttons
        #Use query function later for the index_number the user has chose


    elif query_data in course_index_input:
        #course_code_registered.append(course_code_input[-1])
        #print (course_code_registered)
        #course_index_registered.append(query_data)
        course_registered_saved.append(course_code_input[-1])
        index_integer = int(query_data)
        course_registered_saved.append(index_integer)
        print(course_registered_saved)
        print(Users(from_id).storeInfoToCSV(course_registered_saved))
        #if an index is chosen by the user, variables will be updated
        #The final version will be updated to the local csv file

        if Users(from_id).storeInfoToCSV(course_registered_saved) == True:
            course_code_registered_saved.append(course_code_input[-1])
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=coursename, callback_data=coursename) for coursename in course_code_registered_saved[0:3]],
                [InlineKeyboardButton(text=coursename, callback_data=coursename) for coursename in course_code_registered_saved[3:6]],
                [InlineKeyboardButton(text=coursename, callback_data=coursename) for coursename in course_code_registered_saved[6:9]],
                [InlineKeyboardButton(text=coursename, callback_data=coursename) for coursename in course_code_registered_saved[9:12]],
                [dict(text='+', callback_data='+')],
                [dict(text='Delete all', callback_data='Delete all')],
                [dict(text='Feedback', callback_data='Feedback')],
            ])

            bot.sendMessage(from_id, 'Your course has been added!', reply_markup=markup)
            del course_index_input[:]
            del course_registered_saved[:]
            current_state = 1
        #If it has been proven that the course code has been updated successfully (No repetitive course code in the user's csv file)
        #An updated setting menu will be displayed
        
        else:
            course_registered_saved.pop(-1)
            course_registered_saved.pop(-1)
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=coursename, callback_data=coursename) for coursename in course_code_registered_saved[0:3]],
                [InlineKeyboardButton(text=coursename, callback_data=coursename) for coursename in course_code_registered_saved[3:6]],
                [InlineKeyboardButton(text=coursename, callback_data=coursename) for coursename in course_code_registered_saved[6:9]],
                [InlineKeyboardButton(text=coursename, callback_data=coursename) for coursename in course_code_registered_saved[9:12]],
                [dict(text='+', callback_data='+')],
                [dict(text='Delete all', callback_data='Delete all')],
                [dict(text='Feedback', callback_data='Feedback')],
            ])

            bot.sendMessage(from_id, 'There seems to be a clash in your timetable. Please check again!', reply_markup=markup)
            print (course_registered_saved)
            del course_index_input[:]
            del course_registered_saved[:]
            current_state = 1
        #If the update to local csv file is unsuccessful (due to clashes in timetable timing)
        #The course_registered_saved variable will delete the newly added course code and course index
        #User's csv file will be updated again

        
TOKEN = ''

bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()


print('Listening ...')

while 1:
    time.sleep(10)

#Running the bot