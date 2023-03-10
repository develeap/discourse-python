import os
import logging as log
from discourse_leaderboard import discourse_leaderboard

if __name__ == "__main__":
    LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
    log.basicConfig(format='%(levelname)s: %(message)s', level=LOGLEVEL)
    discourse = discourse_leaderboard(discourse_url = "https://develeap.discourse.group",
                                      discourse_user = "shaked.dotan",
                                      discourse_read_api_token = "5f261d48286eca134745f6616a9bcaacc3dfb240d9cfb62dffc95516b488e9f6",
                                      before_date = "2023-02-01",
                                      after_date = "2023-01-01")
    discourse.get_leaderboard() # list most accepted answers by user
