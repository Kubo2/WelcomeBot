import urllib2
import json

def search(string):
  ddg = urllib2.urlopen("https://api.duckduckgo.com/?q=" + string + "&format=json&pretty=1")
  result = json.load(ddg)
  return result[1]["Heading"]
  
