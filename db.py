# СОХРАНЕН 
import sqlite3 
from random import shuffle
con = sqlite3.connect("db.db") 
cur = con.cursor()


def insert_player(player_id, username):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"insert INTO players(player_id, username) VALUES ('{player_id}','{username}')" 
    cur.execute(sql)
    con.commit() 
    con.close()

def players_amount(): 
    con = sqlite3.connect("db.db") 
    cur = con.cursor()
    sql = f"Select * from players"
    cur.execute(sql)
    res = cur.fetchall()
    con.close()
    return len(res)

def get_mafia_usernames():
    con = sqlite3.connect("db.db") 
    cur = con.cursor()
    sql = f"SELECT username FROM PLAYERS where role = 'mafia' "
    cur.execute(sql)
    data = cur.fetchall()
    names = '' 
    for row in data: 
        name = row[0]
        names += name + '\n' 
    con.close()
    return names 

def get_players_roles(): 
    con = sqlite3.connect("db.db") 
    cur = con.cursor()
    sql = f"SELECT player_id, role FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data 


def get_all_alive():
    con = sqlite3.connect("db.db") 
    cur = con.cursor()
    sql = f"SELECT username FROM PLAYERS where dead = 0"
    cur.execute(sql)
    data = cur.fetchall()
    data = [row[0] for row in data]
    con.close()
    return data


def set_roles(players):
    game_roles = ["citizen"] * players
    mafia = int(players*0.3)
    for i in range(mafia):
        game_roles[i] = 'mafia'
    shuffle(game_roles)
    con = sqlite3.connect("db.db") 
    cur = con.cursor()  
    sql = "SELECT player_id FROM players"
    cur.execute(sql)
    player_ids = cur.fetchall()
    player_ids = [row[0] for row in player_ids]
    for role, player_id in zip(game_roles, player_ids):
        sql = f"UPDATE players SET role = '{role}' WHERE player_id = {player_id}"
        cur.execute(sql)
    con.commit()
    con.close()


def vote(type, username, player_id):
    # type = 'mafia_vote', 'citizen_vote'
    # username = 'username' <- против кого голосуют
    # player_id = player_id <- кто голосует:
    con = sqlite3.connect("db.db") 
    cur = con.cursor()  
    sql = f"SELECT username FROM players WHERE player_id = {player_id} AND dead = 0 AND voted = 0"
    cur.execute(sql)
    can_vote = cur.fetchone()
    print(can_vote)
    # can_vote -> ('username',) -> True or None -> False
    if can_vote:
        sql = f"UPDATE players SET {type} = {type} + 1 WHERE username = '{username}'"
        cur.execute(sql)
        sql = f"UPDATE players SET voted = 1 WHERE player_id = {player_id}"
        cur.execute(sql)
        con.commit()
        con.close()
        return True
    con.close()
    return False 


def mafia_kill():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f"SELECT MAX(mafia_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM players WHERE dead = 0 and role = 'mafia' ")
    mafia_alive = cur.fetchone()[0]
    username_killed = 'никого'
    if max_votes == mafia_alive: 
        cur.execute(f"SELECT username FROM players WHERE mafia_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}' ")
        con.commit()
    con.close()
    return username_killed 
    

def citizen_kill():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f"SELECT MAX(citizen_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM players WHERE citizen_vote = {max_votes}")
    max_votes_count = cur.fetchone()[0]
    username_killed = 'никого'

    if max_votes_count == 1:
        cur.execute(f"SELECT username FROM players WHERE citizen_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}' ")
        con.commit()
    con.close() 
    return username_killed 


def clear():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"UPDATE players SET citizen_vote = 0, mafia_vote = 0, mafia_vote = 0, voted = 0" 
    if dead:
        sql += ', dead = 0'
    cur.execute(sql)
    con.commit() 
    con.close()
   

def check_winner():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = "SELECTR COUNT(*) FROM players WHERE role = 'mafia' and dead = 0" 
    cur.execute(sql)
    mafia_alive = cur.fetchone()[0]
    sql = "SELECTR COUNT(*) FROM players WHERE role = 'citizen' and dead = 0" 
    cur.execute(sql)
    citizen_alive = cur.fetchone()[0]
    if mafia_alive >= citizen_alive:
        return 'Мафия'
    if mafia_alive == 0:
        return 'Горажане'


