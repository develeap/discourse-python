import requests
import os
from datetime import datetime
import logging as log
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

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
class rgb_colors:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    PURPLE = (255,0,255)
    CYAN = (0,255,255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

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
        self.IS_TIE_BREAKER = False
        self.IMAGE_DARK_MODE = True

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
        third_place_user = None
        SORTED_USERS_POINTS_LIST = []
        tied_points = list(self.SORTED_USERS_POINTS.items())[2][1] # points of third place
        tied_users = { user:self.SORTED_USERS_POINTS[user] for user in list(self.SORTED_USERS_POINTS)[2:] if self.SORTED_USERS_POINTS[user] == tied_points }
        
        max_posts = 0
        if len(tied_users) > 1:
            log.info("Starting tie-breaker:")
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
        try:
            accepted_date = topic_response_json['post_stream']['posts'][accepted_post_num]['created_at'].split('T')[0]
        except IndexError:
            accepted_date = topic_response_json['post_stream']['posts'][len(topic_response_json['post_stream']['posts'])-1]['created_at'].split('T')[0]
        if datetime.strptime(accepted_date, "%Y-%m-%d") < datetime.strptime(self.AFTER_DATE, "%Y-%m-%d"):
            return {}
        topic_user = topic_response_json['post_stream']['posts'][0]['username']
        solution_user = topic_response_json['accepted_answer']['username']
        if topic_user == solution_user:
            points = 5
        else:
            points = 10
        return {solution_user: points}

    def fnt_color(self, i, is_last=False):
        if i < 2:
            return rgb_colors.GREEN
        if i == 2:
            if self.IS_TIE_BREAKER:
                return rgb_colors.YELLOW
            return rgb_colors.GREEN
        if is_last and self.IS_TIE_BREAKER:
            return rgb_colors.YELLOW
        if self.IMAGE_DARK_MODE:
            return rgb_colors.WHITE
        return rgb_colors.BLACK

    def list_to_png(self, text_list):
        img_background = rgb_colors.BLACK if (self.IMAGE_DARK_MODE) else rgb_colors.WHITE 
        img_hight = len(text_list)*45+60
        with open('Monaco.ttf', 'rb') as f:
            bytes_font = BytesIO(f.read())
        if self.IS_TIE_BREAKER:
            img_width = 1000
            # footnot_fnt = ImageFont.truetype(bytes_font, 15)
        else:
            img_width = 650
        
        fnt = ImageFont.truetype(bytes_font, 35)
        img = Image.new('RGB', (img_width, img_hight), color=img_background)
        draw = ImageDraw.Draw(img)
        is_footnote = False
        
        for index, line in enumerate(text_list):
            is_footnote = (index == len(text_list)-1) and self.IS_TIE_BREAKER
            draw.text((40, 45*index+30), text_list[index], font=fnt, fill=self.fnt_color(index, is_footnote))
        img.save('discourse_leaderboard.png')

    def get_leaderboard(self):
        user_points = {}
        topic_id_list = self.get_topics()
        # dots = ["", ".", "..", "...", "...."]
        log.info("Fetching results:")
        for i, topic_id in enumerate(topic_id_list):
            # log.info(f"Fetching results{dots[i%len(dots)]}    ", end='\r') # github action issues
            temp_dict = self.get_user_points_by_topic_id(topic_id)
            if temp_dict != {}:
                temp_key = list(temp_dict.keys())[0]
                temp_value = temp_dict[temp_key]
                if temp_key in user_points:
                    user_points[temp_key] += temp_value
                else:
                    user_points.update(temp_dict)
        
        # log.info(f"Fetching results{dots[len(dots)-1]}")
        log.info(f"Done \n\n")
        self.SORTED_USERS_POINTS = dict(sorted(user_points.items(), key=lambda item: item[1], reverse=True))
        self.IS_TIE_BREAKER, max_posts = self.tie_breaker()
        text_list = []
        footnote = ''
        if self.IS_TIE_BREAKER:
            footnote = f"Tie-breaker: {list(self.SORTED_USERS_POINTS_LIST[2].keys())[0]} won by most posts ({max_posts})!"
        for i, user in enumerate(self.SORTED_USERS_POINTS_LIST):
            user_name = list(user.keys())[0]
            points = self.SORTED_USERS_POINTS_LIST[i][user_name]
            text_list.append(f"{i+1:3}. {user_name:.<15}...{points}")
        text_list.append(footnote)
        log.info(f"And the winners are:")
        self.list_to_png(text_list)
