import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
import urllib.request

def download_thumbs(url):
    result = requests.get(url)

    if result.status_code != 200:
        return None

    content = result.content

    soup = BeautifulSoup(content, "html.parser")

    image_cells = soup.find_all(class_="galImageCell")
    j = 0
    for image_cell in image_cells:
        j = j + 1
        img_page = image_cell.a['href']
        img_location = image_cell.img['src']
        med_location = img_location.upper().find("/MED/")
        img_location = img_location[:med_location] + "/LRG/" + img_location[med_location+5:]
        o = urlparse(img_location)
        file_name = os.path.basename(o.path)
        print (str(j).rjust(2) + ": " + file_name)
        urllib.request.urlretrieve(img_location,"downloaded_images/" + file_name)

url_front = "http://www.art.co.uk/gallery/id--b1833-h207271/scenic-prints_p"
url_back = ".htm?ui=B8FD8CDA59CD447799729C04971D4606"

for i in range(1, 11):

    url = url_front + str(i) + url_back
    print ("Page " + str(i))
    download_thumbs(url)
