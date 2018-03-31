import praw
import config
import collections
import time
import datetime
import pyrebase
import json
import strings

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
    Collect data for as many comments as possible
    Should be ran at least once every hour to collect all comment data.
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


def collectSubmissions(reddit):
    """
    Collect data for as many submissions as possible
    Collects up to 1000 past submissions
    Should be ran at least once every day
    """
    count = 0
    for submission in reddit.subreddit('uwaterloo').new(limit=None):
        count += 1
        print(submission.__dict__)
    return
    

def getStats(reddit):
    """
    Fetches comment data for the past 7 days starting the day prior
    """
    print("Getting stats from DB")
    user_comment_count = dict()
    user_total_karma = dict()
    user_comment_ratio = dict()

    total_comments = 0

    db = firebase.database()
    dt = datetime.datetime.fromtimestamp(time.mktime(time.gmtime()))
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
            if(str(comment['author']) in user_comment_count): 
                user_comment_count[str(comment['author'])] += 1
                user_total_karma[str(comment['author'])] += int(comment['score'])
            else:
                user_comment_count[str(comment['author'])] = 1
                user_total_karma[str(comment['author'])] = int(comment['score'])

        for key in user_comment_count:
            user_comment_ratio[key] = user_total_karma[key]/user_comment_count[key]

    return strings.UWATERLOO_FRIDAY_POST.format(
    sub = "uwaterloo", 
    start = "{new_dt.month}-{new_dt.day}-{new_dt.year}".format(new_dt = dt - datetime.timedelta(days=8)), 
    end = "{new_dt.month}-{new_dt.day}-{new_dt.year}".format(new_dt = dt - datetime.timedelta(days=1)), 
    total_submissions = 0, total_submission_karma = 0, total_unique_submitters = 0, total_comments = total_comments, total_comment_karma= 0, total_unique_commentors = 0,
    s_most = [(0,0)], s_karma= [(0,0)], s_highest = [(0,0)], s_lowest = [(0,0)], top_submission_user = "", top_submission_karma = 0, top_submission_link = "",
    c_most = collections.Counter(user_comment_count).most_common(5), c_karma = collections.Counter(user_total_karma).most_common(5),
    c_highest = collections.Counter(user_comment_ratio).most_common(5), c_lowest = collections.Counter(user_comment_ratio).most_common()[-5:][::-1],
    top_comment_user = "", top_comment_karma = 0, top_comment_link = "", 
    common_words = "", goose_count = "", my_dude_count = "", facebook_count = "",
    contact ="https://www.reddit.com/message/compose/?to=user-activity", source= "https://github.com/hygzhu/reddit-participation-bot", website="")


def replyToThread(reddit):
    """
    Replies to the thread of the week with statistics
    """
    subreddit = reddit.subreddit('uwaterloobots')
    #Takes newest submissions first
    for submission in subreddit.stream.submissions():
        if(submission.title == "Free Talk Friday"):
            print("Created at {}".format(submission.created))
            replyText = getStats(reddit)
            print(replyText)
            #submission.reply(replyText)
            return


def main():
    reddit = bot_login()
    #collectComments(reddit)
    collectSubmissions(reddit)
    #replyToThread(reddit)
    #getStats(reddit)

if __name__ == "__main__":
    main()