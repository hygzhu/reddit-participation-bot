import praw
import config
import collections
import time
import datetime
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
    updated_count = 0
    print("RUNNING COLLECT COMMENTS AT TIME " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    
    #print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(comment.created_utc)))
    #Fetch data for comments in the current day
    #print("{dt.tm_mon}-{dt.tm_mday}-{dt.tm_year}".format(dt = time.gmtime()))
    daily_comments = dict()

    all_comments = reddit.subreddit('uwaterloo').comments(limit=None)
    for comment in all_comments:
        #print(comment.body)
        time_posted = time.gmtime(comment.created_utc)
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
        #print(date)
        if(date in daily_comments):
            if(daily_comments[date] != None and any((x["permalink"] == str(comment.permalink) and (x["score"] == str(comment.score))) for x in daily_comments[date].values())):
                #print("Comment {} : {} already exists in DB and does not need to be updated".format(index,str(comment.id)))
                ignored_count += 1
            else:
                if(daily_comments[date] != None and any(x["score"] != str(comment.score) for x in daily_comments[date].values())):
                    #print("Updating score for comment {} : {}".format(index,str(comment.id)))
                    db.child("comments").child("{}-{}-{}".format(time_posted.tm_mon, time_posted.tm_mday, time_posted.tm_year)).child(str(comment.name)).update(data)
                    updated_count += 1
                else:
                    #print("Adding comment {} : {}".format(index,str(comment.id)))
                    db.child("comments").child("{}-{}-{}".format(time_posted.tm_mon, time_posted.tm_mday, time_posted.tm_year)).child(str(comment.name)).set(data)
                    added_count += 1
        else:
            daily_comments[date] = db.child("comments").child("{dt.tm_mon}-{dt.tm_mday}-{dt.tm_year}".format(dt = time.gmtime(comment.created_utc))).get().val()
            #print("Getting all comments for {}".format(date))


        #db.child("{}-{}-{}".format(time_posted.tm_mon, time_posted.tm_mday, time_posted.tm_year)).push(data)
        #print("Added Comment {}".format(index))
        index +=1

    print("Added {}, Ignored {}, Updated {}".format(added_count, ignored_count, updated_count))
    print("COMPLETED COLLECT COMMENTS AT TIME " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))


def getStats(reddit):
    """
    Fetches comment data for the past 7 days starting the day prior
    """
    print("Getting stats from DB")
    users = dict()
    upvotes = dict()
    ratio = dict()
    daily_posts = dict()

    total_comments = 0
    db = firebase.database()
    dt = datetime.datetime.fromtimestamp(time.mktime(time.gmtime()))
    date = "{}-{}-{}".format(dt.month, dt.day, dt.year)
    #print(date)
    for i in range(1,8):
        new_dt = dt - datetime.timedelta(days=i)
        print("{}-{}-{}".format(new_dt.month, new_dt.day, new_dt.year))
        new_dt = "{}-{}-{}".format(new_dt.month, new_dt.day, new_dt.year)
        #fetch daily comments
        daily_comments = db.child("comments").child(new_dt).get().val()
        if daily_comments == None: 
            print("No Comments for {}".format(new_dt))
            continue
        daily_comments = daily_comments.values()
        for comment in daily_comments:
            total_comments += 1
            time_posted = time.gmtime(int(float(comment['created_utc'])))
            date = (time_posted.tm_mday, time_posted.tm_mon, time_posted.tm_year)

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
        """
        print("Comment Stats for {}".format(new_dt))
        print("-----------Top 5 most commented-----------")
        for x in collections.Counter(users).most_common(5):
            print("{}, {} comments".format(x[0], x[1]))
        print("-----------Top 5 most culmulative upvotes-----------")
        for x in collections.Counter(upvotes).most_common(5):
            print("{}, {} Upvotes".format(x[0], x[1]))
        print("-----------Top 5 highest average score-----------")
        for x in collections.Counter(ratio).most_common(5):
            print("{}, {} Average score in {} comments".format(x[0], x[1], users[x[0]]))
        print("-----------Top 5 lowest average score-----------")
        for x in collections.Counter(ratio).most_common()[-5:]:
            print("{}, {} Average score in {} comments".format(x[0], x[1], users[x[0]]))
        """
    return "Comment str"


def replyToThread(reddit):
    """
    Replies to the thread of the week with statistics
    """
    subreddit = reddit.subreddit('uwaterloobots')
    for submission in subreddit.stream.submissions():
        if(submission.title == "Free Talk Friday"):
            print("Created at {}".format(submission.created))
            replyText = getStats(reddit)
            submission.reply(replyText)
            return


def main():
    reddit = bot_login()
    #collectComments(reddit)
    #replyToThread(reddit)
    getStats(reddit)

if __name__ == "__main__":
    main()