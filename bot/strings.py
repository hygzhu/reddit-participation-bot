UWATERLOO_FRIDAY_POST = """# **/r/{sub} Weekly Statistics Bot**
## Week **{start}** To **{end}**
&nbsp;

 | Overall Statistics
:--|:--
**Total Submissions**| {total_submissions} submissions
**Total Submission Karma**| {total_submission_karma} total karma
**Total Unique Submitters**| {total_unique_submitters} Users
**Total Comments**| {total_comments} comments 
**Total Comment Karma**| {total_comment_karma} total karma
**Total Unique Commentors**| {total_unique_commentors} Users

&nbsp;

 | Submission Statistics
:--|:--
**Most Submissions**| /u/{s_most[0][0]}1 with {s_most[0][1]} Submissions
**Most Submission Karma**| /u/{s_karma[0][0]}1 with {s_karma[0][1]} total Submission karma
**Highest Submission karma**| /u/{s_highest[0][0]}1 with {s_highest[0][1]} average karma per Submission

&nbsp;

 | Comment Statistics
:--|:--
**Most Comments**| /u/{c_most[0][0]}1 with {c_most[0][1]} comments 
**Most Comment Karma**| /u/{c_karma[0][0]}1 with {c_karma[0][1]} total comment karma
**Highest Average karma**| /u/{c_highest[0][0]}1 with {c_highest[0][1]} average karma per comment

&nbsp;

 | Misc Statistics
:--|:--
**Mr. Goose Thanked**| Mr. Goose thanked {goose_count} times 
**Rocks on my dude** | My dude rocked {my_dude_count} times
**Working at Facebook** | {facebook_count} people in 4A (menlo park btw) 

---
[Contact]({contact}) | 
[Source Code]({source}) |
[Detailed Breakdown (Coming soon)]({website})"""