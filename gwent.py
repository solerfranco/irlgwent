import serial
import mysql.connector
from random import randint
import os
import pygame as audio
import time


def get_opponent():
    if player1.turno:
        return player2
    else:
        return player1


def apply_weather(effect, player):
        for card in player1.cards:
            if card.idRow == effect.idEffect:
                card.currentPower = 1
        for card in player2.cards:
            if card.idRow == effect.idEffect:
                card.currentPower = 1


def apply_tight_bond(effect, player):
    multiplier = sum(1 for card in player.cards if card.nombre == effect.name)
    for card in player.cards:
        if card.nombre == effect.name:
            card.currentPower *= multiplier


def apply_commanders_horn(effect, player):
    for card in player.cards:
        if card.idRow == effect.idRow:
            card.currentPower *= 2


def apply_effects():
    for card in player1.cards:
        card.currentPower = card.basePower
    for card in player2.cards:
        card.currentPower = card.basePower

    player1.cardEffects.sort(key=lambda x: x.idEffect, reverse=True)
    
    for effect in player1.cardEffects:
        get_persistent_effect(effect, player1)
    for effect in player2.cardEffects:
        get_persistent_effect(effect, player2)
    
    player1.update_rows()
    player2.update_rows()


def get_persistent_effect(effect, player):
    # Get the function from effects dictionary
    func = persistent_effects.get(effect.idEffect, "nothing")
    # Execute the function
    return func(effect, player)


persistent_effects = {
        1: apply_weather,
        2: apply_weather,
        3: apply_weather,
        4: apply_tight_bond,
        5: apply_commanders_horn,
    }


def end_of_round():
    player1.reset_round()
    player2.reset_round()
    play_sound('sounds/gana_ronda.wav')
    time.sleep(1)


def play_sound(path):
    sound = audio.mixer.Sound(path)
    sound.play()


# Efectos instantaneos


def spy(player, card):
    play_sound('sounds/spy.wav')
    print ('\033[97m' + "Lanzaron al espia " + card.nombre + '\033[0m')
    if card.special:
        get_opponent().heroCards.append(card)
    else:
        get_opponent().cards.append(card)
    get_opponent().update_rows()


def decoy(player, card):
    print('\033[97m' + "Un Jugador lanzo un Decoy!" + '\033[0m')
    scan = False
    while not scan:
        arduino_data = ser.readline()[:-2]
        if arduino_data:
            if arduino_data != '1':
                query = "SELECT name, power, special FROM card WHERE id_card = " + str(arduino_data)
                cursor.execute(query)
                for (name, power, special) in cursor:
                    if special:
                        print("No puedes seleccionar una carta especial/heroe")
                        continue
                    for carta in player.cards:
                        if(carta.nombre == name):
                            player.cards.remove(carta)
                            print ("Un Jugador Cambio a " + name + " por un Decoy!")
                            break
            scan = True


def medic(player, card):
    scan = False
    play_sound('sounds/revive.wav')
    player.append_card(card)
    print( '\033[36m' + "Un jugador esta resucitando unidades" + '\033[0m')
    while not scan:
        arduino_data = ser.readline()[:-2]
        if arduino_data:
            if arduino_data != 'pass':
                if not player.place_card(arduino_data, False):
                    print("No puedes seleccionar una carta especial/heroe")
                    continue
            scan = True


def dragon_scorch(player, card):
    player.append_card(card)
    opponent = get_opponent()
    
    if (opponent.rowPower[0] + opponent.heroRowPower[0]) >= 10:
        power = 0
        for unit in opponent.cards:
            if unit.currentPower > power and unit.idRow == 1:
                power = unit.currentPower
        for unit in opponent.cards:
            if unit.currentPower == power and unit.idRow == 1:
                print('\033[91m' + "La carta " + unit.nombre + " ha sido destruida!" + '\033[0m')
        opponent.cards = filter(lambda item: item.currentPower != power, opponent.cards)
        opponent.update_rows()

