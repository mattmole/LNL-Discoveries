import datetime
#from bs4 import BeautifulSoup
import os
import feedparser
import lxml.html
import urllib
from rich import print
from rich.console import Console
import time
import ssl

startTime = time.time()

console = Console()
console.clear()

feedLink = "https://latenightlinux.com/feed/mp3"
basePath = '.'
showSlug = 'LateNightLinuxMkDocsV2/docs'

#print(f.read().decode('utf-8'))

def readMetaAndTitle(uri):
    #Load the HTML from the defined uri
    try:
        #file = urllib.request.urlopen(uri)
        #data = file.read()
        #file.close()
        req = urllib.request.Request(uri,data=None,headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
        data = urllib.request.urlopen(req)
        data = data.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        print(f"[red]\t\t\tError opening: {error} - {uri}")
        return {"title":"","description":""}
    except urllib.error.URLError as error:
        print(f"[red]\t\t\tError opening: {error} - {uri}")
        return {"title":"","description":""}
    except ssl.SSLError as error:
        print(f"[red]\t\t\tError opening: {error} - {uri}")
        return {"title":"","description":""}
    #Parse the HTML using the lxml libraries
    pageHtml = lxml.html.fromstring(data)

    #Return the titles and format into a string
    titles = pageHtml.xpath("//title")
    titleString = ""
    for title in titles:
        titleString += title.text.strip()

    #Return the meta tags with the attribute name of description
    metaDescriptions = pageHtml.xpath("//meta[@name = 'description']")
    metaDescriptionString = ""
    for metaDescription in metaDescriptions:
        if "content" in metaDescription.attrib and metaDescription.attrib["content"] != "":
            metaDescriptionString += metaDescription.attrib["content"].strip()
    return {"title":titleString,"description":metaDescriptionString}

feed = feedparser.parse(feedLink)
episodeAndLinks = {}
episodes = []

# Write the index file and include a modification date
print("[yellow]Writing index file...")
indexFile = open(os.path.join(basePath, showSlug, 'index.md'), "w")
indexFile.write("# Late Night Linux Discoveries"+os.linesep)
indexFile.write(os.linesep)
indexFile.write(
    "Please use the links in the menu to view discoveries from each of the relevant episodes."+os.linesep)
indexFile.write(os.linesep)
indexFile.write("Generated on: " +
                datetime.datetime.now().strftime("%d/%m/%Y"))
indexFile.close()

# Iterate through each episode
print("[yellow]Iterating through episodes...")
count = 0
for episode in feed.entries:
    discoLinkList = []
    episodeName = episode.title
    episodeLink = episode.link
    print(f"[blue]\t{episode.title}")
    episodePublished = datetime.datetime.strptime(
        episode.published, "%a, %d %b %Y %H:%M:%S +0000")
    episodePublishedString = datetime.datetime.strptime(
        episode.published, "%a, %d %b %Y %H:%M:%S +0000").strftime("%d/%m/%Y")

    # Find the rows in the encoded content that referencies <strong>Discoveries and the next tag of strong
    pageHtml = lxml.html.fromstring(episode.content[0].value)
    paragraphs = pageHtml.xpath("//p")
    lowCount = -1
    highCount = -1
    counter = 0
    print(f"[green]\t\tFinding discoveries")
    for paragraph in paragraphs:
        if len(paragraph) > 0:
            paragraph = paragraph.getchildren()[0]
            if paragraph.tag == "strong":
                if type(paragraph.text) == type("") and 'Discoveries' in paragraph.text:
                    lowCount = counter
                    pass
                elif lowCount > -1:
                    highCount = counter
                    break
        counter += 1

    # Now print discoveries, using the values from the previous loop
    print(f"[green]\t\tWorking out details from the link")
    for i in range(lowCount, highCount):
        a = paragraphs[i].getchildren()
        for child in a:
            if child.tag == "a":
                discoveryText = child.text
                discoveryLink = child.attrib["href"]
                discoveryDetails = readMetaAndTitle(discoveryLink)
                if discoveryDetails["title"] == "" and discoveryDetails["description"] == "":
                    discoveryDetails = readMetaAndTitle(discoveryLink)
                if discoveryDetails["title"] == "" and discoveryDetails["description"] == "":
                    discoveryDetails = readMetaAndTitle(discoveryLink)    
                discoLink = {"text":discoveryText, "link":discoveryLink, "linkTitle":discoveryDetails["title"], "linkMetaDescription": discoveryDetails["description"]}
                discoLinkList.append(discoLink)
    if len(discoLinkList) > 0:
        episodes.append({'episodeName': episodeName, 'episodeLink': episodeLink, 'episodePublished': episodePublished,
                        'episodePublishedString': episodePublishedString, 'discoLinkList': discoLinkList})


# Now, write some files into a directory structure, detailing the links inside

if not (os.path.isdir(os.path.join(basePath, showSlug))):
    os.mkdir(os.path.join(basePath, showSlug))

print("[yellow]Writing MD files and directories")
for episode in episodes:
    # Create a folder for each year within the feed
    if not (os.path.isdir(os.path.join(basePath, showSlug, str(episode['episodePublished'].year)))):
        os.mkdir(os.path.join(basePath, showSlug,
                 str(episode['episodePublished'].year)))
    # Create a file for each episode
    fw = open(os.path.join(basePath, showSlug, str(
        episode['episodePublished'].year), episode['episodeName']+'.md'), 'w')

    fw.write("# " + episode['episodeName']+os.linesep)
    fw.write("Episode Link: ["+episode['episodeLink'] +
             "](" + episode['episodeLink']+")  "+os.linesep)
    fw.write("Release Date: "+episode['episodePublishedString']+os.linesep)
    fw.write("## Discoveries"+os.linesep+os.linesep)
    
    fw.write(f'| Name and Link | Page Title | Page Description |{os.linesep}')
    fw.write('| ----- | ----- | ----- |'+os.linesep)
    for disco in episode['discoLinkList']:
        fw.write(f"| [{disco['text']}]({disco['link']}) | {disco['linkTitle']} | {disco['linkMetaDescription']} |{os.linesep}")
    fw.write(os.linesep)
    fw.write("Generated on: " + datetime.datetime.now().strftime("%d/%m/%Y"))
    fw.close()
    print('[red]\tWritten file for...', episode['episodeName'])    

endTime = time.time()
print(f"Time taken to run: {round(endTime-startTime,0)}s")