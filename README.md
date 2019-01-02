# Closer - Randy Yan
Video: https://www.youtube.com/watch?v=7NYudiI6lyM&feature=youtu.be

## Getting started
Closer is a Flask web application which can be tested by executing `$ flask run` in the root directory. To get started, one can register for an account in the upper right-hand corner. Given the username is not already in use, one can then use their newly made login-credentials to start using the website.

## Linking
As a new user, you do not have a linked account with which to interact, so you will first want to find out the username of the person you are trying to use the website with (they must make an account as well). You can then send them a link request by inputting their username where prompted on the left half of the screen, which will then display a request on their end. If logged into their account at this moment, one would see an incoming request on the right half of the screen, for which there is a button to accept the request.

Once two users are linked, they now have access to two main features: breaks and trips, which can both be accessed from the navbar, or through links that will prompt you when you have no inputted breaks or trips (which will be the case when you first sign up).

## Breaks
For breaks, one will see a form filled with the breaks a user has already submitted (blank at first because there are none). One can then input the date ranges for which they are free. One can add more inputs for ranges with the '+' circle button next to submit or press the '-' circle button next to any range inputs to remove it. After updating your break schedule, you will see it on the homepage under the 'Breaks' header on the left column. The middle column will display your linked user's breaks, and the rightmost column will display any overlaps which exist between your two break schedules.

## Trips
For trips, one will see an entry form for which they can input the start and end date/time of a trip which they would like to share. After inputting a trip, one will see it displayed in a table under the 'Upcoming Trips' header on the homepage where each row will display who's trip it is, the start and end dates/times, as well as a countdown towards the beginning or end of that trip, depending on if the trip has started or is currently ongoing. There will also be a green button for each trip which will display a larger timer screen for that trip. (Note: trips which have already finished will be automatically removed from your account.)

## And last but not least...
Other features include the ability to change your password, located on the top right of the navbar, in which case you will be required to input your current password and then provide your new (different-than-before) password twice. One can log out by pressing the log out button in the top right of the navbar. The top right of the navbar also displays the username of the account which you are currently on.