def scorch(player, card):
    print ("Lanzaron un scorch")
    opponent = get_opponent()
    power = 0
    for unit in opponent.cards:
        if unit.currentPower > power:
            power = unit.currentPower
    for unit in player.cards:
        if unit.currentPower > power:
            power = unit.currentPower
    for unit in opponent.cards:
        print unit.currentPower
        if unit.currentPower == power:
            print('\033[91m' + "La carta " + unit.nombre + " ha sido destruida!" + '\033[0m')
    opponent.cards = filter(lambda item: item.currentPower != power, opponent.cards)
    for unit in player.cards:
        if unit.currentPower == power:
            print('\033[91m' + "La carta " + unit.nombre + " ha sido destruida!" + '\033[0m')
    player.cards = filter(lambda item: item.currentPower != power, player.cards)
    player.update_rows()
    opponent.update_rows()


def commanders_horn(player, card):
    print ('\033[93m' + "Lanzaron un cuerno de comandante!" + '\033[0m')
    effect = CardEffect(5,int(input()),card.nombre)
    player.cardEffects.append(effect)
    apply_effects()


def tight_bond(player, card):
    player.append_card(card)
    print ('\033[93m' + "Lanzaron una unidad multiplicador!" + '\033[0m')
    already_active = False
    for effect in player.cardEffects:
        if card.nombre == effect.name:
            already_active = True
    if not already_active:
        effect = CardEffect(4, 1, card.nombre)
        player.cardEffects.append(effect)

def normal(player, card):
    player.append_card(card)

def get_effect(effect, player, card):
    # Get the function from effects dictionary
    func = effects.get(effect, "nothing")
    # Execute the function
    return func(player, card)


effects = {
        1: normal,
        2: spy,
        3: decoy,
        4: medic,
        5: dragon_scorch,
        6: commanders_horn,
        7: scorch,
        8: tight_bond
    }


class Player:
    def __init__(self, number, turno, rondasGanadas, surrender, cardEffects, rowPower, cards, heroRowPower, heroCards, puntosTotales):
        self.number = number
        self.turno = turno
        self.rondasGanadas = rondasGanadas
        self.surrender = surrender
        self.cardEffects = cardEffects
        self.rowPower = rowPower
        self.cards = cards
        self.heroRowPower = heroRowPower
        self.heroCards = heroCards
        self.puntosTotales = puntosTotales

    def update_rows(self):
        self.rowPower = [0,0,0]
        self.heroRowPower = [0,0,0]
        for row_card in self.cards:
            self.rowPower[row_card.idRow - 1] += row_card.currentPower
        for row_card in self.heroCards:
            self.heroRowPower[row_card.idRow - 1] += row_card.currentPower
        self.puntosTotales = 0
        for index, row in enumerate(self.rowPower):
            self.puntosTotales += row
            self.puntosTotales += self.heroRowPower[index]
    
    def reset_round(self):
        self.turno = False
        self.surrender = False
        del self.cards[:]
        del self.heroCards[:]
        del self.cardEffects[:]
        self.update_rows()
    
    def append_card(self, card):
        if card.special:
            self.heroCards.append(card)
        else:
            self.cards.append(card)
        print('\033[95m' + "Un Jugador Lanzo a " + card.nombre + '\033[0m')
        if card.idRow == 1:
            play_sound('sounds/guerrero.wav')
        if card.idRow == 2:
            play_sound('sounds/arquero.wav')
        if card.idRow == 3:
            play_sound('sounds/asedio.wav')
    
    def place_card(self, arduino_data, can_special):
        query = "SELECT power, name, id_row, special, id_effect FROM card WHERE id_card = " + str(arduino_data)
        cursor.execute(query)
        for (power, name, id_row, special, id_effect) in cursor:
            card = Card(name, power, power, id_row, special)
            if special and not can_special:
                return False
            get_effect(id_effect, self, card)
            return True

    def get_card(self):
        arduino_data = ser.readline()[:-2]
        if arduino_data:
            if arduino_data == 'pass':
                self.surrender = True
                self.turno = False
                get_opponent().turno = True
                print("El jugador decide rendirse")
                print("")
            else:
                self.place_card(arduino_data, True)
                apply_effects()
                self.update_rows()
            time.sleep(2)
            if not get_opponent().surrender:
                get_opponent().turno = True
                self.turno = False
            print("")

    def turn(self):
        if not self.surrender and self.turno:
            play_sound('sounds/turno_player' + str(self.number) + '.wav')
            print ('\033[94m' + "Turno del Jugador " + str(self.number) + '\033[0m' )
            self.get_card()

    def round_winner(self):
        self.rondasGanadas += 1
        print ("Player " + str(self.number) + " Gano la ronda!")
        if self.rondasGanadas == 2:
            global partidaFinalizada
            partidaFinalizada = True
            time.sleep(1)
            print ("Player " + str(self.number) + " Gano la partida!")


