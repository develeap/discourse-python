import requests
import os
from datetime import datetime
import logging as log
import json

class bcolors:
    HEADER = '\033[95m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

class discourse_leaderboard():
    def __init__(self, discourse_url, discourse_user, discourse_read_api_token, before_date, after_date):
        self.AFTER_DATE = after_date
        self.BEFORE_DATE = before_date
        self.DISCOURSE_URL = discourse_url
        self.DISCOURSE_USER = discourse_user
        self.DISCOURSE_READ_API_TOKEN = discourse_read_api_token
        self.HEADERS = {
            "Accept": "application/json; charset=utf-8",
            "Api-Username": self.DISCOURSE_USER,
            "Api-Key": self.DISCOURSE_READ_API_TOKEN,
        }
        self.SEARCH_RESPONSE_JSON = []
        self.SORTED_USERS_POINTS = {}
        self.SORTED_USERS_POINTS_LIST = []

    def get_user_posts(self, user) -> int:
        user_posts = {}
        quary = '%20'.join([f'%40{user}', f'before%3A{self.BEFORE_DATE}', f'after%3A{self.AFTER_DATE}'])
        SEARCH_URL = f"{self.DISCOURSE_URL}/search?expanded=true&q={quary}"
        log.debug(f"SEARCH_URL: {SEARCH_URL}")
        search_response = requests.get(SEARCH_URL, headers = self.HEADERS); search_response.raise_for_status()
        search_response_json = search_response.json()
        non_topic_posts_ids = [post['id'] for post in search_response_json['posts'] if post['post_number'] != 1]
        return len(non_topic_posts_ids)

    def tie_breaker(self) -> bool:
        tied_points = list(self.SORTED_USERS_POINTS.items())[2][1] # points of third place
        tied_users = { user:self.SORTED_USERS_POINTS[user] for user in list(self.SORTED_USERS_POINTS)[2:] if self.SORTED_USERS_POINTS[user] == tied_points }
        
        max_posts = 0
        if len(tied_users) > 1:
            log.debug("Starting tie-breaker:")
            log.debug(f"tied_users: {tied_users}")
            for user in tied_users:
                temp_posts = self.get_user_posts(user)
                log.debug(f"user: {user}, posts made: {temp_posts} ")
                if max_posts < temp_posts:
                    max_posts = temp_posts
                    third_place_user = user
            if third_place_user != None:
                third_place_points = self.SORTED_USERS_POINTS.pop(third_place_user)
                SORTED_USERS_POINTS_LIST = [{dic:self.SORTED_USERS_POINTS[dic]} for dic in self.SORTED_USERS_POINTS]
                SORTED_USERS_POINTS_LIST.insert(2, {third_place_user:third_place_points}) # Insert most-posts-user to third place
        else:
            SORTED_USERS_POINTS_LIST = [{dic:self.SORTED_USERS_POINTS[dic]} for dic in self.SORTED_USERS_POINTS]
        self.SORTED_USERS_POINTS_LIST = SORTED_USERS_POINTS_LIST
        return len(tied_users) > 1, max_posts

    def get_topics(self) -> list:
        before_after_date_diff = (datetime.strptime(self.BEFORE_DATE, "%Y-%m-%d") - datetime.strptime(self.AFTER_DATE, "%Y-%m-%d"))
        topic_after_date = (datetime.strptime(self.AFTER_DATE, "%Y-%m-%d") - before_after_date_diff).date() # enlarge after date for topic quary
        quary = '%20'.join(['status%3Asolved', 'in%3Afirst', f'before%3A{self.BEFORE_DATE}', f'after%3A{topic_after_date}'])
        SEARCH_URL = f"{self.DISCOURSE_URL}/search?expanded=true&q={quary}"
        
        log.debug(f'SEARCH_URL: {SEARCH_URL}')
        search_response = requests.get(SEARCH_URL, headers = self.HEADERS); search_response.raise_for_status() # get all topics within the time frame
        self.SEARCH_RESPONSE_JSON = search_response.json()['posts']
        topics_id_list = [topic_json['topic_id'] for topic_json in self.SEARCH_RESPONSE_JSON]
        return topics_id_list

    def get_user_points_by_topic_id(self, id) -> dict:
        TOPIC_URL = f"{self.DISCOURSE_URL}/t/{id}"
        log.debug(f'TOPIC_URL: {TOPIC_URL}')
        topic_response = requests.get(TOPIC_URL, headers = self.HEADERS); topic_response.raise_for_status()
        topic_response_json = topic_response.json()
        accepted_post_num = topic_response_json['accepted_answer']['post_number'] - 1
        accepted_date = topic_response_json['post_stream']['posts'][accepted_post_num]['created_at'].split('T')[0]
        if datetime.strptime(accepted_date, "%Y-%m-%d") < datetime.strptime(self.AFTER_DATE, "%Y-%m-%d"):
            return {}
        topic_user = topic_response_json['post_stream']['posts'][0]['username']
        solution_user = topic_response_json['accepted_answer']['username']
        if topic_user == solution_user:
            points = 5
        else:
            points = 10
        return {solution_user: points}

    def get_leaderboard(self):
        user_points = {}
        topic_id_list = self.get_topics()
        dots = ["", ".", "..", "...", "...."]
        for i, topic_id in enumerate(topic_id_list):
            print(f"Fetching results{dots[i%len(dots)]}    ", end='\r')
            temp_dict = self.get_user_points_by_topic_id(topic_id)
            if temp_dict != {}:
                temp_key = list(temp_dict.keys())[0]
                temp_value = temp_dict[temp_key]
                if temp_key in user_points:
                    user_points[temp_key] += temp_value
                else:
                    user_points.update(temp_dict)
        
        log.info(f"Fetching results{dots[len(dots)-1]}")
        log.info(f"Done \n\n")
        print(f"And the winners are:")
        self.SORTED_USERS_POINTS = dict(sorted(user_points.items(), key=lambda item: item[1], reverse=True))
        tie_breaker, max_posts = self.tie_breaker()
        text = []
        for i, user in enumerate(self.SORTED_USERS_POINTS_LIST):
            addition = ''
            user_name = list(user.keys())[0]
            points = self.SORTED_USERS_POINTS_LIST[i][user_name]
            if i < 2:
                text_color = bcolors.GREEN
            elif i == 2:
                if tie_breaker:
                    addition = f"Tie-breaker: Won by most posts ({max_posts})! \n    ----------"
                    text_color = bcolors.YELLOW
                else:
                    addition = "\n"
                    text_color = bcolors.GREEN
            else:
                if tie_breaker and points == 35:
                    text_color = bcolors.CYAN
                else: 
                    text_color = bcolors.WHITE
            text.append(f"{i+1:3}. {user_name:.<15}...{points} {addition}")
            # print(text_color + f"{i+1:3}. {user_name:.<15}...{points} {addition}" + bcolors.ENDC)
        print(text)
