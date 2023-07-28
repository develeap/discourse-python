import os
import logging as log
from discourse_leaderboard import discourse_leaderboard
import argparse

class case_insensitive_list(list):
    # list subclass that uses lower() when testing for 'in'
    def __contains__(self, other):
        return super(case_insensitive_list,self).__contains__(other.lower())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Script to quary Discourse topics and export resaults as .png file')
    parser.add_argument("-u", "--user", dest='user', required=True,
                                help='Username used to authenticate Discourse')
    parser.add_argument("-t", "--token", dest='token', required=True,
                                help='Token used to authenticate Discourse')
    parser.add_argument("-s", "--start_date", dest='start_date', required=True, default="2023-01-01",
                                help='Start date from which to quary topics (e.g 2023-01-01)')
    parser.add_argument("-e", "--end_date", dest='end_date', required=True, default="2023-01-11",
                                help='End date until which to quary topics (e.g 2023-04-01)')
    parser.add_argument("-l", "--log", dest='log', required=False, choices=case_insensitive_list(['debug', 'info', 'warning', 'error', 'critical']), default='INFO',
                                help='Set the log level',)

    args = parser.parse_args()
    print(args)
    USER = args.user
    TOKEN = args.token
    START_DATE = args.start_date
    END_DATE = args.end_date
    LOGLEVEL = args.log

    log.basicConfig(format='%(levelname)s: %(message)s', level=LOGLEVEL.upper())

    discourse  =  discourse_leaderboard(discourse_url = "https://develeap.discourse.group",
                                        discourse_user = USER,
                                        discourse_read_api_token = TOKEN,
                                        after_date = START_DATE,
                                        before_date = END_DATE)
    discourse.get_leaderboard() # create png of users leaderboard
