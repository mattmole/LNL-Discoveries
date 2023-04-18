#! /usr/bin/python3

# Import libraries
import datetime
import os
import feedparser
import lxml.html
import urllib
from rich import print
from rich.console import Console
import time
import ssl
from jinja2 import Template

dateGenerated = datetime.datetime.now().strftime("%d/%m/%Y")

# Time the processing
startTime = time.time()

# Clear the screen whenever the script is run
console = Console()
console.clear()

# Variables to store RSS feed URI and path to mkdocs folder
feedLink = "https://latenightlinux.com/feed/mp3"
basePath = '.'
showSlug = 'LateNightLinuxMkDocsV3/docs'
confFilePath = 'LateNightLinuxMkDocsV3/mkdocs.yml'
buildCmd = './buildSite.sh'

# Open template files
with open("templates/indexTemplate.md.j2") as f:
    indexTemplate = Template(f.read())

with open("templates/discoveriesTemplate.md.j2") as g:
    discoveriesTemplate = Template(g.read())

with open("templates/rssLinkTemplate.md.j2") as h:
    rssLinkTemplate = Template(h.read())

# List all currently generated MD files to determine if all episodes need to be processed


def listMdFiles():
    mdFiles = []
    dirList = os.listdir(os.path.join(basePath, showSlug))
    for dirObject in dirList:
        if os.path.isdir(os.path.join(basePath, showSlug, dirObject)):
            fileList = os.listdir(os.path.join(basePath, showSlug, dirObject))
            for file in fileList:
                if os.path.isfile(os.path.join(basePath, showSlug, dirObject, file)):
                    if os.path.splitext(os.path.join(basePath, showSlug, dirObject, file))[1] == ".md":
                        mdFiles.append(os.path.splitext(file)[0])
    return mdFiles

# Generate, from the site's HTML a string to represent the title and one to represent the meta description contents


