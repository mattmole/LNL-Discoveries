import datetime
from bs4 import BeautifulSoup
import os
import feedparser

feedLink = "https://latenightlinux.com/feed/mp3"
basePath = '.'
showSlug = 'LateNightLinuxMkDocs/docs'


feed = feedparser.parse(feedLink)
episodeAndLinks = {}
episodes = []

# Write the index file and include a modification date
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
count = 0
for episode in feed.entries:
    discoLinkList = []
    episodeName = episode.title
    episodeLink = episode.link
    episodePublished = datetime.datetime.strptime(
        episode.published, "%a, %d %b %Y %H:%M:%S +0000")
    episodePublishedString = datetime.datetime.strptime(
        episode.published, "%a, %d %b %Y %H:%M:%S +0000").strftime("%d/%m/%Y")

    page_soup = BeautifulSoup(episode.content[0].value, "html.parser")

    # Find the rows in the encoded content that referencies discoveries and feedback
    lowCount = -1
    highCount = -1
    counter = 0
    for row in page_soup:
        if 'Discoveries' in row.text:
            lowCount = counter
        if row.text == 'Feedback' or row.text == "KDE Korner" or row.text == 'AI “art”' or row.text == 'Tailscale' or row.text == 'Ken VanDine' or row.text == 'Mailing lists are on the wane':
            highCount = counter
            break
        counter += 1

    # Now print discoveries, using the values from the previous loop
    counter = 0
    for row in page_soup:
        if counter < highCount and counter > lowCount and lowCount > -1:
            if row.text.strip() != '':
                discoveryLink = 'No link available'
                try:
                    discoveryLink = row.find('a')['href']
                except:
                    pass
                discoveryText = row.text
                discoLink = {'text': discoveryText, 'link': discoveryLink}
                # print(discoLink)
                discoLinkList.append(discoLink)
        counter += 1
    if len(discoLinkList) > 0:
        episodes.append({'episodeName': episodeName, 'episodeLink': episodeLink, 'episodePublished': episodePublished,
                        'episodePublishedString': episodePublishedString, 'discoLinkList': discoLinkList})


# pip install feedparser

# Now, write some files into a directory structure, detailing the links inside

if not (os.path.isdir(os.path.join(basePath, showSlug))):
    os.mkdir(os.path.join(basePath, showSlug))

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
    fw.write("## Discoveries"+os.linesep)
    print('Written file for...', episode['episodeName'])
    for disco in episode['discoLinkList']:
        fw.write("* [" + disco['text']+'](' + disco['link']+')'+os.linesep)
    fw.write(os.linesep)
    fw.write("Generated on: " + datetime.datetime.now().strftime("%d/%m/%Y"))
    fw.close()
### dict_keys(['title', 'title_detail', 'links', 'link', 'published', 'published_parsed', 'id', 'guidislink', 'comments', 'wfw_commentrss', 'slash_comments', 'tags', 'summary', 'summary_detail', 'content', 'subtitle', 'subtitle_detail', 'authors', 'author', 'author_detail', 'image', 'itunes_duration'])
