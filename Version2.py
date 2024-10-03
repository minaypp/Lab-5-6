import random
import os
import sys

# Function to clear the console screen
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Base class for all cards
class Card:
    def __init__(self, name, description, energy_cost):
        self.name = name
        self.description = description
        self.energy_cost = energy_cost

    def play(self, game, player, target):
        pass

# Subclass for creature cards
class CreatureCard(Card):
    def __init__(self, name, description, energy_cost, attack, health, abilities=None):
        super().__init__(name, description, energy_cost)
        self.attack = attack
        self.health = health
        self.max_health = health
        self.abilities = abilities if abilities else []
        self.can_attack = 'Haste' in self.abilities
        self.is_taunt = 'Taunt' in self.abilities
        self.is_stealth = 'Stealth' in self.abilities
        self.owner = None

    def play(self, game, player, target=None):
        self.owner = player
        player.battlefield.append(self)
        game.turn_log.append(f"{player.name} played creature {self.name}.")
        game.game_log.append(f"{player.name} played creature {self.name}.")

        # Handle Battlecry abilities
        if 'Battlecry' in self.abilities:
            if self.name == 'Mage Apprentice':
                if target:
                    if isinstance(target, CreatureCard) or isinstance(target, Player):
                        target.take_damage(1, game)
                        game.turn_log.append(f"{self.name} deals 1 damage to {target.name} with Battlecry.")
                        game.game_log.append(f"{self.name} deals 1 damage to {target.name} with Battlecry.")
                    else:
                        print("Invalid target.")
                else:
                    print("No target selected for Battlecry.")
            elif self.name == 'Dragon':
                for creature in self.owner.opponent.battlefield.copy():
                    creature.take_damage(2, game)
                    game.turn_log.append(f"{self.name} deals 2 damage to {creature.name} with Battlecry.")
                    game.game_log.append(f"{self.name} deals 2 damage to {creature.name} with Battlecry.")

        # Handle Goblin's ability
        if self.name == 'Goblin':
            for creature in player.battlefield:
                if creature.name == 'Goblin' and creature != self:
                    creature.attack += 1
                    game.turn_log.append(f"{creature.name} gains +1 Attack due to another Goblin.")
                    game.game_log.append(f"{creature.name} gains +1 Attack due to another Goblin.")

        return True  # Indicate successful play

    def attack_target(self, game, target):
        game.turn_log.append(f"{self.owner.name}'s {self.name} attacks {target.name}.")
        game.game_log.append(f"{self.owner.name}'s {self.name} attacks {target.name}.")
        self.can_attack = False
        if isinstance(target, CreatureCard):
            target.take_damage(self.attack, game)
            if target.health > 0:
                self.take_damage(target.attack, game)
        elif isinstance(target, Player):
            target.take_damage(self.attack, game)

    def take_damage(self, amount, game):
        self.health -= amount
        game.turn_log.append(f"{self.name} takes {amount} damage.")
        game.game_log.append(f"{self.name} takes {amount} damage.")
        if self.health <= 0:
            self.die(game)

    def die(self, game):
        game.turn_log.append(f"{self.owner.name}'s {self.name} has died.")
        game.game_log.append(f"{self.owner.name}'s {self.name} has died.")
        self.owner.battlefield.remove(self)

# Subclass for spell cards
class SpellCard(Card):
    def __init__(self, name, description, energy_cost, effect):
        super().__init__(name, description, energy_cost)
        self.effect = effect

    def play(self, game, player, target=None):
        success = self.effect(game, player, target)
        if success:
            game.turn_log.append(f"{player.name} casts spell {self.name}.")
            game.game_log.append(f"{player.name} casts spell {self.name}.")
        return success

# Node class for the linked list implementation of hand and deck
class Node:
    def __init__(self, card):
        self.card = card
        self.next = None

