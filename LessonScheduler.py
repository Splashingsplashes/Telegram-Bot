from NTULessonScheduleExtractor import Courses
import csv
import pandas as pd
import datetime
import os
import shutil
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import re

day_dict = {'MON':1, 'TUE':2, 'WED':3, 'THU':4, 'FRI':5, 'SAT':6, 'SUN':7, 'nan':8}
day_dict_1 = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
start_day = datetime.date(2017 , 8 , 13)
recess_week = datetime.date(2017 , 10 , 1)
number_of_weeks = 13
nan = 'nan'
coursetype_dict = {
            'LEC/STUDIO' : 'lecture/studio',
            'TUT' : 'tutorial',
            'SEM' : 'seminar',
            'LAB' : 'lab',
            'PRJ' : 'project',
            'DES' : 'design'
}

def semweeks():
	'''Return a list of datetime objects each representing the start of all the weeks in a semester with recess week excluded.'''
	tdelta = datetime.timedelta(days=7)
	sem_weeks = []

	for a in range(number_of_weeks + 1):
		sem_weeks.append(start_day + a * tdelta)

	sem_weeks.remove(recess_week)
	return sem_weeks

def courseweeks(remark):
	'''Return a list of weeks that a module have in a semester.
	
	The remark argument is in the form of 'Wk2-13' or something like 'Wk2,4,5,8-11'
	This function is able to parse it into a list.

	'''
	if 'nan' in remark:
		return list(range(1 , number_of_weeks + 1))
	else:
		course_weeks = []
		course_weeks_raw = remark[2:].split(',')	# Split in to a list
		for a in course_weeks_raw:
			if '-' in a:
				week_range = a.split('-')		# If '-' is found, then convert it into a list of integers
				for b in range(int(week_range[0]) , int(week_range[1]) + 1):
					course_weeks.append(b)
			else:
				course_weeks.append(int(a))
	return course_weeks

def getCurrentWeek():
	'''Return an integer representing current school week.'''
	for w in range(number_of_weeks):
		if (datetime.date.today() - semweeks()[w]).days < 7 and (datetime.date.today() - semweeks()[w]).days >= 0:
			return w + 1

def gotLessonThisWeek(remark):
	'''Return true if a particular module has lesson this week.

	Can be used when a lab only takes place on alternate weeks or modules only take place on specific weeks.

	'''
	return getCurrentWeek() in courseweeks(remark)

def coursetypeinfull(course_type):
	'''Return a string of the full name of course type (e.g. 'TUT' returns 'Tutorial').'''
	if course_type in coursetype_dict:
		return coursetype_dict[course_type]
	else:
		return course_type

def romannumeralConverter(coursename):
	'''Convert roman numeral in the name of a coure to arabic numeral.'''
	roman_dict = {' I': ' 1', ' II': ' 2', ' III': ' 3', ' IV': ' 4'}
	for roman_numeral in list(roman_dict):
		if roman_numeral in coursename:
			converted_coursename = coursename.replace(roman_numeral, roman_dict[roman_numeral])
			return converted_coursename
	else:
		return coursename

def coursenameConverter(coursename):
	'''Convert all-capitalized course name to course name with only the first letter of each word capitalized.'''
	 converted_coursename = re.sub("[^A-Za-z :,&?()'0-9]", "", romannumeralConverter(coursename))
	 return converted_coursename.title()

def summaryFormatter(summarylist):
	'''Convert list of detailed info a course into a string that can be sent and read by user.'''
	summaryformatted =  coursetypeinfull(summarylist[2][:-1]) + ' of ' + summarylist[0] + ' ' + coursenameConverter(summarylist[1]) + ' at {0[3]} from '.format(summarylist) + summarylist[4][0:4] + ' to ' + summarylist[4][5:] + '\n\n'
	return summaryformatted

def lessonFinishChecker(rawtimedata):
	'''Return True if there is no lesson at the current moment.'''
	lesson_starttime = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, int(rawtimedata[0:2]), int(rawtimedata[2:4]))
	lesson_endtime = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, int(rawtimedata[5:7]), int(rawtimedata[7:9]))
	if datetime.datetime.now() > lesson_starttime and datetime.datetime.now() < lesson_endtime:
		return True

