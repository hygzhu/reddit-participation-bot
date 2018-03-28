import praw
import config
import collections
import time
import pyrebase
import json

firebase = pyrebase.initialize_app(config.firebase_config)

users = dict()
upvotes = dict()
ratio = dict()

daily_posts = dict()

def bot_login():
    """
    Allows the bot to login
    Returns the reddit class
    """
    reddit = praw.Reddit(username = config.username, 
                password= config.password, 
                client_id = config.client_id, 
                client_secret = config.client_secret,
                user_agent = "User participation bot v0.1")
    return reddit

def collectComments(reddit):
    """
    Collects all comments within a certain time frame.
    Note: reddit caps comment collection at 1000, so we will need to run this at intervals depending on how busy the subreddit is
    """
    db = firebase.database()

    total = 0
    #print("THE TIME IS " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    for comment in reddit.subreddit('uwaterloo').comments(limit=None):
        #adds the post to a dict
        #print(comment.body)
        #print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment.created_utc)))

        time_posted = time.localtime(comment.created_utc)
        date = (time_posted.tm_mday, time_posted.tm_mon, time_posted.tm_year)
        if(date in daily_posts):
            daily_posts[date] += 1
        else:
            daily_posts[date] = 1

        total += 1
        if(str(comment.author) in users): 
            users[str(comment.author)] += 1
            upvotes[str(comment.author)] += comment.score
        else:
            users[str(comment.author)] = 1
            upvotes[str(comment.author)] = comment.score
        data = {
            "link_url": str(comment.link_url),
            "edited": str(comment.edited),
            "link_id": str(comment.link_id),
            "link_author": str(comment.link_author),
            "gilded": str(comment.gilded),
            "author": str(comment.author),
            "num_comments": str(comment.num_comments),
            "body": str(comment.body),
            "score": str(comment.score),
            "ups": str(comment.ups),
            "downs": str(comment.downs),
            "link_title": str(comment.link_title),
            "is_submitter": str(comment.is_submitter),
            "name": str(comment.name),
            "permalink": str(comment.permalink),
            "created_utc": str(comment.created_utc)
        }
        db.child("comments").push(data)

    for key in users:
        ratio[key] = upvotes[key]/users[key]
    print(daily_posts)

    #print(collections.Counter(users).most_common(10)) #top 10 most commented
    #print(collections.Counter(upvotes).most_common(10)) #top ten most upvotes
    #print(collections.Counter(ratio).most_common(10)) #top ten best averages per post
    #print(collections.Counter(ratio).most_common()[-10:]) #bottom ten average per post


def replyToThread(reddit):
    """
    Replies to the thread of the week with statistics
    """
    subreddit = reddit.subreddit('uwaterloobots')
    for submission in subreddit.stream.submissions():
        if(submission.title == "Free Talk Friday"):
            print("Created at {}".format(submission.created))
            replyText = "Found a free talk friday"
            submission.reply(replyText)


    



def main():
    reddit = bot_login()
    collectComments(reddit)
    #replyToThread(reddit)

if __name__ == "__main__":
    main()