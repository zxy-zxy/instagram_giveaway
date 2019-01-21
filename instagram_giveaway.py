import argparse
import os
import sys
import re
import pprint

from dotenv import load_dotenv
from instabot import Bot

bot = Bot()


def get_user_id(username):
    user_id = bot.get_user_id_from_username(username.lstrip('@'))
    return user_id


def confirm_mentioned_users_are_exists(mentioned_usernames):
    users_exists = []
    for username in mentioned_usernames:
        user_id = get_user_id(username)
        if user_id is None:
            continue
        users_exists.append(user_id)
    return users_exists


def get_usernames_mentioned_in_comment(comment_text):
    pattern = '(?:@)([A-Za-z0-9_](?:(?:[A-Za-z0-9_]' \
              '|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)'
    return re.findall(pattern, comment_text)


def comment_satisfies_conditions(comment, post_likers, author_followers):
    comment_text = comment['text']
    comment_author_user_id = comment['user_id']

    usernames_mentioned_in_comment = get_usernames_mentioned_in_comment(
        comment_text)
    if not usernames_mentioned_in_comment:
        return False

    users_mentioned_in_comment = confirm_mentioned_users_are_exists(
        usernames_mentioned_in_comment)
    if not usernames_mentioned_in_comment:
        return False

    user_followers = bot.get_user_followers(comment_author_user_id)

    followers_mentioned_users_intersection = \
        set(users_mentioned_in_comment).intersection(set(user_followers))

    if not followers_mentioned_users_intersection:
        return False

    if str(comment_author_user_id) not in post_likers:
        return False

    if str(comment_author_user_id) not in author_followers:
        return False

    return True


def get_post_likers(post_id):
    post_likers = bot.get_media_likers(post_id)
    return post_likers


def get_author_followers(author_username):
    author_user_id = bot.get_user_id_from_username(author_username)
    return bot.get_user_followers(author_user_id)


def get_all_allowed_competitors(author_username, post_id):
    post_comments = bot.get_media_comments_all(post_id)
    post_likers = get_post_likers(post_id)
    author_followers = get_author_followers(author_username)

    competitors = []
    pprint.pprint(post_comments, indent=4)
    for post_comment in post_comments:
        user_id = post_comment['user']['pk']
        username = post_comment['user']['username']
        if comment_satisfies_conditions(
                post_comment,
                post_likers,
                author_followers
        ):
            competitors.append((user_id, username))
    competitors = set(competitors)
    return competitors


def get_post_id(post_url):
    post_id = bot.get_media_id_from_link(post_url)
    return post_id


def authenticate_with_bot(instagram_login, instagram_password):
    load_dotenv()

    loggged_in_succesfully = bot.login(
        username=instagram_login,
        password=instagram_password,
        use_cookie=False
    )
    if loggged_in_succesfully:
        return True
    return False


def create_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'post_url',
        type=str,
        help='Instagram post url to count.')
    return parser


if __name__ == '__main__':

    argument_parser = create_argument_parser()
    args = argument_parser.parse_args()
    post_url = args.post_url

    instagram_login = os.getenv('instagram_login')
    instagram_password = os.getenv('instagram_password')

    if not authenticate_with_bot(instagram_login, instagram_password):
        sys.exit('''
        Cannot log-in with provided credentials.
        Check instagram_login and instagram_password env variables.
        ''')

    post_id = get_post_id(post_url)
    if not post_id:
        sys.exit('''
        Wrong instagram post url
        ''')

    competitors = get_all_allowed_competitors(instagram_login, post_id)

    print('Allowed competitors: ')
    pprint.pprint(competitors)
