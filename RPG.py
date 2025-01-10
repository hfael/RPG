import os
import sqlite3
import time
from PNJ import get_pnj_story
import random

current_directory = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_directory, "playerdata.db")
text_delay = 1

default_data = {
    "name": "null",
    "attack_damage": 10,
    "attack_speed": 1.0,
    "hp_max": 100,
    "current_village": "null",
    "potions": 0,
    "inventory": "[]",
    "xp": 0,
    "level": 1
}

villages = ["Boing", "Drum", "Jaya", "Gunhao", "Harahettia"]
monsters = [
    {"name": "Gobelin", "base_hp": 50, "base_attack_damage": 8, "base_attack_speed": 1.0},
    {"name": "Sanglier", "base_hp": 30, "base_attack_damage": 5, "base_attack_speed": 1.2},
    {"name": "Orc", "base_hp": 80, "base_attack_damage": 12, "base_attack_speed": 0.8},
    {"name": "Loup", "base_hp": 60, "base_attack_damage": 10, "base_attack_speed": 1.1},
    {"name": "Troll", "base_hp": 100, "base_attack_damage": 15, "base_attack_speed": 0.7},
    {"name": "Dragon", "base_hp": 150, "base_attack_damage": 20, "base_attack_speed": 0.6},
    {"name": "Nécromancien", "base_hp": 180, "base_attack_damage": 30, "base_attack_speed": 0.5}
]

items = {
    "attack_damage": {"name": "Potion de Force", "effect": 5},
    "attack_speed": {"name": "Élixir de Vitesse", "effect": 0.2},
    "hp_max": {"name": "Flacon de Santé", "effect": 20},
    "potion": {"name": "Potion de Soin", "effect": 30}
}

