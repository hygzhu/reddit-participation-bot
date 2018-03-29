import praw
import config
import collections
import time
import pyrebase
import json

firebase = pyrebase.initialize_app(config.firebase_config)

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
    Should be ran at least once every 12 hours to collect all comment data.
    Note: reddit caps comment collection at 1000, so we will need to run this at intervals depending on how busy the subreddit is
    """
    db = firebase.database()
    index = 1
    ignored_count = 0
    added_count = 0
    print("THE TIME IS " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    
    #print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment.created_utc)))
    #Fetch data for comments in the current day
    print("{dt.tm_mon}-{dt.tm_mday}-{dt.tm_year}".format(dt = time.localtime()))
    daily_comments = dict()

    all_comments = reddit.subreddit('uwaterloo').comments(limit=None)
    for comment in all_comments:
        #print(comment.body)
        time_posted = time.localtime(comment.created_utc)
        date = (time_posted.tm_mday, time_posted.tm_mon, time_posted.tm_year)

        data = {
            "link_url": str(comment.link_url),
            "edited": str(comment.edited),
            "gilded": str(comment.gilded),
            "author": str(comment.author),
            "body": str(comment.body),
            "score": str(comment.score),
            "ups": str(comment.ups),
            "downs": str(comment.downs),
            "is_submitter": str(comment.is_submitter),
            "permalink": str(comment.permalink),
            "created_utc": str(comment.created_utc),
            "id": str(comment.id)
        }

        #Check if the comment was already added in, else fetch total comments for the day
        print(date)
        if(date in daily_comments):
            if(daily_comments[date] != None and any(x["permalink"] == str(comment.permalink) for x in daily_comments[date].values())):
                print("Comment {} already exists in DB".format(index))
                ignored_count += 1
            else:
                print("Adding comment {} to DB".format(index))
                db.child("{}-{}-{}".format(time_posted.tm_mon, time_posted.tm_mday, time_posted.tm_year)).push(data)
                added_count += 1
        else:
            daily_comments[date] = db.child("{dt.tm_mon}-{dt.tm_mday}-{dt.tm_year}".format(dt = time.localtime(comment.created_utc))).get().val()
            print("Getting all comments for {}".format(date))


        #db.child("{}-{}-{}".format(time_posted.tm_mon, time_posted.tm_mday, time_posted.tm_year)).push(data)
        #print("Added Comment {}".format(index))
        index +=1

        
    print("Added {} and ignored {}".format(added_count, ignored_count))

    

def getStats(reddit):
    """
    Fetches comment data for the past day from firebase
    """
    print("Getting stats from DB")
    users = dict()
    upvotes = dict()
    ratio = dict()
    daily_posts = dict()

    total = 0
    db = firebase.database()
    daily_comments = db.child("{dt.tm_mon}-{dt.tm_mday}-{dt.tm_year}".format(dt = time.localtime())).get().val().values()
    for comment in daily_comments:
        time_posted = time.localtime(int(float(comment['created_utc'])))
        date = (time_posted.tm_mday, time_posted.tm_mon, time_posted.tm_year)

        total += 1

        if(date in daily_posts):
            daily_posts[date] += 1
        else:
            daily_posts[date] = 1

        if(str(comment['author']) in users): 
            users[str(comment['author'])] += 1
            upvotes[str(comment['author'])] += int(comment['score'])
        else:
            users[str(comment['author'])] = 1
            upvotes[str(comment['author'])] = int(comment['score'])

    for key in users:
        ratio[key] = upvotes[key]/users[key]
    print(collections.Counter(users).most_common(10)) #top 10 most commented
    print(collections.Counter(upvotes).most_common(10)) #top ten most upvotes
    print(collections.Counter(ratio).most_common(10)) #top ten best averages per post
    print(collections.Counter(ratio).most_common()[-10:]) #bottom ten average per post


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
    #getStats(reddit)

if __name__ == "__main__":
    main()