import praw
import config
import collections
import time
import datetime
import pyrebase
import json
import re
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
    print("Bot logged in properly")
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

        #Updates comment data if it does not exist or if the score changed in past 
        if(date not in daily_comments):
            daily_comments[date] = db.child("comments").child("{dt.tm_mon}-{dt.tm_mday}-{dt.tm_year}".format(dt = time.gmtime(comment.created_utc))).get().val()
            #print("Getting all comments for {}".format(date))

        if(daily_comments[date] != None and any((x["permalink"] == str(comment.permalink) and (x["score"] == str(comment.score))) for x in daily_comments[date].values())):
            #print("Comment {} : {} already exists in DB and does not need to be updated".format(index,str(comment.id)))
            ignored_count += 1
        else:
            if(daily_comments[date] != None and any(x["permalink"] == str(comment.permalink) and x["score"] != str(comment.score) for x in daily_comments[date].values())):
                #print("Updating score for comment {} : {}".format(index,str(comment.id)))
                db.child("comments").child("{}-{}-{}".format(time_posted.tm_mon, time_posted.tm_mday, time_posted.tm_year)).child(str(comment.name)).update(data)
                updated_count += 1
            else:
                #print("Adding comment {} : {}".format(index,str(comment.id)))
                db.child("comments").child("{}-{}-{}".format(time_posted.tm_mon, time_posted.tm_mday, time_posted.tm_year)).child(str(comment.name)).set(data)
                added_count += 1

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
    db = firebase.database()
    daily_submissions= dict()
    
    ignored_count = 0
    added_count = 0
    updated_count = 0

    count = 0
    print("RUNNING COLLECT SUBMISSIONS AT TIME " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    for submission in reddit.subreddit('uwaterloo').new(limit=None):
        count += 1
        time_posted = time.gmtime(submission.created_utc)
        date = (time_posted.tm_mday, time_posted.tm_mon, time_posted.tm_year)

        data = {
            "subreddit": str(submission.subreddit),
            "author": str(submission.author),
            "score": str(submission.score),
            "gilded": str(submission.gilded),
            "permalink": str(submission.permalink),
            "created_utc": str(submission.created_utc),
            "num_comments": str(submission.num_comments),
            "title": str(submission.title),
            "self_text": str(submission.selftext),
            "id": str(submission.id)
        }

        #Updates submissioon data if it does not exist or if the score changed in past 
        if(date not in daily_submissions):
            daily_submissions[date] = db.child("submissions").child("{dt.tm_mon}-{dt.tm_mday}-{dt.tm_year}".format(dt = time.gmtime(submission.created_utc))).get().val()

        if(daily_submissions[date] != None and any((x["permalink"] == str(submission.permalink) and (x["score"] == str(submission.score)) and x["num_comments"] == str(submission.num_comments)) for x in daily_submissions[date].values())):
            ignored_count += 1
            #print("Ignored")
        else:
            if(daily_submissions[date] != None and any((x["permalink"] == str(submission.permalink) and (x["score"] != str(submission.score) or x["num_comments"] != str(submission.num_comments))) for x in daily_submissions[date].values())):
                db.child("submissions").child("{}-{}-{}".format(time_posted.tm_mon, time_posted.tm_mday, time_posted.tm_year)).child(str(submission.name)).update(data)
                updated_count += 1
                #print("Updated")
            else:
                db.child("submissions").child("{}-{}-{}".format(time_posted.tm_mon, time_posted.tm_mday, time_posted.tm_year)).child(str(submission.name)).set(data)
                added_count += 1
                #print("Added")

    print("Added {}, Ignored {}, Updated {}".format(added_count, ignored_count, updated_count))
    print("COMPLETED COLLECT SUBMISSIONS AT TIME " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    return
    

def getStats(reddit):
    """
    Fetches comment data for the past 7 days starting the day prior
    """
    print("Getting stats from DB")
    user_comment_count = dict()
    user_total_comment_karma = dict()
    user_comment_ratio = dict()

    user_submission_count = dict()
    user_total_submission_karma = dict()
    user_submission_ratio = dict()

    total_comments = 0
    total_comment_karma = 0
    total_submissions = 0
    total_submission_karma = 0

    all_comment_text = []
    all_submission_text = []
    all_submission_titles = []

    db = firebase.database()
    dt = datetime.datetime.fromtimestamp(time.mktime(time.gmtime()))
    #print(date)
    for i in range(1,8):
        new_dt = dt - datetime.timedelta(days=i)
        #print("{}-{}-{}".format(new_dt.month, new_dt.day, new_dt.year))
        new_dt = "{}-{}-{}".format(new_dt.month, new_dt.day, new_dt.year)
        
        #fetch daily submissions
        daily_submissions = db.child("submissions").child(new_dt).get().val()
        if daily_submissions == None: 
            #print("No Submissions for {}".format(new_dt))
            continue
        daily_submissions = daily_submissions.values()
        for submission in daily_submissions:
            total_submissions += 1
            total_submission_karma += int(submission['score'])
            all_submission_text.append(str(submission['self_text']))
            all_submission_titles.append(str(submission['title']))
            if(str(submission['author']) in user_submission_count): 
                user_submission_count[str(submission['author'])] += 1
                user_total_submission_karma[str(submission['author'])] += int(submission['score'])
            else:
                user_submission_count[str(submission['author'])] = 1
                user_total_submission_karma[str(submission['author'])] = int(submission['score'])

        for key in user_submission_count:
            user_submission_ratio[key] = user_total_submission_karma[key]/user_submission_count[key]
        
        #fetch daily comments
        daily_comments = db.child("comments").child(new_dt).get().val()
        if daily_comments == None: 
            #print("No Comments for {}".format(new_dt))
            continue
        daily_comments = daily_comments.values()
        for comment in daily_comments:
            total_comments += 1
            total_comment_karma += int(comment['score'])
            all_comment_text.append(str(comment['body']))
            if(str(comment['author']) in user_comment_count): 
                user_comment_count[str(comment['author'])] += 1
                user_total_comment_karma[str(comment['author'])] += int(comment['score'])
            else:
                user_comment_count[str(comment['author'])] = 1
                user_total_comment_karma[str(comment['author'])] = int(comment['score'])

        for key in user_comment_count:
            user_comment_ratio[key] = user_total_comment_karma[key]/user_comment_count[key]

    words = dict()
    for text in all_comment_text + all_submission_text + all_submission_titles:
        for word in text.split(' '):
            if word in words:
                words[word] += 1
            else: 
                words[word] = 1
    

    return strings.UWATERLOO_FRIDAY_POST.format(
    sub = "uwaterloo", 
    start = "{new_dt.month}-{new_dt.day}-{new_dt.year}".format(new_dt = dt - datetime.timedelta(days=8)), 
    end = "{new_dt.month}-{new_dt.day}-{new_dt.year}".format(new_dt = dt - datetime.timedelta(days=1)), 
    total_submissions = total_submissions, total_submission_karma = total_submission_karma, total_unique_submitters = len(user_submission_count), 
    total_comments = total_comments, total_comment_karma= total_comment_karma, total_unique_commentors = len(user_comment_count),
    s_most = collections.Counter(user_submission_count).most_common(5), s_karma = collections.Counter(user_total_submission_karma).most_common(5), 
    s_highest =  collections.Counter(user_submission_ratio).most_common(5),
    c_most = collections.Counter(user_comment_count).most_common(5), c_karma = collections.Counter(user_total_comment_karma).most_common(5),
    c_highest = collections.Counter(user_comment_ratio).most_common(5),
    goose_count = words['goose'], my_dude_count = words['dude'], facebook_count = words['facebook'],
    contact ="https://www.reddit.com/message/compose/?to=user-activity", source= "https://github.com/hygzhu/reddit-participation-bot", website="")


def replyToComments(reddit):
    """
    Replies to comments requesting statistics
    """
    replyText = getStats(reddit)

    #Takes newest submissions first
    all_comments = reddit.subreddit('uwaterloobots').comments(limit=None)
    for comment in all_comments:
        if(re.match(r'.*<get-stats>.*',str(comment.body))):
            print("Found a comment!")
            #To get replies, we need to fetch the entire submission
            comment.refresh()
            if(any(str(reply.author) == 'user-activity' for reply in comment.replies)):
                print('Already replied to this command')
            else:
                print('Replying to new command')
                comment.reply(replyText)
    