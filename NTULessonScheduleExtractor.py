import pandas
from bs4 import BeautifulSoup
import urllib.request
import re
import subprocess
from pyshorteners import Shortener
import os
from PIL import Image

class Courses:
	'''The 'Courses' class can be used to extract module information from NTU website.'''

	def __init__(self, course_code):
		def saveHTMLtodatabase(html_source):
			'''Save webpage to HTML in the database.'''
			file_name = 'Database/saved_webpage/' + str(self.course_code) + '.html'
			with open(file_name,'wb') as f:
				f.write(html_source)

		self.course_code = course_code
		self.course_url = 'https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE.main_display1?acadsem=2017;1&r_search_type=F&r_subj_code=' + self.course_code + '&boption=Search&staff_access=false'

		if os.path.isfile('Database/saved_webpage/' + str(self.course_code) + '.html'):	# Check if the HTML file of a module already exists.
			self.course_webpage_list = pandas.read_html('Database/saved_webpage/' + str(self.course_code) + '.html', header=0)
			self.course_webpage_dataframes = self.course_webpage_list[1]
			self.course_index_list = self.course_webpage_dataframes['INDEX'].tolist()
		else:
			self.course_webpage = urllib.request.urlopen(self.course_url).read()
			saveHTMLtodatabase(self.course_webpage)
			self.course_webpage_soup = BeautifulSoup(self.course_webpage, 'html.parser')
			try: # Check whether course code entered is valid
				self.course_webpage_list = pandas.read_html(self.course_webpage, header=0)
				if len(self.course_webpage_list) > 2:
					os.remove('Database/saved_webpage/' + str(self.course_code) + '.html')
				self.course_webpage_dataframes = self.course_webpage_list[1]
				self.course_index_list = self.course_webpage_dataframes['INDEX'].tolist()	
			except:
				self.course_webpage_list = []
				self.course_index_list = None
				os.remove('Database/saved_webpage/' + str(self.course_code) + '.html')
				print('There is no module called', self.course_code)

	def dataframeNumberChecker(self):
		'''Return True if there are more than two dataframes in the list.

		This method can be used to check whether user has entered a valid course code. For instance, if the user entered 'French', then there will be more than 2 tables showing different modules. This is to avoid mistakes in cases when users entered an invalid course code.

		'''
		if len(self.course_webpage_list) > 2:
			return True

	def getwebpagePNG(self):
		'''Return True if a screenshot of the webpage is generated or is already in the Database/webpage_screenshot folder. Return False if the course code is invalid.'''
		def compressPNG(png_path):
			'''Compress PNG iamges'''
			image = Image.open(png_path)
			image = image.resize(image.size,Image.ANTIALIAS)
			image.save(png_path, quality=95)

		if os.path.isfile('Database/webpage_screenshot/' + str(self.course_code) + '.png'): # Check if screenshot is already in Database/webpage_screenshot
			return True
		else:
			if os.path.isfile('Database/saved_webpage/' + str(self.course_code) + '.html'):	# Check if the webpage where the screenshot will be taken from is in Database/saved_webpage
				command = 'wkhtmltoimage -f png --width 0 ' + 'Database/saved_webpage/' + str(self.course_code) + '.html' + ' Database/webpage_screenshot/' + str(self.course_code)+ '.png'	# Convert the HTML file to .png format
				subprocess.call(command, shell=True)
				compressPNG('Database/webpage_screenshot/' + str(self.course_code)+ '.png')
				return True
			else:
				if not self.dataframeNumberChecker():
					if self.course_index_list:
						shortener = Shortener('Tinyurl')	
						shortened_url = shortener.short(self.course_url)	# Shorten the URL so that there is no error when the URL is written in the command prompt
						command = 'wkhtmltoimage -f png --width 0 ' + shortened_url + ' Database/webpage_screenshot/' + str(self.course_code)+ '.png'
						subprocess.call(command, shell=True)
						compressPNG('Database/webpage_screenshot/' + str(self.course_code)+ '.png')
						return True
					else:
						return False
				else:
					return False

	def getCourseIndexList(self):
		'''Returns a list of courses indices under a particular course index. Returns 'Please check your course code and re-enter!' if the course code in invalid.'''
		course_index_list_without = []

		if self.course_index_list != None:
			for course_index in self.course_index_list:
				if 'nan' in str(course_index):
					pass	# Remove all the 'nan' entries
				else:
					course_index_list_without.append(str(int(course_index)))
			else:
				return course_index_list_without
		else:
			return 'Please check your course code and re-enter!'

	def getCourseIndexInfo(self, course_index):
		'''Return a dataframe object containing all the relevant information of the course index of a course code.'''	
		self.course_index = course_index
		row_number = -1
		course_index_dict = {}

		if self.course_index_list == None:
			return 'Error in course code!'	# If the course code is invalid
		else:
			for course_index in self.course_index_list:
				if 'nan' in str(course_index):
					row_number += 1
					pass
				else:
					row_number += 1
					course_index_dict[str(int(course_index))] = row_number	# Dictionary with the course index as the keys and row number (in the dataframe) as the key

		course_index_keyList = sorted(course_index_dict.keys()) # List of all the row number of the each course index

		for i , j in enumerate(course_index_keyList):
			if j == self.course_index:
				if i == len(course_index_dict)-1:
					return self.course_webpage_dataframes[course_index_dict[course_index_keyList[i]] :]
				else:
					return self.course_webpage_dataframes[course_index_dict[course_index_keyList[i]] : course_index_dict[course_index_keyList[i+1]]]

	def getModuleInfo(self, course_index):
		'''Returns a dictionary of all the relevant information regarding a particular course index, such as course name, AU, time and venues, etc.'''
		module_info = list(self.course_webpage_list[0].columns.values)
		type_list = self.getCourseIndexInfo(course_index)['TYPE'].tolist()
		type_list_new = []
		x = 0
		for lesson_type in type_list:
			type_list_new.append(str(lesson_type) + str(x))	# To avoid cases where a single module has two lesson types (e.g. CZ1003 has two lectures per week), becasue later the lesson type of each lesson is used as the key of the dictionary and Python will discard items in the dictionary if they have the same key
			x += 1

		module_summary_dataframe = self.getCourseIndexInfo(course_index).drop('TYPE', 1)
		module_summary_dataframe.insert(loc=1, column='TYPE', value=type_list_new)
		module_summary_dictionary = module_summary_dataframe[module_summary_dataframe.columns[1:7]].set_index('TYPE').to_dict(orient = 'index')
		module_summary_dictionary = {module_info[0] : module_info[1] , 'AU' : module_info[2] , 'Lesson Info' : module_summary_dictionary}	# Dictionary with course code and course index as the key and value for the first item, 'AU' and Academic Unit of a course as the key and value for the second item and 'Lesson Info' and detailed info the module as the key and value for the third item.
		return module_summary_dictionary

	def getModuleInfoForSameModule(self, course_index, *args):
		'''Return a dictionary of any combination of the relevant information wanted by the user regarding a particular course index. 

		The only accepted arguments are  'INDEX' , 'TYPE' , 'DAY' , 'GROUP' , 'TIME' , 'VENUE' and 'REMARK'. Notice that all arguments are to be capitalized.

		'''
		self.args = args
		args_list = list(self.args)
		for a in args_list:
			if a == 'TYPE':
				module_any_dataframe = pandas.DataFrame(self.getCourseIndexInfo(course_index))
				module_any_dataframe = module_any_dataframe[list(self.args)]
				module_any_dictionary  = module_any_dataframe.set_index('TYPE').to_dict(orient = 'index')
				break
		else:
			args_list.append('TYPE')
			module_any_dataframe = pandas.DataFrame(self.getCourseIndexInfo(course_index))
			module_any_dataframe = module_any_dataframe[args_list]
			module_any_dictionary  = module_any_dataframe.set_index('TYPE').to_dict(orient = 'index')
		return module_any_dictionary