from telebot import TeleBot 
import db 
from time import sleep 

TOKEN = '5716281114:AAEILmG1Pwp40YbDuo_DKp2J5jP1e-OZqak' 
bot = TeleBot(TOKEN)

# Привет Чингиз!

game = False 
night = False

def get_killed(night):
    if not night:
        username_killed = db.citizens_kill()
        return f'Горажане выгнали:{username_killed}'
    username_killed = db.mafia_kill()
    return f'Мафия убила: {username_killed}'


def game_loop(message):
    global night, game
    bot.send_message(message.chat.id, 'Добро пожаловать в игру! Вам дается 2 минуты, чтобы познокомиться')
    sleep(2)
    while True:
        msg = get_killed(night)
        bot.send_message(message.chat.id, msg)
        if night:
            bot.send_message(message.chat.id, 'Город засыпает, просыпается мафия. Наступила ночь')
        else:
            bot.send_message(message.chat.id, 'Город просыпается. Наступил день')
        winner = db.check_winner()
        if winner == 'Мафия' or winner == 'Горожане':
            bot.send_message(message.chat.id, f'Победили {winner}')
            game = False    
            break    
        night = not night
        alive = db.get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id, 'В игре остались:\n' + alive)
        sleep(2)
        

@bot.message_handler(commands=['play'])
def start(message):
    bot.send_message(message.chat.id, "Если хотите играть напишите 'готов играть' в лс")


@bot.message_handler(func=lambda m: m.text.lower() == 'готов играть' and m.chat.type == 'private')
def send_text(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name} играет')
    bot.send_message(message.from_user.id, 'Вы добавлены в игру')
    db.insert_player(message.from_user.id, username=message.from_user.first_name)


@bot.message_handler(commands=['kick'])
def kick(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()
    if not night:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет')
            return
        voted = db.vote('citizen_vote', username, message.from_user.id)
        if voted: 
            bot.send_message(message.chat.id, "Ваш голос учитан")
            return 
        bot.send_message(message.chat.id, "У вас больше нет правва на голосовать!")
        return
    bot.send_message(message.chat.id, 'Сейчас ночь вы не можете никого выгнать')


@bot.message_handler(commands=['kill'])
def kill(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()
    mafia_usernames = db.get_mafia_usernames()
    if night:
        if message.from_user.name not in mafia_usernames:
            bot.send_message(message.chat.id, 'Вам нельзя убивать игроков')
            return
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет')
            return
        voted = db.vote('mafia_vote', username, message.from_user.id)
        if voted: 
            bot.send_message(message.chat.id, "Ваш голос учитан")
            return 
        bot.send_message(message.chat.id, "У вас больше нет правва на голосовать!")
        return
    bot.send_message(message.chat.id, 'Сейчас день вы не можете никого убить')



@bot.message_handler(commands=["start"])
def game_start(message):
    global game 
    players = db.players_amount()
    if players >= 2 and not game:
        db.set_roles(players)
        players_roles = db.get_players_roles()
        mafia_usernames = db.get_mafia_usernames()
        for player_id, role in players_roles:
            bot.send_message(player_id, text=role)
            if role == "mafia":
                bot.send_message(player_id, text=f'Все члены мафии:\n{mafia_usernames}')

        game = True 
        bot.send_message(message.chat.id, text='Игра началась!')
        
        game_loop(message)
        return 

    bot.send_message(message.chat.id, text='недастаточно людей!') 


if __name__ == '__main__':  
    bot.polling(none_stop=True)