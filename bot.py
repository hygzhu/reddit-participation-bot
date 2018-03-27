import praw
import config
import collections

users = dict()
upvotes = dict()
ratio = dict()

def bot_login():
    reddit = praw.Reddit(username = config.username, 
                password= config.password, 
                client_id = config.client_id, 
                client_secret = config.client_secret,
                user_agent = "User participation bot v0.1")
    return reddit

def run_bot(reddit):
    total = 0
    for comment in reddit.subreddit('uwaterloo').comments(limit=None):
        #adds the post to a dict
        total += 1
        if(str(comment.author) in users): 
            users[str(comment.author)] += 1
            upvotes[str(comment.author)] += comment.ups
        else:
            users[str(comment.author)] = 1
            upvotes[str(comment.author)] = comment.ups

    for key in users:
        ratio[key] = upvotes[key]/users[key]

    print(collections.Counter(users).most_common(10)) #top 10 most commented
    print(collections.Counter(upvotes).most_common(10)) #top ten most upvotes
    print(collections.Counter(ratio).most_common(10)) #top ten best averages per post
    print(collections.Counter(ratio).most_common()[-10:]) #bottom ten average per post



def main():
    run_bot(bot_login())

if __name__ == "__main__":
    main()