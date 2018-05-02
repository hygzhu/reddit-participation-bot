import argparse
import bot


def main():
    parser = argparse.ArgumentParser(description="Updates the DB with comments")
    parser.add_argument('action', type=str, nargs=None, help='What the bot should do')
    parser.set_defaults(function=runAction)

    args = parser.parse_args()
    try:
        args.function(args)
    except AttributeError:
        parser.print_help()

def runAction(args):
    """
    Does the specifed action
    """
    print(args.action)
    reddit = bot.bot_login()
    if(args.action == 'comments'):
        bot.collectComments(reddit)
    elif(args.action == 'submissions'):
        bot.collectSubmissions(reddit)
    elif(args.action == 'replycomment'):
        bot.replyToComments(reddit)
    elif(args.action == 'replysubmission'):
        bot.replyToSubmission(reddit)

if __name__ == "__main__":
    main()