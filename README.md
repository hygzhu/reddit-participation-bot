# reddit-participation-bot
This is a script that is ran on a Heroku Scheduler at certain time intervals.
It collects the past ~1000 submissions on /r/uwaterloo once a day.
It collects the past ~1000 comments on /r/uwaterloo once an hour.
All data is stored on a Firebase Realtime DB which is accessed using Pyrebase.

Current Usage
```
# collects the past ~1000 comments and adds to the db
python bot comments

# collects the past ~1000 submissions and adds to the db
python bot submissions

# Replies to the most recent submission titled "Free Talk Friday"
python bot reply 
```
