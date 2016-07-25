# coding=utf-8

import threading
from datetime import datetime, time
import pymongo
import time

from tornado import websocket, web, ioloop
import json


class Post:
    def __init__(self, data):
        self.data = data

        if 'post_type' not in data.keys():
            data['type'] = "photo"
            data['url'] = "https://new.vk.com/id{}?z=photo{}_{}".format(data['owner_id'], data['id'], data['owner_id'])
        else:
            data['type'] = "post"
            data['url'] = "https://new.vk.com/feed?w=wall{}_{}".format(data['owner_id'], data['id'])

        if 'geo' in data.keys():
            geo = data['geo']['coordinates'].split(' ')
            data['lat'] = float(geo[0])
            data['long'] = float(geo[1])

        if 'attachments' in data.keys():
            for a in data['attachments']:
                if a['type'] == 'photo':
                    if 'photo_807' in a['photo'].keys():
                        data['photo_url'] = a['photo']['photo_807']
                        data['photo_url_75'] = a['photo']['photo_75']
                        break
                    else:
                        sizes = list(filter(lambda p: p.startswith('photo'), a['photo'].keys()))
                        maxsize = max(list(map(lambda p: int(p.replace("photo_", '')), sizes)))
                        data['photo_url'] = a['photo']['photo_' + str(maxsize)]
                        data['photo_url_75'] = a['photo']['photo_75']
                        break

        if 'photo_75' in data.keys():
            sizes = list(filter(lambda p: p.startswith('photo'), data.keys()))
            maxsize = max(list(map(lambda p: int(p.replace("photo_", '')), sizes)))
            data['photo_url'] = data['photo_' + str(maxsize)]
            data['photo_url_75'] = data['photo_75']


clients = set()

to_unixtime = lambda datetime_: int(time.mktime(datetime_.timetuple()))


def stream_new_posts():

    q = {'date': {'$gte': to_unixtime(datetime.today())}}

    time.sleep(5)

    db = pymongo.MongoClient("192.168.13.133").VkFest
    coll = db.data
    cursor = coll.find(q, cursor_type=pymongo.CursorType.TAILABLE_AWAIT)
    while True:
        for doc in cursor:
            p = Post(doc)
            print(p.data)
            if 'lat' in p.data.keys() and 'photo_url' in p.data.keys():
                for client in clients:
                    client.write_message(p.data)
        time.sleep(0.5)
        print("")


thread = threading.Thread(target=stream_new_posts)
thread.start()


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("vkmap.html")


class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in clients:
            clients.add(self)

    def on_close(self):
        if self in clients:
            clients.remove(self)


app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler)
])

if __name__ == '__main__':
    app.listen(8888)
    ioloop.IOLoop.instance().start()