# LinkedList class to represent the player's hand and deck
class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def add(self, card):
        new_node = Node(card)
        new_node.next = self.head
        self.head = new_node
        self.size += 1

    def remove(self, card_name):
        current = self.head
        previous = None
        while current:
            if current.card.name.lower() == card_name.lower():
                if previous:
                    previous.next = current.next
                else:
                    self.head = current.next
                self.size -= 1
                return current.card
            previous = current
            current = current.next
        return None  # Card not found

    def draw(self):
        if self.head is None:
            return None
        card = self.head.card
        self.head = self.head.next
        self.size -= 1
        return card

    def to_list(self):
        current = self.head
        cards = []
        while current:
            cards.append(current.card)
            current = current.next
        return cards

# Class representing the player's hand
class Hand:
    def __init__(self):
        self.cards = LinkedList()

    def add_card(self, card):
        self.cards.add(card)

    def remove_card(self, card_name):
        return self.cards.remove(card_name)

    def display(self):
        hand_cards = self.cards.to_list()
        print("\nYour hand:")
        for idx, card in enumerate(hand_cards):
            print(f"{idx + 1}. {card.name} (Cost: {card.energy_cost}) - {card.description}")
        if not hand_cards:
            print("Your hand is empty.")

    def has_playable_card(self, energy):
        for card in self.cards.to_list():
            if card.energy_cost <= energy:
                return True
        return False

# Class representing a player
class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 20
        self.energy = 3
        self.max_energy = 3
        self.hand = Hand()
        self.deck = LinkedList()
        self.battlefield = []
        self.discard_pile = []
        self.has_drawn_initial_hand = False
        self.opponent = None

    def draw_card(self):
        card = self.deck.draw()
        if card:
            self.hand.add_card(card)
            print(f"{self.name} draws {card.name}.")
        else:
            print(f"{self.name}'s deck is empty!")
            self.hp = 0
            print(f"{self.name} has no more cards to draw and loses the game!")

    def take_damage(self, amount, game):
        self.hp -= amount
        game.turn_log.append(f"{self.name} takes {amount} damage. HP is now {self.hp}.")
        game.game_log.append(f"{self.name} takes {amount} damage. HP is now {self.hp}.")

# Class representing the game
class Game:
    def __init__(self):
        self.players = []
        self.current_turn = 0
        self.turn_log = []
        self.game_log = []

    def start_game(self):
        clear_console()
        print("Welcome to the Python Card Game!")
        player1_name = input("Enter name for Player 1: ")
        player2_name = input("Enter name for Player 2: ")
        player1 = Player(player1_name)
        player2 = Player(player2_name)
        player1.opponent = player2
        player2.opponent = player1
        self.players = [player1, player2]
        self.setup_players()
        self.current_turn = random.randint(0, 1)
        print(f"{self.players[self.current_turn].name} will go first.")
        input("Press Enter to start the game...")
        self.main_game_loop()

    def setup_players(self):
        for player in self.players:
            deck_cards = self.create_deck()
            random.shuffle(deck_cards)
            for card in deck_cards:
                player.deck.add(card)

    def create_deck(self):
        deck = []
        # Creature Cards
        for _ in range(4):
            deck.append(CreatureCard(
                name="Goblin",
                description="Gain +1 Attack when another Goblin is played.",
                energy_cost=1,
                attack=1,
                health=1,
                abilities=[]
            ))
        for _ in range(3):
            deck.append(CreatureCard(
                name="Quick Archer",
                description="Can attack immediately when played (Haste).",
                energy_cost=1,
                attack=2,
                health=1,
                abilities=["Haste"]
            ))
        for _ in range(2):
            deck.append(CreatureCard(
                name="Knight Defender",
                description="Taunt (Enemies must attack this unit first).",
                energy_cost=3,
                attack=3,
                health=4,
                abilities=["Taunt"]
            ))
        for _ in range(2):
            deck.append(CreatureCard(
                name="Mage Apprentice",
                description="Battlecry: Deal 1 damage to any target.",
                energy_cost=3,
                attack=2,
                health=2,
                abilities=["Battlecry"]
            ))
        deck.append(CreatureCard(
            name="Rogue Assassin",
            description="Stealth (Cannot be targeted until it attacks).",
            energy_cost=4,
            attack=4,
            health=2,
            abilities=["Stealth"]
        ))
        deck.append(CreatureCard(
            name="Sorcerer Supreme",
            description="While in play, all spells in hand are free.",
            energy_cost=7,
            attack=2,
            health=2
