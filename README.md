# Discourse Leaderboard:
This is a python sctipt to crawl discourse and retrive required info.

## discourse.get_leaderboard()
A function to print a sorted list of the most solutions given by each user.
Solutions given to a co-worker will count as 10 points,
while self created topic will count as 5 points.

* Notes:
- The leaderboard function will quary topics withing a larger timeframe then given, but only solutions withing the timeframe will be chosen.]
this is to catch solutions giving for topics from the previous quarter. 
E.g - We want to test the solutions given in Q2 (Apr-Jul), topics that were created between Jan-Jul (Q1-Q2) will be parsed, and only soutions given in Q2 wil be chosen. 
- A debugging option is available - Run: `$ export LOGLEVEL=debug`, before running the python sctipt.

## Running the script:
1. Clone the project
2. In the main.py file:
    a. Fill in `discourse_user` and `discourse_read_api_token` with read permissions.
    b. Choose the required time frame (`before_date` and `after_date` dates), in a `%Y-%m-%d` format (E.g 01-01-2023)
3. Run: `$ python main.py`
