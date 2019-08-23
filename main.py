import json
import logging
import subprocess
import time

from bs4 import BeautifulSoup

# Set you friend name here
FRIEND = ["name1", "name2"]


def init_log(level=10):
    """
    init logging
    level <Int>: logging level
    return <None> : Empty
    """
    format = "%(asctime)s %(message)s"
    datefmt = "%m/%d/%Y %I:%M:%S"
    logging.basicConfig(format=format, datefmt=datefmt, level=level)
    logging.info("Set logging with : format={}, datefmt={}, lvl={}".format(format, datefmt, level))


def search_friend(users):
    """
    Check in all users if we find friend.
    users <Lst> : List of dictionnary with all user found in current server
    return <Lst> : List of user who are in FRIEND list
    """
    res = []
    try:
        for user in users:
            if user["na"] in FRIEND:
                logging.info("{} user ( {} ) find to friend list".format(user["id"], user["na"]))
                res.append(user)
    except Exception as e:
        logging.error(e)
    return res


def curl_get_all_player_cmd(player=65000, server="fr13"):
    """
    run a curl cmd to get all users from server Noarsil by default
    player <int> : number of player search
    server <Str> : Default server are Noarsil
    return <Tuple> : Output and error of the curl command
    """
    req = "curl -X GET https://foe-data.ovh/world/{}/player_search?player_name=&nb_battle_critere=0&nb_battle_value=&nb_point_critere=0&nb_point_value=&have_guild=2&player_actif=2&age=99&nb_element={}&num_page=1"
    process = subprocess.Popen(req.format(server, player), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # Launch the shell command:
    output, error = process.communicate()
    return (output, error)


def curl_get_player_cmd(player_id, server="fr13"):
    """
    Run a curl cmd to get all information about user id
    player_id : Player Id who need to find
    return <Tuple> : Output and error of the curl command
    """
    req = "curl -X GET https://foe-data.ovh/world/{}/player/{}"
    process = subprocess.Popen(req.format(server, player_id), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # Launch the shell command:
    output, error = process.communicate()
    return (output, error)


def check_activity(friends):
    """
    Check activity of all friends
    friends <Lst> : List of friends
    return <Lst> : List of friend information
    """
    result = []
    for friend in friends:
        tds = {}
        r = curl_get_player_cmd(friend["id"])
        soup = BeautifulSoup(r[0], 'html.parser')
        divs = soup.find("table", {"class": "table-user-information"})
        rows = divs.findAll('tr')
        for row in rows:
            tds[row.findAll('th')[0].text] = row.findAll('td')[0].text
        result.append(tds)
    return result


def display(friends, **kwargs):
    """
    Display data from friends. Can be custom with kwargs args
    friends <Lst> : Content list of friend with all information
    kwargs <Dict> : Can be content multiple value for display setting
            "type" : Type of display. Actually can only be set to Activity
            "max_time" : Maximun time in secondes before to considere a friend like inactive
    return Empty
    """
    type = kwargs["type"] if "type" in kwargs else "Activity"
    if type == "Activity":
        max_time = kwargs["max_time"] if "max_time" in kwargs else 604800  # 7 days
        logging.info("Display user sorted by last activity")
        v = sorted(friends, key=lambda x: time.strptime(x['Date du dernier changement de points'].strip(), "%d/%m/%Y"))
        for friend in v:
            last_activity = friend["Date du dernier changement de points"].strip()
            curent_time = time.mktime(time.gmtime())
            last_activity_time = time.mktime(time.strptime(last_activity, "%d/%m/%Y"))
            logging.info("Last activity of {} : \033[3{}{}{}".format(
                                                              friend["Joueur"],
                                                              "1m" if curent_time - last_activity_time > max_time else "2m",
                                                              last_activity,
                                                              "\033[0m"))


def main():
    """
    Entry point
    """
    init_log()

    r = curl_get_all_player_cmd()
    x = json.loads(r[0])
    if int(x["nb_players"]) > 65000:
        r = curl_get_player_cmd(x["nb_players"])
    x = json.loads(r[0])
    friends = search_friend(x["players"])
    result = check_activity(friends)
    display(result, type="Activity")


if __name__ == "__main__":
    main()
