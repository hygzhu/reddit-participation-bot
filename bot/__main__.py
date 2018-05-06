import argparse
import bot


def main():
    parser = argparse.ArgumentParser(description="Reddit bot")
    parser.add_argument('--comments', metavar='Subreddit', type=str, help='Collect Comments from a subreddit')
    parser.add_argument('--submissions', metavar='Subreddit', type=str, help='Collect Submissions from a subreddit')
    parser.add_argument('--replycomment', metavar='Subreddit', type=str, help='Reply to comments on a subreddit')
    parser.add_argument('--replysubmission', metavar='Subreddit', type=str, help='Reply to submissions on a subreddit')
    args = parser.parse_args()
    try:
        reddit = bot.bot_login()
        if(args.comments):
            bot.collectComments(reddit, args.comments)
        elif(args.submissions):
            bot.collectSubmissions(reddit, args.submissions)
        elif(args.replycomment):
            bot.replyToComments(reddit, args.replycomment)
        elif(args.replysubmission):
            bot.replyToSubmission(reddit, args.replysubmission)
    except AttributeError:
        parser.print_help()


if __name__ == "__main__":
    main()