class Card:
    def __init__(self, nombre, basePower, currentPower, idRow, special):
        self.nombre = nombre
        self.basePower = basePower
        self.currentPower = currentPower
        self.idRow = idRow
        self.special = special


class CardEffect:
    def __init__(self, idEffect, idRow, name):
        self.idEffect = idEffect
        self.idRow = idRow
        self.name = name


audio.mixer.init()
audio.mixer.music.load("drink.mp3")
audio.mixer.music.set_volume(0.5)
audio.mixer.music.play(-1)


ser = serial.Serial('/dev/ttyACM0', 9600)
cnx = mysql.connector.connect(user='franco', password='mysql', database='card_game')
cursor = cnx.cursor()
partidaFinalizada = False    

time.sleep(1)
print("Inicia La partida")
play_sound('sounds/inicia_partida.wav')
time.sleep(2)

# Empieza la partida
player1 = Player(1, False, 0, False, [], [0, 0, 0], [], [0, 0, 0], [], 0)
player2 = Player(2, False, 0, False, [], [0, 0, 0], [], [0, 0, 0], [], 0)
player1_start_round = randint(0, 1)

print("Lanzamos una moneda y...")
play_sound('sounds/coin.wav')
time.sleep(1)

while not partidaFinalizada:
    # Se determina quien empieza la partida.
    player1.turno = player1_start_round
    player2.turno = not player1_start_round

    # Empieza la Ronda
    while not player1.surrender or not player2.surrender:
        # Turno de Jugador 1
        player1.turn()
        os.system('clear')
        print('\033[92m' + "Puntos del jugador " + str(player1.number) + '\033[0m')
        print("Puntos de Guerrero:" + str(player1.rowPower[0] + player1.heroRowPower[0]))
        print ("Puntos de Arquero:" + str(player1.rowPower[1] + player1.heroRowPower[1]))
        print ("Puntos de Asedio:" + str(player1.rowPower[2] + player1.heroRowPower[2]))
        print ("Puntos Totales:" + str(player1.puntosTotales))
        print('\033[92m' + "Puntos del jugador " + str(player2.number) + '\033[0m')
        print("Puntos de Guerrero:" + str(player2.rowPower[0] + player2.heroRowPower[0]))
        print ("Puntos de Arquero:" + str(player2.rowPower[1] + player2.heroRowPower[1]))
        print ("Puntos de Asedio:" + str(player2.rowPower[2] + player2.heroRowPower[2]))
        print ("Puntos Totales:" + str(player2.puntosTotales))
        # Turno de Jugador 2
        player2.turn()
        os.system('clear')
        print('\033[92m' + "Puntos del jugador " + str(player1.number) + '\033[0m')
        print("Puntos de Guerrero:" + str(player1.rowPower[0] + player1.heroRowPower[0]))
        print ("Puntos de Arquero:" + str(player1.rowPower[1] + player1.heroRowPower[1]))
        print ("Puntos de Asedio:" + str(player1.rowPower[2] + player1.heroRowPower[2]))
        print ("Puntos Totales:" + str(player1.puntosTotales))
        print('\033[92m' + "Puntos del jugador " + str(player2.number) + '\033[0m')
        print("Puntos de Guerrero:" + str(player2.rowPower[0] + player2.heroRowPower[0]))
        print ("Puntos de Arquero:" + str(player2.rowPower[1] + player2.heroRowPower[1]))
        print ("Puntos de Asedio:" + str(player2.rowPower[2] + player2.heroRowPower[2]))
        print ("Puntos Totales:" + str(player2.puntosTotales))
    
    #Finaliza la Ronda
    time.sleep(1)
    if player1.puntosTotales > player2.puntosTotales:
        player1.round_winner()
    else:
        player2.round_winner()

    player1_start_round = not player1_start_round
    end_of_round()

play_sound('sounds/gana_partida.wav')
time.sleep(10)
cursor.close()
cnx.close()
