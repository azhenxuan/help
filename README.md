# Project HELP

## Status Update for Milestone 3

In the past month, we've been able to test the application on many of our 
friends, and made significant updates based on their feedback. The application
is available to view [here](http://nus-help.herokuapp.com), and our milestone 3 
video is [here](https://www.youtube.com/watch?v=26umT37VlAg). Older features 
demonstrated in the milestone 2 video were not demonstrated again. To view those,
go [here](https://youtu.be/3HfA9drTI4k). (Note that some new features did not 
appear in any of the videos as they were pushed to production only after the 
video was completed, and there wasn't sufficient time to include them. This
includes the 'Invite Link' and 'Calendar View' features.)

### User Feedback (Form we sent out [here](docs/Usability Testing.pdf))

User testing was really helpful not only in identifying bugs in our app, but
also helped us focus on features that were important to the users. We are 
also extremely grateful to Professor Kan Min-Yen for his help with testing our
application. 

One major bugfix was only discovered when we realised that some students were
unable to view their modules through our app. Through our error logs, we 
realised that the CFG module caused the thread to throw an error due to its 
excessively long name. We confirmed that only students who had taken the CFG
module had this issue, and were finally able to fix the issue, and confirm the
fix with the help of our testers.

We also received a lot of suggestions, which can categorized into:

1. Aesthetics - Some users felt that the app could be redesigned and made more
unique (it had a distinctly Bootstrap feel to it)

2. Functionality (for future sprints)
	- Manually add modules
	- Calendar editing similar to Google Cal 
	- Reporting system for errant users
	- Better location selection
	- Mobile app to complement the website

In general, the consensus was that the testers were willing to use the app, but
only predicated on support from the teaching staff. Due to time constraints, 
however, not all the above features could be incorporated into the application.

### New features

1. **Consult Details page**: Every consult now has it's own page, where its 
creators can manage the consult, see who's signed up etc, and students can 
see all the details about the consult.

2. **Comments section**: Students who have questions about the consult can
now post questions after joining the consult! (On the consults details page)

3. **Invite link**: We generate an invite link for each consult so users can
invite their friends to join them for their consults. TAs can also use this 
feature to get their students to attend their consults. (Below the comments
section)

4. **Module Filtering**: On the Get-Help page, students can filter through 
their modules based on module code.

5. **Calendar View**: As suggested by our testers, we started work on a 
calendar view. Users can now view their timetable in calendar format. We also
plan to allow them to edit their consults through the calendar interface in the
future. (My Calendar link in the navbar)

### Unit Testing

While we don't have complete coverage or end-to-end tests, we were able to
make some headway by writing automated tests for some sections of our code.
We hope to improve on this by writing more tests after this milestone. 

```
Coverage Summary:
Name                              Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------------------
app\__init__.py                      25      2      2      1    89%
app\main\__init__.py                  3      0      0      0   100%
app\main\api.py                      77     27     28      8    55%
app\main\errors.py                   10      1      0      0    90%
app\main\forms.py                    28      9      4      0    59%
app\main\views.py                   197     98     72     13    45%
app\models.py                        84     18      6      0    73%
-------------------------------------------------------------------
TOTAL                               424    155    112     22    56%
```

-- END OF MILESTONE 3 UPDATE --

## Status Update for Milestone 2

The progress of Project Help has been in-line with expectations. A demo of the
application (note that this is still a work-in-progress) is available [here](http://nus-help.herokuapp.com).
We have also prepared a [short video](https://youtu.be/3HfA9drTI4k) demonstrating 
the features available. As can be seen,  we have implemented the basic features, 
including IVLE login and simple adding and joining of modules is available. 

For the next milestone, we plan to work on two main areas, maintainability and 
usability.

### Maintability
Our current app and its code base is still small, and we were able to get this
far without writing a whole bunch of tests. However, to move beyond this point,
we feel that we would need to include a comprehensive set of tests to ensure we 
don't break our app while trying to improve it.

### Usability
During the past month, we have been overly focused on the technical aspects of 
building the app. At some point, we lost sight of users' needs. To fix this, we
plan to enlist some of our friends to test the app. We will then gather their
feedback on work on the problems they've identified, and perhaps include some
features they feel would be critical to the application's success.

## Introduction
A web-based help-session scheduler.

We are Team HELP, which comprises two BZA students, Zhen Xuan and Ken.
Our current target is Project Gemini, the intermediate level of achievement. The
main inspiration for this project was our daily struggle with schoolwork, and 
our inability to get timely help. 

Our solution is a web application where students can signal their need for 
assistance, before they fall deeper into CAP hell. Upon seeing the demand for
their services, TAs and Profs will (hopefully) start opening up time slots that
students can ballot for.  

## Team HELP
- Ang Zhen Xuan
- Ken Oung Yong Quan

## Scope of Project
### Target Groups
**Students:** Students in NUS who need extra face-time with TAs and Profs.

**Teaching Staff:** 
- TAs and Profs who want a platform to reach out to students who need more
help
- TAs and Profs who want a platform to coordinate help sessions

### Future Plans
Could see the scope of operations being expanded into other learning institutes
OR into corporate environments where employees want to schedule face-time with
higher-ups?

## Features
### Completed
1. (Student) Register for GetHelp sessions
2. (Users)   Set time slots for ProvideHelp sessions
3. (Student) Able to see schedule for GetHelp & ProvideHelp sessions for 
him/herself
4. (Student) Automatically display mods taken this sem 
5. (Student) Automatically filters irrelevant GetHelp sessions which provides
a cleaner view for users
6. (Users) Consult details page to manage/view details
7. (Users) Add comments/queries to consults
8. (Users) Invite people to join consults using invite link

### Next Sprint (Subject to change based on user feedback)
1. (Users) Manually add modules
2. (Users) Reporting system for errant users
3. (Teacher) Better location selection

### KIV
1. (Users) Mobile app to complement the website
2. (Users) Calendar views similar to Google Cal

## User Stories
1. As a **Student**, I want to *register for help sessions*, so I can 
*arrange for consults easily*.
2. As a **User**, I want to *place help sessions up for registration*, so I can 
*provide help to students/peers who need it urgently*.
3. As a **Student**, I want to *have an easy schedule to refer to*, so I can
*save time checking back on my registered consults*.
4. As a **Student**, I want to *be able to see all the mods I'm taking* so I 
can *get started quickly without much setup needed*.
5. As a **User**, I want to *be able to blacklist students*, so I *won't have
to waste my time*.
6. As a **Student**, I want to *provide feedback on help sessions*, so I can 
*get better help from Profs and TAs next time*.

## Project Log
[Link to Google Sheets](https://docs.google.com/spreadsheets/d/1irWFqA-WFoaXJmSb0RhwxuIm9TfVC-xpZLDoqmZmDJ4/edit?usp=sharing)

## Kickoff Video
[Link to Milestone 2 Video](https://youtu.be/3HfA9drTI4k)
