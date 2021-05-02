import requests
import json
# import getopt, sys
import telebot
from datetime import date
from Player import Player
from Team import Team

players = [Player("Deck", 9530711),
           Player("Campazzo", 3547304)]

base_url = "https://free-nba.p.rapidapi.com/"
get_player_endpoint = "players/"
get_matches_endpoint = "games/"

headers = {
    'x-rapidapi-key': "c3ca4bcdd0msh04115e6644d31dbp16d152jsn7a294e5263c8",
    }

t_token = "1713690982:AAHxWq50NPijPQqSOJ-9l88V-vZomY5m7dA"
bot = telebot.TeleBot(t_token, parse_mode=None)

markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
itembtn1 = telebot.types.KeyboardButton('/Facu')
itembtn2 = telebot.types.KeyboardButton('/Tortu')
itembtn3 = telebot.types.KeyboardButton('Se viene Vildo?')
markup.add(itembtn1, itembtn2, itembtn3)

def get_team_of_players():
    player_and_teams = {}
    url = base_url + get_player_endpoint

    for p in players:
        response = requests.request("GET", url + str(p.id), headers=headers)
        if response.status_code != 200:
            return 1
        data = json.loads(response.content)
        player_and_teams[p.name] = Team(data["team"]["name"], data["team"]["id"], data["team"]["abbreviation"])

    return player_and_teams


def team_plays(team):
    # YY-mm-dd
    today = date.today()
    d = today.strftime("%Y-%m-%d")

    url = base_url + get_matches_endpoint
    querystring = {"dates[]": d, "per_page": "25", "page": "0"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code != 200:
        exit()
    data = json.loads(response.content)

    for game in data["data"]:
        if (game["home_team"]["id"] == team.id) or (game["visitor_team"]["id"] == team.id):
            return game

    return None


player = "Campazzo"
teams = get_team_of_players()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Que crack queres ver hoy?", reply_markup=markup)


@bot.message_handler(commands=['Facu'])
def check_games(message):
    result = team_plays(teams[player])
    if result:
        print("Juega el Facu a las", result["status"])
        bot.reply_to(message, "Juega el Facu a las " + str(result["status"]))
    else:
        print("Hoy no jeuga el Facu :(")
        bot.reply_to(message, "Hoy no juega el Facu :(")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Mandame un comando que conozca, a que crack queres ver?", reply_markup=markup)


def main():
    # short_options = "p:"
    # long_options = ["player="]

    # if ("Facu")
    # result = team_plays(teams[player])
    # if result:
    #     print("Juega el Facu a las", result["status"])

    bot.polling()


if __name__ == "__main__":
    main()
