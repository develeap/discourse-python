import os
import logging as log
from discourse_leaderboard import discourse_leaderboard

if __name__ == "__main__":
    LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
    log.basicConfig(format='%(levelname)s: %(message)s', level=LOGLEVEL)
    discourse = discourse_leaderboard(discourse_url = "https://develeap.discourse.group",
                                      discourse_user = "",
                                      discourse_read_api_token = "",
                                      before_date = "2023-02-01",
                                      after_date = "2023-01-01")
    discourse.get_leaderboard() # list most accepted answers by user