def readMetaAndTitle(uri):
    data = ""
    # Load the HTML from the defined uri
    try:
        req = urllib.request.Request(uri, data=None, headers={
                                     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
        data = urllib.request.urlopen(req)
        data = data.read().decode("utf-8")
    except Exception as error:
        print(f"[red]\t\t\tError opening: {error} - {uri}")
        return {"title": "", "description": ""}

    # Parse the HTML using the lxml libraries
    pageHtml = lxml.html.fromstring(data)

    # Return the titles and format into a string
    titles = pageHtml.xpath("//head//title")
    titleString = ""
    for title in titles:
        if type(title.text) == type(""):
            titleString += title.text.strip().replace("\n", " - ")

    # Return the meta tags with the attribute name of description
    metaDescriptions = pageHtml.xpath("//meta[@name = 'description']")
    metaDescriptionString = ""
    for metaDescription in metaDescriptions:
        if "content" in metaDescription.attrib and metaDescription.attrib["content"] != "":
            if type(metaDescription.attrib["content"]) == type(""):
                tempString = metaDescription.attrib["content"].replace(
                    "\n", " - ").replace(
                    "\r", " - ").replace(
                    "\r\n", " - ").replace(
                    "\n\r", " - ")
                metaDescriptionString += tempString

    return {"title": titleString, "description": metaDescriptionString}


def processDiscoveries(paragraph):
    discoLinkList = []
    print(paragraph.getnext())

    links = paragraph.getchildren()
    print(links)
    for child in links:
        if child.tag == "a":
            discoveryText = child.text
            discoveryLink = child.attrib["href"]
            discoveryDetails = readMetaAndTitle(discoveryLink)
            if discoveryDetails["title"] == "" and discoveryDetails["description"] == "":
                discoveryDetails = readMetaAndTitle(discoveryLink)
            if discoveryDetails["title"] == "" and discoveryDetails["description"] == "":
                discoveryDetails = readMetaAndTitle(discoveryLink)
            discoLink = {"text": discoveryText, "link": discoveryLink,
                         "linkTitle": discoveryDetails["title"], "linkMetaDescription": discoveryDetails["description"]}
    return discoLinkList


# Load the RSS feed and create an empty dictionary and list to store episode details
feed = feedparser.parse(feedLink)
episodeAndLinks = {}
episodes = []

print("[yellow]Calculating already processed episodes...")
processedEpisodes = listMdFiles()

# Write the index file and include a modification date
print("[yellow]Writing index file...")

output = indexTemplate.render(
    {
        "dateGenerated": dateGenerated,
    }
)

with open(os.path.join(basePath, showSlug, 'index.md'), "w") as f:
    f.write(output)
    f.close()

# Iterate through each episode and work out which ones have discoveries
# detail the discoveries and add to a list / dictionary
print("[yellow]Iterating through episodes...")
count = 0
for episode in feed.entries:
    discoLinkList = []
    episodeName = episode.title
    episodeLink = episode.link
    print(f"[blue]\t{episode.title}")
    # Ignore if the episode has already got an MD file associated with it
    if episodeName in processedEpisodes:
        print("[green]\t\tAlready processed. Ignoring")
    else:
        # Process episodes if an MD file does not exist for it
        episodePublished = datetime.datetime.strptime(
            episode.published, "%a, %d %b %Y %H:%M:%S +0000")
        episodePublishedString = datetime.datetime.strptime(
            episode.published, "%a, %d %b %Y %H:%M:%S +0000").strftime("%d/%m/%Y")
        episodePublishedTimeString = datetime.datetime.strptime(
            episode.published, "%a, %d %b %Y %H:%M:%S +0000").strftime("%H:%M:%S")
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
                        # discoLinkList = processDiscoveries(paragraph)
                        # pass
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
                    discoLink = {"text": discoveryText, "link": discoveryLink,
                                 "linkTitle": discoveryDetails["title"], "linkMetaDescription": discoveryDetails["description"]}
                    discoLinkList.append(discoLink)
        if len(discoLinkList) > 0:
            episodes.append({'episodeName': episodeName, 'episodeLink': episodeLink, 'episodePublished': episodePublished,
                            'episodePublishedString': episodePublishedString, 'episodePublishedTimeString': episodePublishedTimeString, 'discoLinkList': discoLinkList})

# Now, write some files into a directory structure, detailing the links inside
# Create the base directory if it doesn't exist
if not (os.path.isdir(os.path.join(basePath, showSlug))):
    os.mkdir(os.path.join(basePath, showSlug))

# Create the rss directory if it doesn't exist
if not (os.path.isdir(os.path.join(basePath, showSlug, 'rss'))):
    os.mkdir(os.path.join(basePath, showSlug, 'rss'))

# Create the rss directory .pages file if it doesn't exist
if not (os.path.isfile(os.path.join(basePath, showSlug, 'rss', '.pages'))):
    f = open(os.path.join(basePath, showSlug, 'rss', '.pages'), 'w')
    f.write("hide: true")
    f.close()
    os.mkdir(os.path.join(basePath, showSlug, 'rss'))

print("[yellow]Writing MD files and directories")
for episode in episodes:
    # Create a folder for each year within the feed
    if not (os.path.isdir(os.path.join(basePath, showSlug, str(episode['episodePublished'].year)))):
        os.mkdir(os.path.join(basePath, showSlug,
                 str(episode['episodePublished'].year)))
    # Create a file for each episode
    output = discoveriesTemplate.render(
        {
            "episode": episode,
        }
    )

    with open(os.path.join(basePath, showSlug, str(
            episode['episodePublished'].year), episode['episodeName']+'.md'), "w") as f:

        f.write(output)
    print('[red]\tWritten file for...', episode['episodeName'])

# Now generate the RSS links
print('[yellow]Writing files for RSS feed')
for episode in episodes:
    for discovery in episode["discoLinkList"]:
        output = rssLinkTemplate.render(
            {
                "episode": episode,
                "discovery": discovery
            }
        )
        backslashChar = "\'"
        with open(os.path.join(basePath, showSlug, 'rss', f'{episode["episodeName"]} - {discovery["text"].replace("/","").replace(backslashChar,"").replace("&","")}.md'), "w") as f:
            f.write(output)
    print('[red]\tWritten file for...', episode['episodeName'], '-',
          discovery["text"].replace("/", "").replace(backslashChar, "").replace("&", ""), '.md')

print('[yellow]Generating site...')
os.system(buildCmd)

endTime = time.time()
print(f"Time taken to run: {round(endTime-startTime,0)}s")