class RPG():
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.ask_name()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                name TEXT PRIMARY KEY,
                attack_damage INTEGER,
                attack_speed REAL,
                hp_max INTEGER,
                current_village TEXT,
                potions INTEGER,
                inventory TEXT,
                xp INTEGER,
                level INTEGER
            )
        ''')
        self.conn.commit()

    def ask_name(self):
        user_name = input("Entrez votre prénom: ")
        if user_name.isalpha() and 2 <= len(user_name) < 13:
            user_name = user_name.lower().capitalize()
            self.cursor.execute("SELECT * FROM players WHERE name = ?", (user_name,))
            player_data = self.cursor.fetchone()

            if player_data:
                self.nPrint(f"Bonjour, {user_name} !")
                player_data = dict(zip([col[0] for col in self.cursor.description], player_data))
                self.choose_village(player_data)
            else:
                self.nPrint(f"Ah, alors ton prénom c'est {user_name} !")
                player_data = default_data.copy()
                player_data["name"] = user_name
                self.cursor.execute('''
                    INSERT INTO players (name, attack_damage, attack_speed, hp_max, current_village, potions, inventory, xp, level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_name, default_data["attack_damage"], default_data["attack_speed"], default_data["hp_max"],
                      default_data["current_village"], default_data["potions"], default_data["inventory"],
                      default_data["xp"], default_data["level"]))
                self.conn.commit()
                self.nPrint("Le but du jeu va être de battre les monstres présents dans chaque village afin de sauver la population !")
                time.sleep(text_delay)
                self.nPrint("Sois prêt, car chaque monstre a sa propre façon de combattre !")
                self.choose_village(player_data)
        else:
            self.nPrint("Le nom d'utilisateur doit être alphabétique et contenir entre 2 et 12 caractères.")

    def choose_village(self, player_data):
        self.nPrint("Tu peux choisir parmi les villages suivants :")
        len_villages = len(villages)
        for i, village in enumerate(villages, start=1):
            self.nPrint(f"{i}. {village}")

        while True:
            try:
                choice = int(input("Choisis un village (1-5) : "))
                if 1 <= choice <= len_villages:
                    selected_village = villages[choice - 1]
                    player_data["current_village"] = selected_village
                    self.cursor.execute("UPDATE players SET current_village = ? WHERE name = ?", (selected_village, player_data["name"]))
                    self.conn.commit()
                    self.nPrint(f"Tu te diriges vers {selected_village}. Prépare-toi pour l'aventure !")
                    self.fight_monster(player_data, selected_village)
                    break
                else:
                    self.nPrint(f"Choix invalide. Entre un nombre entre 1 et {len_villages}.")
            except ValueError:
                self.nPrint(f"Entrée invalide. Entre un nombre entre 1 et {len_villages}.")

    def fight_monster(self, player_data, village):
        monster = random.choice(monsters)
        monster_level = player_data["level"]
        monster["hp"] = monster["base_hp"] + (monster_level * 10)
        monster["attack_damage"] = monster["base_attack_damage"] + (monster_level * 2)
        monster["attack_speed"] = monster["base_attack_speed"]

        player_attack_damage = player_data["attack_damage"]
        monster["hp"] += player_attack_damage // 2
        monster["attack_damage"] += player_data["hp_max"] // 20

        self.nPrint(f"Tu affrontes un {monster['name']} avec {monster['hp']} PV, {monster['attack_damage']} de dégâts d'attaque et {monster['attack_speed']} de vitesse d'attaque.")

        player_hp = player_data["hp_max"]
        player_attack_speed = player_data["attack_speed"]
        potions = player_data["potions"]

        while player_hp > 0 and monster["hp"] > 0:
            self.display_xp_bar(player_data)
            self.nPrint(f"PV du joueur: {player_hp}, PV du monstre: {monster['hp']}")
            self.nPrint("Que veux-tu faire ?")
            self.nPrint("1. Attaquer")
            self.nPrint("2. Fuir")
            if potions > 0:
                self.nPrint("3. Utiliser une potion de soin")
                choice = input("Choisis une action (1-3) : ")
            else:
                choice = input("Choisis une action (1-2) : ")

            if choice == "1":
                if player_attack_speed >= monster["attack_speed"]:
                    monster["hp"] -= player_attack_damage
                    self.nPrint(f"Tu attaques le {monster['name']} et lui infliges {player_attack_damage} dégâts.")
                if monster["hp"] > 0 and random.random() < monster["attack_speed"]:
                    player_hp -= monster["attack_damage"]
                    self.nPrint(f"Le {monster['name']} t'attaque et te fait {monster['attack_damage']} dégâts.")
            elif choice == "2":
                self.nPrint(f"Tu fuis le combat contre {monster['name']}.")
                break
            elif choice == "3" and potions > 0:
                self.nPrint(f"Tu utilises une potion de soin et récupères 30 PV.")
                player_hp += items["potion"]["effect"]
                potions -= 1
                self.cursor.execute("UPDATE players SET potions = ? WHERE name = ?", (potions, player_data["name"]))
                self.conn.commit()
            else:
                self.nPrint("Choix invalide ou pas de potion disponible.")

            if random.random() < monster["attack_speed"] and monster["hp"] > 0:
                player_hp -= monster["attack_damage"]
                self.nPrint(f"Le {monster['name']} t'attaque et te fait {monster['attack_damage']} dégâts.")

            time.sleep(text_delay)

        if player_hp > 0:
            self.nPrint(f"Tu as vaincu le {monster['name']} !")
            player_data["xp"] += 10
            if player_data["xp"] >= player_data["level"] * 50:
                self.level_up(player_data)
            item = random.choice(list(items.values()))
            self.nPrint(f"Tu obtiens un {item['name']} qui augmente ta statistique.")
            self.update_stats(player_data, item['effect'], item['name'])
            self.explore_village(player_data, village)
        else:
            self.nPrint(f"Tu as été vaincu par le {monster['name']}. Tu perds la bataille.")
            self.cursor.execute("DELETE FROM players WHERE name = ?", (player_data["name"],))
            self.conn.commit()
            self.nPrint("Ton aventure est terminée. Les données du joueur ont été supprimées.")
            exit()

    def level_up(self, player_data):
        player_data["level"] += 1
        player_data["xp"] = 0
        self.nPrint("Tu montes de niveau ! Choisis une statistique à améliorer :")
        self.nPrint("1. Augmenter les dégâts d'attaque")
        self.nPrint("2. Augmenter la vitesse d'attaque")
        self.nPrint("3. Augmenter les PV max")

        while True:
            choice = input("Choisis une statistique (1-3) : ")
            if choice == "1":
                player_data["attack_damage"] += 5
                self.nPrint("Tes dégâts d'attaque augmentent !")
                break
            elif choice == "2":
                player_data["attack_speed"] += 0.1
                self.nPrint("Ta vitesse d'attaque augmente !")
                break
            elif choice == "3":
                player_data["hp_max"] += 10
                self.nPrint("Tes PV max augmentent !")
                break
            else:
                self.nPrint("Choix invalide. Entre un nombre entre 1 et 3.")

        self.cursor.execute('''
            UPDATE players SET attack_damage = ?, attack_speed = ?, hp_max = ?, level = ?, xp = ? WHERE name = ?
        ''', (player_data["attack_damage"], player_data["attack_speed"], player_data["hp_max"],
              player_data["level"], player_data["xp"], player_data["name"]))
        self.conn.commit()

    def update_stats(self, player_data, effect, item_name):
        if item_name == "Potion de Force":
            player_data["attack_damage"] += effect
        elif item_name == "Élixir de Vitesse":
            player_data["attack_speed"] += effect
        elif item_name == "Flacon de Santé":
            player_data["hp_max"] += effect
        elif item_name == "Potion de Soin":
            pass

        self.cursor.execute('''
            UPDATE players SET attack_damage = ?, attack_speed = ?, hp_max = ? WHERE name = ?
        ''', (player_data["attack_damage"], player_data["attack_speed"], player_data["hp_max"], player_data["name"]))
        self.conn.commit()
        self.nPrint(f"Ta statistique a été améliorée grâce au {item_name}.")

    def display_xp_bar(self, player_data):
        xp_percentage = (player_data["xp"] / (player_data["level"] * 50)) * 100
        filled_bars = int(xp_percentage // 10)
        bar = "[" + "-" * filled_bars + "|" + "-" * (10 - filled_bars - 1) + "]"
        self.nPrint(f"XP: {bar} ({int(xp_percentage)}%)")

    def nPrint(self, text):
        for char in text:
            print(char, end='', flush=True)
            time.sleep(0.02)
        print()

if __name__ == "__main__":
    RPG()
