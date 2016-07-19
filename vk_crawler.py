# coding=utf-8
import concurrent.futures
import time
import vk
import pymongo

try:
    pymongo.MongoClient(host="192.168.13.133")['VkFest'].create_collection('vk_data', capped=True, size=99999999999)
    print("Table created")
except:
    print("Table already created")


tags = [u'#spb', u'#saint', u'#питер', u'#спб', u'#санктпетербург', u'#санкт-петербург']
timeout = 100


def task(tag, request_timeout):
    vkapi = vk.API(vk.Session(), v='5.12', lang='ru', timeout=request_timeout)
    vk_posts_collection = pymongo.MongoClient(host="192.168.13.133")['VkFest']['vk_data']

    added_count = 0
    try:
        posts = vkapi.newsfeed.search(q=tag, count='200')['items']
        added_count += len(posts)
        for post in posts:
            print(post)
            key = {'_id': "{}_{}".format(post['owner_id'], post['id'])}
            fields = {'$set': post}
            updated_result = vk_posts_collection.update(key, fields, True, False)
            added_count += not updated_result['updatedExisting']
    except:
        pass

    return added_count


def start():
    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tags)) as executor:

            futures = {executor.submit(task, tag, timeout): tag for tag in tags}
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                try:
                    data = future.result()
                    print(u'{} added {} post'.format(url, data))
                except Exception as e:
                    print(u"{} generated an exception {}".format(url, e))

        time.sleep(1)


if __name__ == '__main__':
    start()
