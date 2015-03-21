"""
Author: Nicholas Rutherford
License: MIT
"""

import datetime
import sys
import websiteBlocks
import sumUtil

SUM_DIR = "./hnSummarized/summaries/"
WEBSITE = "./hnSummarized/website/index.html"
STORIES_PER_ROW = 2


def elementBlock(title, keywords, summary, article, comments):
    """Format given variables into the HTML code block for a story

    Args:
        title (str): The title of the story.
        keywords (str): The keywords associated with the story.
        summary (str): The story summary.
        article (str): The link to the actual story
        comments (str): The link to the HN comments page

    Returns:
        String. HTML code with the variables put into the correct locations
    """
    block = websiteBlocks.ELEMENT
    return block.format(title, keywords, summary, article, comments)

def formatDate(itemDate):
    """Format the date into the HTML code block for the date

    Args:
        itemDate (str): The date as a string in the form yyyy-mm-dd

    Returns:
        str. HTML code for the date
    """
    # Get the current date in the format yyyy-mm-dd
    today = datetime.datetime.now().date().isoformat()

    if itemDate == today:
        return websiteBlocks.DATE.format("Today")
    else:
        try:
            y, m , d = itemDate.split("-")
            dateOb = datetime.date(int(y), int(m), int(d))
        except ValueError:
            print "Warning: Invalid date format:", itemDate
            dateText = "------"
        else:
            dateText = dateOb.strftime("%B %d, %Y") # January 01, 2015

        return websiteBlocks.DATE.format(dateText)


def loadHNData(info, fileID):
    """Load the data stored from the HN api

    Args:
        info (dict): Dictionay of HN data
        fileID (str): The unique ID of the story

    Returns:
        title (str): The title of the story
        article (str): The link to the actual story
        comments (str): The link to the HN comment section for this story

    Raises:
        Exit - Missing data for this file
    """
    try:
        title = info[fileID]["title"].encode("ascii", "ignore")
        article = info[fileID]["url"].encode("ascii", "ignore")
        comments = info[fileID]["comments"].encode("ascii", "ignore")
    except KeyError:
        print "Error: No info entry for ID: ", fileID
        sys.exit(1)
    return title, article, comments

def formatStory(downFile, folder, info):
    """Format the story data into the HTML code block for a story

    Args:
        downFile (str): The path to the summarized story
        folder (str): The folder of the story
        info (dict): Dictionary of HN data

    Returns:
        str. HTML code for the story

    Raises:
        Exit. If file can not be opened.
    """

    path = SUM_DIR + folder + "/" + downFile
    summaryText = sumUtil.loadFile(path)
    keywords, summary = summaryText.split("\n")

    # ID is the name of the file (excluding extension)
    fileID = downFile.split(".")[0]

    title, article, comments = loadHNData(info, fileID)

    return elementBlock(title, keywords, summary, article, comments)


def formatRows(downFile, folder, info, storyNum,):
    """Format the story into an element of the current row.

    Args:
        downFile (str): The path to the summarized story
        folder (str): The folder of the story
        info (dict): Dictionary of HN data
        storyNum (int): The current story number

    Returns:
        str. HTML code for this element of the row

    Raises:
        Exit. If file can not be opened.
    """

    storyText = ""

    # Start a new row
    if storyNum % STORIES_PER_ROW  == 0:
        storyText += websiteBlocks.ROW

    storyText += formatStory(downFile, folder, info)

    # End a row
    if (storyNum % STORIES_PER_ROW) == (STORIES_PER_ROW - 1):
        storyText += websiteBlocks.ROW_END

    return storyText



def constructWebsite():
    """Contructs a website from the summarized data

    Requirements:
        Summaries must be stored in the summaries folder, with a subfolder
        for separate dates.

    WEBSITE denotes where the file is saved
    """

    # Load saved HN api data
    info = sumUtil.loadInfo()

    webpage = ""
    webpage += websiteBlocks.HEADER

    storyNum = 0

    for folder in sumUtil.listDirectory(SUM_DIR):

        webpage += formatDate(folder)

        fileList = sumUtil.listDirectory(SUM_DIR + folder)
        for downFile in fileList:
            webpage += formatRows(downFile, folder, info, storyNum)
            storyNum += 1

        # Close rows with imperfect number of stories
        if len(fileList) % STORIES_PER_ROW != 0:
            webpage += websiteBlocks.ROW_END

    sumUtil.saveFile(webpage, WEBSITE)

if __name__ == '__main__':
    constructWebsite()
