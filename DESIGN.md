# Design (Closer - Randy Yan)

## Flask
I built Closer using the bare framework of the CS50 Finance Pset. It still maintains the original Bootstrap navbar as well as the login and register features.

## `closer.db`
I designed the database of this project around 4 main tables: `users`, `trips`, `break`, and `requests` which store what you think they would.

#### `users`
The `users` table of `closer.db` is almost an exact copy of the one used in CS50 Finance: It stores a user_id, username, password_hash, as well as the id of their linked user (which may be `NULL`).
#### `trips`
The `trips` table stores every trip submitted by every user in the form of rows consisting of an id, start datetime, and end datetime.
#### `break`
Similar to `trips`, the `break` table stores every break range submitted by users in the form of rows consisting of an id, start date, and end date.
#### `requests`
`requests` stores the linking requests sent by users as rows consisting of a from id, a to id, and a datetime of sending.

## Breaks
The 'breaks' part of this project is built on `break.html`, and the `/breaks` route of `application.py`. The breaks stored in the `break` table are reused and edited everytime a user submits their schedule through `break.html`. `break.html` will load on every `GET` request with what the user has already submitted in the past and then support adding or removing fields to create a new break schedule. On `POST` requests, all old breaks are removed from the `break` table and the newly inputted ones are added.
## Trips
The 'trips' part of this project consists of `trips.html`, and `/trips` of `application.py`. Each time a user can submit one trip through `POST` method on `/trips` which will add the trip under their id to the `trips` table.
## Home
The home screen has two templates: `index.html` for unlinked users, and `linked.html` for linked users and both are rendered by the `/` route.

`index.html` for linked users displays an input which allows them to send a linking request to the inputted username, which will send a `POST` request to `/linkrequest` which will add an entry in the `requests` table. The other half consists of incoming linking requests which can be accepted via a button which sends a `POST` request to `/accept`, clearing all existing associated requests from the `requests` table as well as updating their linked status in the `users` table.

`linked.html` is split into a 'trips' part and a 'breaks' part.
The 'trips' part is rendered by `/` querying the database for all trips inputted by the current user or their link, and displaying them in sorted order in a table. The table also contains a javascript countdown timer for the start/end time of each trip (depending on if the trip has already started or not). Each trip also has a button which sents a `POST` request to `/timer` and displays blank page with a larger countdown timer for that trip and its start/end time.
The 'breaks' part contains a table of the break schedule of the current user and their link in sorted order which also matches overlapping breaks and puts them in the same row, also displaying said overlap in a third column with corresponding start/end dates as well as the duration of the overlap in days. These overlap calculations and sorting are all done in `/` which are then passed through a `data` variable to `render_template`. (A decent amount of the layouts use a good amount of jinja for their rendering.)

## Other
`\login`, `\logout`, `\register`, and `\change_password` are almost the same as my implementations of them from CS50 Finance, save for the fact that session now also stores the id of the current user's linked user as well as the username of the current user (which are still cleared after logging out). Error throwing in `application.py` is still done through `apology()`.