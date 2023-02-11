import Scraper as Scraper
import time
from pprint import pprint

start_time = time.time() # time execution

# arguments: steam_id, app_id
steam_id = "76561198042800823"

user = Scraper.Scraper(steam_id)

pprint(user.get_achievements(steam_id))

#print(f"run time: {time.time() - start_time} seconds")