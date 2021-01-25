# So, we’ll need 4 packages:
# requests — for downloading the HTML code from a given URL
# beautiful soup — for extracting data from that HTML string
# re — Python has a module named re to work with RegEx
# pprint — It Provides a capability to “pretty-print” data in a well-formatted and more readable way!
# install Modules By
# python -m pip install requests beautifulsoup4

import requests
import pprint, re
from bs4 import BeautifulSoup as bs

class VideoScraper:
    def __init__(self, url) -> None:
        self.url = url
    
    def get_video_details(self) -> dict:

        # Making a GET request 
        response = requests.get(self.url)

        # response.text returns the content of the response in Unicode.
        # Here we preferred for textual responses, such as an HTML or XML document so response.text is used instead of response.content, 
        
        # bs4 arguments
        # markup_string — the string of our web page
        # parser — a string consisting of the name of the parser to be used; here we will use python’s default parser: “html.parser”
        
        soup = bs(response.text, "html.parser")

        # For View The HTML Data
        # f = open("save.txt", "a")
        # f.write(str(soup.prettify()))
        # f.close()
        
        # Define object to store data
        video_details = {}

        # Parsing Data From Meta Tag

        # for tag in soup.find_all("meta"):
        #     print(tag)

        video_details["title"] = soup.find("meta",  property="og:title").attrs['content']
        video_details["view"] = soup.select_one('meta[itemprop="interactionCount"][content]').attrs['content']
        video_details["description"] = soup.find("meta",  property="og:description").attrs['content']
        video_details["tags"] = ', '.join([ meta.attrs['content'] for meta in soup.find_all("meta", property ="og:video:tag")])
        video_details["datePublished"] = soup.select_one('meta[itemprop="datePublished"][content]').attrs['content']
        video_details["uploadDate"] = soup.select_one('meta[itemprop="uploadDate"][content]').attrs['content']
        video_details["Category"] = soup.select_one('meta[itemprop="genre"][content]').attrs['content']
        video_details["channelId"] = soup.select_one('meta[itemprop="channelId"][content]').attrs['content']
        video_details["videoId"] = soup.select_one('meta[itemprop="videoId"][content]').attrs['content']

        # Parsing From Single Span Elements
        video_details["thumbnail"] = soup.find("span", itemprop="thumbnail").find('link')['href']

        # Channel Url Common For All Except Channel ID
        video_details["channelUrl"] = "https://www.youtube.com/channel/"+video_details["channelId"]
        
        # Remaining Data Parsing From JS Data Fields Which is Subscribers Count, Likes, Dislikes & Videolength
        subsDetails = soup(text=lambda t: "subscriberCountText" in t)
        video_details["subscribers"] = str(subsDetails)[str(subsDetails).index("subscriberCountText"):str(subsDetails).index("subscribers")].split('"')[-1].strip()
        
        likeAndDislike = soup(text=lambda t: '''"iconType":"LIKE"''' in t)
        video_details["likes"] = str(likeAndDislike)[str(likeAndDislike).index('''"iconType":"LIKE"'''):str(likeAndDislike).index('''likes''')].split('''"''')[-1].strip()
        video_details["dislikes"] = str(likeAndDislike)[str(likeAndDislike).index('''"iconType":"DISLIKE"'''):str(likeAndDislike).index('''dislikes''')].split('''"''')[-1].strip()
        
        videoLength = soup(text=lambda t: '''"lengthSeconds"''' in t)
        start = str(videoLength).find("lengthSeconds")
        end = str(videoLength).find("keywords")
        video_details["videoLength"] = self.hms(int(re.findall(r'\d+', str(videoLength)[start:end])[0] if len(re.findall(r'\d+', str(videoLength)[start:end])) != 0 else None))
        
        return video_details


    def hms(self,seconds) -> str:
        h = seconds // 3600
        m = seconds % 3600 // 60
        s = seconds % 3600 % 60
        return '{:02d}:{:02d}:{:02d}'.format(h, m, s)

if __name__ == '__main__':
    data = VideoScraper('https://youtu.be/iFSJhENRLZY').get_video_details()
    pprint.pprint(data)