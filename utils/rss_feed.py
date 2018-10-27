import requests
from xml.etree import ElementTree
import pickle
import os

def array_to_dict_items(items, keyname):
    ret_dict = {}
    for i in items:
        print(i)
        ret_dict[i[keyname]] = i
    return ret_dict

class RSSFeed:
    def __init__(self, url):
        self.items=[]
        self.old_items = None
        res = requests.get(url)
        root = ElementTree.fromstring(res.text)
        self._parse_content(root)

    def _parse_content(self, root):
        channel = root.find('channel')
        self.title = channel.find('title').text
        self.description = channel.find('description').text
        self.url = channel.find('link').text
        self._parse_image_url(channel)
        self._parse_items(channel)

    def _parse_image_url(self, channel):
        image = channel.find('image')
        self.image_url = image.find('url').text

    def _parse_items(self, channel):
        for item in channel.findall('item'):
            self._parse_single_item(item)

    def _parse_single_item(self, item):
        self.items.append(Item(item))

    def get_dict(self):
        items = [{
                'title' : i.title,
                'description' : i.description,
                'url' : i.url,
                'item' : i.date,
            }
            for i in self.items]
        ret = {
            'title' : self.title,
            'description' : self.description,
            'url': self.url,
            'image_url' : self.image_url,
            'items': items
        }
        return ret
    
    def get_items_as_dict(self):
        items_dict = []
        for x in self.items:
            items_dict.append({
                'title' : self.title,
                'url' : self.url,
                'image_url' : self.image_url,
                'item_title' : x.title,
                'item_description' : x.description,
                'item_url' : x.url,
                'item_date' : x.date
            })
        return items_dict

class Item:
    def __init__(self, item):
        self.title = item.find('title').text
        self.description = item.find('description').text
        self.url = item.find('link').text
        self.date = item.find('pubDate').text

