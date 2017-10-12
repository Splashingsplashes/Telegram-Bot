# Can Pon Or Not? Telegram Bot
This is a collaborative project among Wenxuan, Huang Peng, Shenggui, Daifei and Yanxi. The aim of the project is to create a Telegram bot as part of the assignment under CZ1003 Introduction to Computational Thinking.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

To run the bot on your device, Python 3.6.2 must be installed on your machine. To download Python 3.6.2, go to [Python 3.6.2](https://www.python.org/downloads/release/python-362/)

After installing Python 3.6.2, intall the following modules with Pip:

* pandas (0.20.3)
* pillow (4.2.1)
* telepot (12.3)
* numpy (1.13.1)
* pyshorteners (0.6.1)
* lxml (3.8.0)
* html5lib (0.999999999)
* beautifulsoup (4.6.0)

Install font Lato, you can download the font from [Google Fonts](https://fonts.google.com/)

Lastly, install [Wkhtmltopdf](https://wkhtmltopdf.org/downloads.html), and add it to environment variables.

### Installing

Below is an example of how to install telepot with pip in Command Prompt on Windows:

```
pip install telepot
```

The package is successfully installed when the following message is shown in the Command Prompt:

```
Successfully installed telepot-12.3
```

### Instructions on uses

Open the MainPage.py file with any text editor of your choice, and put your own Telegram bot token in line 394. Save and run!

## Directory Structure

```
CanPonOrNot
│   README.md
│   Global_variables.py
│   Lab_full.py
│   LessonScheduler.py
│   MainPage.py
│   NTULessonScheduleExtractor.py  
│
└───Database
    │   Feedback.csv
    │   timetable_original.bmp
    │   usermoduleinfo.csv
    │
    └───Resources
    │   │   botpic.jpg
    │   │   Lato-Regular.ttf
    │   │   timetable.psd
    │   
    └───saved_webpage 
    │   │   coursecode1.html
    │   │   coursecode2.html
    │   │   coursecode3.html
    │   │   ...
    │ 
    └───user_timetable_info
    │   │
    │   └───chat_id1
    │   │   │   chat_id1.csv
    │   │   │   Timetable.jpg
    │   │   
    │   └───chat_id2
    │   │   │   chat_id2.csv
    │   │   │   Timetable.jpg
    │   │   
    │   └───chat_id1
    │   │   │   chat_id1.csv
    │   │   │   Timetable.jpg
    │   │   
    │   └───...
    │   
    └───webpage_screenshot
        │   coursecode1.png
        │   coursecode2.png
        │   coursecode3.png
        │   ...

```

### Explanation of each file and folder

* **README.md** The readme file.
* **Global_variables.py** File created for the various variables used in the MainPage.py. This is created to avoid the confusion caused by local namespace of defined function.
* **Lab_full.py** This file is created to solve the problem of the NTU Campus Map Website since some of the locations cannot be indexed by abbreviations. The script contains functions to search for the full name of the labs with abbreviations so that NTU Campus Map can search the desired location with abbreviation.
* **LessonScheduler.py** Module that defines a class and offers various methods to get list of course codes or course indices registered by a specific user, get the info of next lesson of a user, generate timetable in .jpeg format, etc.
* **MainPage.py** Main script to be run to use the bot on Telegram.
* **NTULessonScheduleExtractor.py** Module used to scrape info from NTU Schedule website
* **Database** Where all the data are stored
  * **Feedback.csv** Stores all the feedback of users.
  * **timetable_original.bmp** The original timetable image from which the generated user timetable is converted from.
  * **usermoduleinfo.csv** Stores users' chat id as well as each users' corresponding course code (e.g. CZ1003) and course index (e.g. 10101).
  * **Resources**
    * **botpic.jpg** Profile picture of the bot
    * **Lato-Regular.ttf** Font used for the generation of timetable
    * **timetable.psd** Original .psd file of the timetable
  * **saved_webpage** Contains all the saved webpages in .html format so that if the webpage exists in the local database, the scraper doesn't have to go online and scrape again, effectively saving time.
  * **user_timetable_info** Each subfolder in this folder contains the timetable (in .jpeg format) as well as a .csv file which stores all the module info which a user registered.
  * **webpage_screenshot** Contains all the screenshot of the websites, so that if the screenshot of a particular course exists in our local database, the bot can send the screenshot directly to the user without having to open the website and screenshot again.

## Deployment

The bot was deloyed on Microsoft Azure Virtual Machine running Microsoft Server 2016.

## Contributors

The names are in alphabetical order.

* **Feng Daifei**
* **Huang Peng**
* **Li Shenggui**
* **Wu Wenxuan**
* **Zeng Yanxi**

## Acknowledgments

* Thank Prof. Lua Ruiping for providing us with the opportunity to use this project to push our group members out of comfort zone to try out new things.
* Thank Huang Peng, Shenggui and Wenxuan for dilligently writing and testing the code.
* Thank Daifei and Yanxi for writing the report, writing and testing the bot.

