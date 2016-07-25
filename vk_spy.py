import concurrent.futures

import vk

vkapi = vk.API(vk.Session(), v='5.12', lang='ru', timeout=100)
ac = '08c326c34b6278484bb6af6f697043f447d70d7f5490075eda22755b07625585175bf32e4ee4b549a4bc9'
user_id = '1'
items = []

users = vkapi.friends.get(user_id=user_id)['items']
print(users)
print(len(users))
items.extend(users)

groups = vkapi.groups.get(user_id=user_id,
                          access_token=ac)['items']
print(groups)
print(len(groups))
items.extend([-g for g in groups])

for item in items:
    print(item)


def is_liked(post):
    end = False
    while not end:
        try:
            liked = vkapi.likes.isLiked(user_id=user_id,
                                        owner_id=post['owner_id'],
                                        item_id=post['id'],
                                        type='post',
                                        access_token=ac)['liked']
            if liked:
                print("Found like! ", liked, post)

            end = True
            return liked
        except:
            pass


def analyze_posts(posts):
    for post in posts:

        likes_info = vkapi.likes.getList(owner_id=post['owner_id'],
                                         item_id=post['id'],
                                         type='post')

        # print('likes count =', likes_info['count'])

        liked = False
        if likes_info['count'] > 100:
            liked = is_liked(post)

        else:
            liked = int(user_id) in likes_info['items']

        if liked:
            print("Found like! ", liked, post)
            if post['post_type'] == 'post':
                print("https://new.vk.com/feed?w=wall{}_{}".format(post['owner_id'], post['id']))




for item in items:
    try:
        posts = []
        posts_temp = vkapi.wall.get(owner_id=item, offset=len(posts), count=100)['items']
        posts.extend(posts_temp)
        print('item {} {}'.format(item, len(posts)))

        # while not end:
        #     posts_temp = vkapi.wall.get(owner_id=-g, offset=len(posts), count=100)
        #     # print(posts_temp)
        #     if len(posts) >= 500 or posts_temp['count'] < 100: end = True
        #     posts_temp_2 = posts_temp['items']
        #     for post in posts_temp_2:
        #         post_id = '{}_{}'.format(post['owner_id'], post['id'])
        #         # print(post_id)
        #         posts.append(post_id)
        #
        # print('group {} {}'.format(g, len(posts)))

        analyze_posts(posts)
    except:
        pass


# print('group {} {}'.format(g, len(posts)))
