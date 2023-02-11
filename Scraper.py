from steam import Steam
from decouple import config
import json
import datetime
import os
from pprint import pprint

# These are just to get the Steam package to work
KEY = config("STEAM_API_KEY")
steam = Steam(KEY)


class Scraper:

    def __init__(self, user_id):

        self._user_id = user_id

        


    def get_owned_game_ids(self, uid):
        """_summary_

        Args:
            uid (str): Steam user id
        """

        user_game_info = steam.users.get_owned_games(uid)

        game_ids = {}

        user_games = user_game_info["games"]

        for game in user_games:
            # Retrieve game info
            
            appid = game["appid"]
            game_name = game["name"]
            game_icon_url_code = game["img_icon_url"]
            game_icon_url = f"https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/{appid}/{game_icon_url_code}.jpg"

            # Store appids with their associated game name and icon
            game_ids[appid] = (game_name, game_icon_url)
        
        return game_ids

    def get_achievements(self, uid):
        """_summary_

        Args:
            uid (str): Steam user id
            appids (_type_): Steam game ids to retrieve achievements for
        """
        all_game_achievements = {} # dict gamename: (appid, dict(achievement_name: unlocktime))

        user_games = self.get_owned_game_ids(uid)

        for appid in user_games:
            game_achievements = {}
            game_name = user_games[appid][0]
            game_icon_url = user_games[appid][1]

            # Games that don't have achievements will throw up a 400 error so need try-except
            try:
                game_achievement_info = steam.apps.get_user_achievements(uid, appid)

                game_achievement_list = game_achievement_info["playerstats"]["achievements"] # access the list containing a dict for each achievement

                for achievement in game_achievement_list:
                    # dict to generate the json to form the metadata for this achievement
                    achievement_dict = {}
                    if achievement["achieved"] == 1: # Only store unlocked achievements
                        achievement_name = \
                            achievement["apiname"].replace("achievement_", "").replace("ACHIEVEMENT_", "").capitalize() # remove the "achievement_" prefix and make the first character capitalised
                        achievement_name_pretty = " ".join(achievement_name.split("_"))
                        # Tie this achievement with its unlock time in the dict game_achievements for this appid
                        # unlocktime needs to be converted from unix
                        achievement_unlocktime = datetime.datetime.fromtimestamp(achievement["unlocktime"]).strftime("%d/%m/%Y %H:%M:%S")
                        game_achievements[achievement_name_pretty] = achievement_unlocktime

                        ### Create json for each achievement
                        achievement_dict["Achievement Title"] = achievement_name_pretty
                        achievement_dict["Game"] = game_name
                        achievement_dict["Game Icon"] = game_icon_url
                        achievement_dict["Date Unlocked"] = achievement_unlocktime
                        # Serializing json
                        json_object = json.dumps(achievement_dict, indent = 4)

                        # Create directory to save jsons to
                        output_path = f"achievement_metadata/{achievement_name}.json"
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
 
                        # Writing to sample.json
                        with open(output_path, "w") as outfile:
                            outfile.write(json_object)
                
                # store game name to access a tuple of the appid and the dict with each achievement and its unlocktime
                all_game_achievements[game_name] = (appid, game_icon_url, game_achievements)
            except:
                continue
        
        # Only use this if you want to output a json with all the achievements across all games
        """# Serializing json
        json_object = json.dumps(all_game_achievements, indent = 4)
 
        # Writing to sample.json
        with open("all_achievements.json", "w") as outfile:
            outfile.write(json_object)"""

        
        return all_game_achievements
