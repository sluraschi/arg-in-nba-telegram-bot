import requests
import json
import os
import telebot
import logging
import time
from datetime import date
from Player import Player
from Team import Team

players = [Player("Deck", 9530711),
           Player("Campazzo", 3547304),
           Player("Vildoza", 11314392)]

base_url = "https://free-nba.p.rapidapi.com/"
get_player_endpoint = "players/"
get_matches_endpoint = "games/"

headers = {
    'x-rapidapi-key': os.environ['rapidapi-key']
}

bot = telebot.TeleBot(os.environ['telegram-token'], parse_mode=None)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.


def create_keyboard(keyboard):
    for player_to_add in players:
        keyboard.add(telebot.types.KeyboardButton(player_to_add.name))


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


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Que crack queres ver hoy?", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def check_games(message):
    payload = message.json
    player_to_search = payload["text"]

    logger.log(logging.INFO, "Message received with ID: " + str(payload["message_id"]))
    logger.log(logging.INFO, "From user with ID: " + payload["from"]["id"])
    logger.log(logging.INFO, "On Date: " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payload["date"]))))
    logger.log(logging.INFO, "Message: " + player_to_search)

    if player_to_search not in [p.name for p in players]:
        bot.reply_to(message, player_to_search + " no es un jugador que conozca, solo trabajo con cracks.", reply_markup=markup)
        return

    match = {}
    for option in markup.keyboard:
        if player_to_search == option[0]["text"]:
            match = team_plays(teams[player_to_search])

    # A helper class can help clean up the if-else
    if match:
        if match["period"] > 0:
            bot.reply_to(message, "El partido de " + player_to_search + " ya empezo! Va por el " + str(match["status"]), reply_markup=markup)
        else:
            logger.log(logging.INFO, player_to_search + " juega a las " + str(match["status"]))
            bot.reply_to(message, player_to_search + " juega a las " + str(match["status"]), reply_markup=markup)
    else:
        logger.log(logging.INFO, "Hoy no juega " + player_to_search + " :(")
        bot.reply_to(message, "Hoy no juega " + player_to_search + " :(", reply_markup=markup)


# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
#     bot.reply_to(message, "Mandame un jugador que conozca, a que crack queres ver?", reply_markup=markup)


markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
create_keyboard(markup)
teams = get_team_of_players()


def main():
    # check_games("Deck")
    bot.polling()


if __name__ == "__main__":
    main()
