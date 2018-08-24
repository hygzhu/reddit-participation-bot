# reddit-participation-bot
This is a script that is ran on a Heroku Scheduler at certain time intervals.
It collects the past ~1000 submissions on /r/uwaterloo once a day.
It collects the past ~1000 comments on /r/uwaterloo once an hour.
All data is stored on a Firebase Realtime DB which is accessed using Pyrebase.

Current Usage
```
python bot [flags]

non-optional arguments:
  -h, --help            show this help message and exit
  --comments Subreddit  Collect Comments from a subreddit
  --submissions Subreddit
                        Collect Submissions from a subreddit
  --replycomment Subreddit
                        Reply to comments on a subreddit
  --replysubmission Subreddit
                        Reply to submissions on a subreddit

```

When collecting comments or submissions, the script will collect the most recent 1000.