def userinfoChecker(chat_id):
	'''Return True if user's info is stored in Database/usermoduleinfo.csv'''
	user_info_dataframe = pd.read_csv('Database/usermoduleinfo.csv')#, error_bad_lines=False)
	user_chatid_list = user_info_dataframe['chat_id'].tolist()
	return int(chat_id) in user_chatid_list

class Users:

	'''The 'Users' class can be used to extract various information of a particular user.

	The class defines 11 methods, allowing user to retrieve, generate and store various information of a particular user to and from local database.

	Attributes:
		self.chat_id			User's chat id.
		self.next_lesson_loc	Location of next lesson (if there is)
		self.next_lesson_type	Type of next lesson (e.g. tutorial, lecture, lab, etc,)
		self.user_info			List of course codes and course indices, empty if user's info is not in database

	'''

	def __init__(self, chat_id):
		self.chat_id = chat_id
		self.next_lesson_loc = 0
		self.next_lesson_type = 0
		self.user_info = []
		if userinfoChecker(self.chat_id):
			user_info_dataframe = pd.read_csv('Database/usermoduleinfo.csv')
			user_chatid_list = user_info_dataframe['chat_id'].tolist()
			j = -1
			for i in user_chatid_list:
				j += 1
				if int(self.chat_id) == i:
					break
			self.user_info = user_info_dataframe[j : j + 1].values.tolist()[0]  # A list of course codes and course indices registered by the user in the format [chat_id, course_code1, course_index1, course_code2, course_index2,...]

	def getCourseCodeRegistered(self):
		'''Return a list of course codes registered by a user. (e.g. [CZ1003, CZ1004, CZ1005, ...]).'''
		course_code_registered = []
		for a in range(len(self.user_info)):
			if a % 2 == 1 and str(self.user_info[a]) != 'nan':	# Course codes are in the odd number position in self.user_info
				course_code_registered.append(str(self.user_info[a]))
		return course_code_registered

	def getCourseIndexRegistered(self):
		'''Return a list of course indices registered by a user. (e.g. [10101, 10506, 189, ...]).

		The sequence of the course indcies corresponds to that returned by method getCourseCodeRegistered()

		'''
		course_index_registered = []
		for b in range(len(self.user_info)):
			if b % 2 == 0 and str(self.user_info[b]) != 'nan' and b != 0:	# Course indices are in the even number position in self.user_info, and excluding the first item in the list since the first item is the chat id of the user.
				course_index_registered.append(str(int(self.user_info[b])))
		return course_index_registered


	def getUserTimetableDictList(self):
		'''Return a list of dictionary each containing various info of a module(e.g. Module name, module AU, start and end time of each lab/tutorial/lecture, venue, remark etc.).

		If one of the course codes registered by user is invalid (i.e. there is so such module), the method returns None.

		'''
		course_code_of_user = self.getCourseCodeRegistered()
		course_index_of_user = self.getCourseIndexRegistered()

		timetable_dictlist = []
		for k in range(len(course_code_of_user)):
			if type(Courses(course_code_of_user[k]).getCourseIndexInfo(course_index_of_user[k])) is str:
				return
			else:
				timetable_dictlist.append(Courses(course_code_of_user[k]).getModuleInfo(course_index_of_user[k]))
		return timetable_dictlist

	def storeInfoToCSV(self, user_course_info_list):
		'''Return True upon successfully storing user's timetable info (i.e. a list of dictionary each vaiours info a module). Return 'invalid' if there is clash in timetable.

		The method takes in a list of course code and indice in the form of [course_code1, course_index1, course_code2, course_index2,...] as the argument.
		
		The storing of user timetable info is split into 3 cases:
			1. If the user is storing the same list of course codes and course indices (where order doesn't matter), the method returns True and no changes are done to the current current user database (i.e. Database/user_timetable_info)
			2. If the user is storing a list of course codes and course indices which is different from the current info in the database, the row in Database/usermoduleinfo.csv is replaced with the updated list of course codes and indices. And the correponding in Database/user_timetable_info will be overwritten.
			3. If user's info is not found in the database, his/her info will be stored in Database/usermoduleinfo.csv and detailed info regarding each module will be stored under Database/user_timetable_info.

		'''
		self.user_course_info_list = user_course_info_list
		if not self.user_info:
			self.user_info = [str(self.chat_id)] + user_course_info_list

		def timetableValiditycheck(user_course_info_list):
			'''Return True if there is no clash in the timetable, and return False otherwise.'''
			course_code_of_user = []
			for a in range(len(user_course_info_list)):
				if a % 2 == 0:
					course_code_of_user.append(str(user_course_info_list[a]))			

			course_index_of_user = []
			for b in range(len(user_course_info_list)):
				if b % 2 == 1:
					course_index_of_user.append(str(int(user_course_info_list[b])))			

			timetable_dictlist = []
			for k in range(len(course_code_of_user)):
				timetable_dictlist.append(Courses(course_code_of_user[k]).getModuleInfo(course_index_of_user[k]))

			for x in day_dict:
				end_start_list = []
				for y in timetable_dictlist:
					for z in y['Lesson Info']:
						if x == str(y['Lesson Info'][str(z)]['DAY']) and x != 'nan':
							time_raw = y['Lesson Info'][z]['TIME']
							lesson_starttime = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, int(time_raw[0:2]), int(time_raw[2:4]))
							lesson_endtime = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, int(time_raw[5:7]), int(time_raw[7:9]))
							end_start_list.append([next(iter(y)), lesson_starttime, lesson_endtime])	
				for m in end_start_list:
					for n in end_start_list:
						if m[2] < n[2] and m[2] > n[1]:	# Starting time of a lesson is between the starting and ending time of another lesson.
							return False
						elif m[0] != n[0]:
							if m[1] == n[1] or m[2] == n[2]:	# Two lessons start or end at the same time
								return False
			return True

		def userinfoDuplicationCheck(chat_id):
			'''Return integer 1, 2, 3 each corresponding to the case where existing user course code and index info is the same as in the database, different in the database and not in the database respectively.'''
			if userinfoChecker(chat_id):
				user_info = [i for i in self.user_info[1:] if str(i) != nan]
				if set(user_info) == set(self.user_course_info_list):
					return 1
				else:
					return 2
			else:
				return 3

		def writeDictList(chat_id, dict_list):
			'''Store the detailed module info, including time, day, venue, group, etc., to the directory Database/user_timetable_info/user_chat_id in .csv format'''
			timetable_dir = 'Database/user_timetable_info/' + str(chat_id)
			if not os.path.exists(timetable_dir):	# Check if directory already exists, create one if not
				os.makedirs(timetable_dir)
			timetable_path = timetable_dir + '/' + str(chat_id) + '.csv'
			with open(timetable_path, 'w') as csvfile:
				user_timetable_info = csv.writer(csvfile)
				user_timetable_info.writerow([chat_id, dict_list])

		def changeRow(user_info_list):
			'''Replace a row in Database/usermoduleinfo.csv'''
			with open('Database/usermoduleinfo_tmp.csv', 'w', newline='') as t:	# Create a temporary usermoduleinfo_tmp.csv
				writer = csv.writer(t)
				with open('Database/usermoduleinfo.csv', newline='') as f:
					reader = csv.reader(f)
					for row in reader:
						if row[0] == str(self.chat_id):
							writer.writerow([str(self.chat_id)] + user_info_list)	# Write the replaced row if the first item in the row is the chat id who wants to update their info
							continue
						writer.writerow(row)	# Write the rest lines in usermoduleinfo.csv to temporary usermoduleinfo_tmp.csv

			os.remove('Database/usermoduleinfo.csv')
			os.rename('Database/usermoduleinfo_tmp.csv', 'Database/usermoduleinfo.csv') # Remove old file and rename temporary file.

		if userinfoDuplicationCheck(self.chat_id) == 1:
			return True		# No change is done if it's case 1.
		elif userinfoDuplicationCheck(self.chat_id) == 2:
			if timetableValiditycheck(self.user_course_info_list):	# Check for clash in timetable
				changeRow(self.user_course_info_list)
				self.user_info = [str(self.chat_id)] + user_course_info_list
				writeDictList(self.chat_id, self.getUserTimetableDictList())
			else:
				return 'invalid'
			if not self.user_course_info_list:
				with open('Database/usermoduleinfo_tmp.csv', 'w', newline='') as t:
					writer = csv.writer(t)
					with open('Database/usermoduleinfo.csv', newline='') as f:
						reader = csv.reader(f)
						for row in reader:
							if row[0] == str(self.chat_id):
								continue	# If the argument of the method is an empty list, the correponding row of that user is removed from Database/usermoduleinfo.csv
							writer.writerow(row)
				os.remove('Database/usermoduleinfo.csv')
				os.rename('Database/usermoduleinfo_tmp.csv', 'Database/usermoduleinfo.csv')
			return True
		else:
			if not self.user_course_info_list:
				return False
			if timetableValiditycheck(self.user_course_info_list):	# Check for clash everytime before storing data to database
				user_info_list = [str(self.chat_id)] + self.user_course_info_list
				with open('Database/usermoduleinfo.csv' , 'a' , newline='') as usermoduleinfo_csv:
					usermoduleinfo = csv.writer(usermoduleinfo_csv)
					usermoduleinfo.writerows([user_info_list])
				writeDictList(self.chat_id, self.getUserTimetableDictList())
				return True
			else:
				return False

	def getNextLesson(self):
		'''Return 0 if there is a next lesson. Return string if other cases happen (e.g. recess week, lesson finished on that day, no lesson on that day, etc.)'''
		time_diff = {}
		tday = datetime.date.today().isoweekday()

		def gotLessonToday(daynumber):
			'''Return False if there is no lesson on a particular, and false if there is.

			Take in daynumber (i.e. 1, 2, 3, etc,.) as the argument and the daynumber is the day to be checked for it there is any lesson.

			'''
			time_diff_list = []
			lesson_counter = 0
			for d in user_timetable_dict_list:
				for m in d['Lesson Info']:
					if daynumber == day_dict[str(d['Lesson Info'][str(m)]['DAY'])]:
						if gotLessonThisWeek(str(d['Lesson Info'][m]['REMARK'])):
							lesson_counter += 1
			if lesson_counter == 0:
				return False
			else:
				return True

		if (datetime.date.today() - recess_week) <= datetime.timedelta(days=7) and (datetime.date.today() - recess_week) >= datetime.timedelta(days=0):	# During recess week
			return 'Please lah! Now is recess week, relax a little can? If you really want to know your timetable when the semester resumes, you can click on the Timetable button'

		if not userinfoChecker(self.chat_id):	# User info not in database
			return "Hmmm... We cannot find your information in our database. Seems like you haven't tell us what course you have yet. Please go to Settings to tell us!"
		else:
			user_file = 'Database/' + 'user_timetable_info/'+ str(self.chat_id) + '/' + str(self.chat_id) + '.csv'
			with open(user_file, newline='') as f:
				reader = csv.reader(f)
				for row in reader:
					user_timetable_dict_list = eval(row[1])
					break

			while True:
				if not gotLessonToday(tday):
					if tday == 7:
						tday = 0
					tday += 1
				else:
					break
			# If there is lesson today, then tday is the day of today. If there is no lesson today, tday is the day of the next day with lesson.

			if tday != datetime.date.today().isoweekday():	# If there is no lesson today
				for d in user_timetable_dict_list:
					for m in d['Lesson Info']:
						if tday == day_dict[str(d['Lesson Info'][str(m)]['DAY'])]:
							if gotLessonThisWeek(str(d['Lesson Info'][m]['REMARK'])):
								time_raw = d['Lesson Info'][m]['TIME'] # Example of time_raw: 1200-1300
								first_key = next(iter(d))	# Course code (e.g. CZ1003)
								lesson_starttime = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, int(time_raw[0:2]), int(time_raw[2:4])) # Convert lesson start time as a datetime object
								time_diff[lesson_starttime] = [first_key, d[first_key], m, d['Lesson Info'][m]['VENUE'], time_raw] # Write a dictioanry with lesson start time as the key and the following list as the value: [course_code, module_name, lesson_type, venue, time]
				
				next_day_lesson_summary = "Congratulations! You don't have lesson for today!\n"
				if tday < datetime.date.today().isoweekday(): # If the next day with lesson on next week
					next_day_lesson_summary = next_day_lesson_summary + 'However, you have lesson on next ' + day_dict_1[tday] + ' and here is your timetable!\n\n'
				else: # If the next day with lesson on this week
					next_day_lesson_summary = next_day_lesson_summary + 'However, you have lesson on this ' + day_dict_1[tday] + ' and here is your timetable!\n\n'
				
				sorted_time_diff = sorted(time_diff)	

				for i in sorted_time_diff:
					next_day_lesson_summary += summaryFormatter(time_diff[i])
				return next_day_lesson_summary	# String containing the formatted summary of all lesson on the next day with lesson.

			else: # There is lesson today
				for d in user_timetable_dict_list:
					for m in d['Lesson Info']:
						if tday == day_dict[str(d['Lesson Info'][str(m)]['DAY'])]:
							if gotLessonThisWeek(str(d['Lesson Info'][m]['REMARK'])):
								time_raw = d['Lesson Info'][m]['TIME']
								first_key = next(iter(d))
								lesson_starttime = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, int(time_raw[0:2]), int(time_raw[2:4]))
								time_diff[lesson_starttime - datetime.datetime.now()] = [first_key, d[first_key], m, d['Lesson Info'][m]['VENUE'], time_raw]	

				next_lesson = datetime.timedelta(days=-1) # Set the next_lesson as a negative time delta
				next_lesson_new = [t for t in time_diff if t > datetime.timedelta(days=0)] # New list containing lessons with positive timedelta (i.e lesson that haven't been conducted on that day)
				if next_lesson_new:
					next_lesson = min(next_lesson_new)
					global next_lesson_loc
					next_lesson_loc = time_diff[next_lesson][3]
					global next_lesson_type
					next_lesson_type = time_diff[next_lesson][2]
					global next_lesson_summary
					next_lesson_summary = 'Here you go! You have a ' + summaryFormatter(time_diff[next_lesson])
					return 0
				else:	# All lesson today has strated.
					lastlesson = max(list(time_diff.keys()))
					if lessonFinishChecker(time_diff[lastlesson][4]): # Last lesson has started but not finished
						return 'Relax! Couple more minutes before you finish all your lessons today!'
					return 'Congratulations! You have completed all your lessons for today! Good Job!' # All lesson has finished

	def gotLessonLater(self):
		'''Return True if there is lesson to be conducted later'''
		if self.getNextLesson() == 0:
			return True

	def message(self):
		'''Return string of info to be sent to user'''
		if self.gotLessonLater():
			return next_lesson_summary
		else:
			return self.getNextLesson()

	def getNextLessonLoc(self):
		'''Return a string of venue of the next lesson'''
		if self.gotLessonLater():
			return next_lesson_loc

	def getNextLessonType(self):
		'''Return the string of class type of the next lesson'''
		if self.gotLessonLater():
			return next_lesson_type

	def generateTimetableinJpeg(self):
		'''Return False if user's info cannot be found in the database. Return True is the image of the timetable is suffessfully generated.'''
		day_coord = {'MON':(110,272), 'TUE':(272,433), 'WED':(433,595), 'THU':(595,757), 'FRI':(757,919), 'SAT':(919,1080)}
		time_coord = {'0800':(200,272), '0830':(272,343), '0900':(343,415), '0930':(415,487), '1000':(487,559), '1030':(559,630), '1100':(630,702), '1130':(702,774), '1200':(774,846), '1230':(846,917), '1300':(917,989), '1330':(989,1060), '1400':(1060,1132), '1430':(1132,1204), '1500':(1204,1276), '1530':(1276,1347), '1600':(1347,1419), '1630':(1419,1491), '1700':(1491,1563), '1730':(1563,1634), '1800':(1634,1670), '1830':(1670,1706), '1900':(1706,1742), '1930':(1742,1777), '2000':(1777,1813), '2030':(1813,1849), '2100':(1849,1885), '2130':(1885,1920), '2200':(1920,1920)}
		colour_list = [[(213,11,83),(252,145,58),(237,175,184),(115,192,244),(17,140,139),(241,77,73),(251,177,60),(146,175,215),(82,150,165),(255,0,0),(255,192,0),(112,173,71)],[(249,205,173),(84,121,128),(91, 152, 172), (239, 202, 210), (128, 152, 113), (168, 150, 162), (218, 194, 214), (197, 144, 174),(196, 230, 192), (144, 182, 159), (195, 213, 223), (124, 158, 216)]]
		def getModCoord(rawtime, rawday):		
			'''Return a tuple of coordinates of the image to be pasted on the Database/Resouces/original_timetable.bmp'''
			def getyCoord(time):
				'''Return the y coordiate of the image'''
				if time[2:4] == '00' or time[2:4] == '30':
					lesson_start_coord = time_coord[time[0:4]][0]
				elif int(time[2:4]) <= 30: # To take into account of cases when the start minute of a lesson is not 00 or 30
					lesson_start_coord = int((time_coord[time[0:2] + '00'][1] - time_coord[time[0:2] + '00'][0]) * int(time[2:4]) / 30 + time_coord[time[0:2] + '00'][0])
				else:
					lesson_start_coord = int((time_coord[time[0:2] + '30'][1] - time_coord[time[0:2] + '30'][0]) * int(time[2:4]) / 30 + time_coord[time[0:2] + '30'][0])
				return lesson_start_coord		

			xcoord_s = day_coord[rawday][0]
			xcoord_f = day_coord[rawday][1]		

			ycoord_s = getyCoord(rawtime[0:4])
			ycoord_f = getyCoord(rawtime[5:9])		

			return xcoord_s, ycoord_s, xcoord_f, ycoord_f	
			

		def pasteImage(info_list, timetable_img_obj, colour):
			'''Return an Image object, which has the relevant info of a particular module at a particular timeslot printed on it.'''
			box = getModCoord(info_list[6], info_list[7])
			region = timetable_img_obj.crop(box) # Crop a portion of the timetable image object specified in the argument out
			region = Image.new('RGB',(box[2] - box[0], box[3] - box[1]), colour)	# Convert the cropped region to the colour as specified in the argument
			if info_list[4] == 'nan':
				text = str(info_list[0]) + '\n' + str(info_list[1]) + '\n' + str(info_list[5]) + '\n' + str(info_list[2]) + '\n' + str(info_list[3])
			else:
				text = str(info_list[0]) + '\n' + str(info_list[1]) + '\n' + str(info_list[5]) + '\n' + str(info_list[2]) + '\n' + str(info_list[3]) + '\n' + str(info_list[4])
			font = ImageFont.truetype('Lato-Regular.ttf', 17)
			texted = ImageDraw.Draw(region)		

			offset = margin = 7
			for line in textwrap.wrap(text, width = 11, break_long_words=False):	# Write the info of the lesson of particular timeslot on the cropped region
				texted.text((margin, offset), line, fill=(0,0,0), font= font)
				offset += font.getsize(line)[1]		

			texted = ImageDraw.Draw(region)
			timetable_img_obj.paste(region, box)	# Paste the cropped region back to the timetable image object
		
			return timetable_img_obj

		if not userinfoChecker(self.chat_id):
			return False
		else:
			img_path = 'Database/user_timetable_info/' + str(self.chat_id) + '/'
			shutil.copy('Database/timetable_original.bmp', img_path)
			original_timetable = Image.open(img_path + 'timetable_original.bmp')
			colour_counter = 0
			random.shuffle(colour_list)
			colour_list  = colour_list[0]
			random.shuffle(colour_list)

			user_file = 'Database/' + 'user_timetable_info/'+ str(self.chat_id) + '/' + str(self.chat_id) + '.csv'
			with open(user_file, newline='') as f:
				reader = csv.reader(f)
				for row in reader:
					user_timetable_dict_list = eval(row[1])
					break

			for i in user_timetable_dict_list:		
				for j in i['Lesson Info']:
					if i['Lesson Info'][j]['TIME'] != 'nan' and i['Lesson Info'][j]['DAY'] != 'nan':
						info_list = [next(iter(i)), i[next(iter(i))], i['Lesson Info'][j]['VENUE'], i['Lesson Info'][j]['GROUP'], i['Lesson Info'][j]['REMARK'], j[:-1], i['Lesson Info'][j]['TIME'], i['Lesson Info'][j]['DAY']] 
						pasteImage(info_list, original_timetable, colour_list[colour_counter])
				colour_counter += 1			

			original_timetable.save(img_path + 'Timetable.jpg', optimize=True,quality=90)	# Save the timetable image object as Timetable.jpg
			os.remove(img_path + 'timetable_original.bmp')
			return True

	def storeFeedbackToCSV(self, feedback):
		'''Return True if user's feedback is successfully stored in the Database/Feedback.csv file.'''
		with open('Database/Feedback.csv', 'a', newline='') as f:
			f_writer = csv.writer(f)
			f_writer.writerows([[self.chat_id, feedback]])
		return True