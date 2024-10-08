import random
import os
import sys

# Function to clear the console depending on the operating system
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Base class for all cards (both creature cards and spell cards)
class Card:
    def __init__(self, name, description, energy_cost):
        # Initialize common attributes for all cards
        self.name = name
        self.description = description
        self.energy_cost = energy_cost

    # Default play method, meant to be overridden by subclasses
    def play(self, game, player, target):
        pass

# Subclass for creature cards with additional attributes specific to creatures
class CreatureCard(Card):
    def __init__(self, name, description, energy_cost, attack, health, abilities=None):
        super().__init__(name, description, energy_cost)  # Call parent constructor
        self.attack = attack  # Attack points of the creature
        self.health = health  # Current health of the creature
        self.max_health = health  # Maximum health the creature can have
        self.abilities = abilities if abilities else []  # Special abilities the creature might have
        self.can_attack = 'Haste' in self.abilities  # Can the creature attack immediately (Haste ability)?
        self.is_taunt = 'Taunt' in self.abilities  # Is the creature a Taunt? (Must be attacked first)
        self.is_stealth = 'Stealth' in self.abilities  # Is the creature in Stealth? (Can't be targeted)
        self.owner = None  # The player who controls this creature

    # Method to play the creature on the battlefield
    def play(self, game, player, target=None):
        self.owner = player  # Set the owner of the creature
        player.battlefield.append(self)  # Add the creature to the player's battlefield
        game.turn_log.append(f"{player.name} played creature {self.name}.")
        game.game_log.append(f"{player.name} played creature {self.name}.")

        # Handle Battlecry abilities that trigger when the creature is played
        if 'Battlecry' in self.abilities:
            if self.name == 'Mage Apprentice':
                # Mage Apprentice deals 1 damage to a target when played
                if target:
                    if isinstance(target, CreatureCard) or isinstance(target, Player):
                        if target.is_stealth:
                            print(f"{target.name} cannot be targeted due to Stealth.")
                            return False
                        target.take_damage(1, game)
                        game.turn_log.append(f"{self.name} deals 1 damage to {target.name} with Battlecry.")
                        game.game_log.append(f"{self.name} deals 1 damage to {target.name} with Battlecry.")
                    else:
                        print("Invalid target.")
                        return False
                else:
                    print("No target selected for Battlecry.")
                    return False
            elif self.name == 'Dragon':
                # Dragon deals 2 damage to all enemy creatures upon being played
                for creature in self.owner.opponent.battlefield.copy():
                    if not creature.is_stealth:  # Stealth creatures cannot be targeted
                        creature.take_damage(2, game)
                        game.turn_log.append(f"{self.name} deals 2 damage to {creature.name} with Battlecry.")
                        game.game_log.append(f"{self.name} deals 2 damage to {creature.name} with Battlecry.")

        # Handle Goblin's ability to boost other Goblins' attack
        if self.name == 'Goblin':
            for creature in player.battlefield:
                if creature.name == 'Goblin' and creature != self:
                    creature.attack += 1
                    game.turn_log.append(f"{creature.name} gains +1 Attack due to another Goblin.")
                    game.game_log.append(f"{creature.name} gains +1 Attack due to another Goblin.")

        return True  # Indicate successful play

    # Method to initiate an attack on a target (creature or player)
    def attack_target(self, game, target):
        # Remove Stealth status after attacking
        if self.is_stealth:
            self.is_stealth = False
            game.turn_log.append(f"{self.name} loses Stealth after attacking.")
            game.game_log.append(f"{self.name} loses Stealth after attacking.")

        game.turn_log.append(f"{self.owner.name}'s {self.name} attacks {target.name}.")
        game.game_log.append(f"{self.owner.name}'s {self.name} attacks {target.name}.")
        self.can_attack = False  # Set creature to be unable to attack until the next turn
        if isinstance(target, CreatureCard):
            target.take_damage(self.attack, game)  # Deal damage to the target creature
            if target.health > 0:
                self.take_damage(target.attack, game)  # If target survived, it retaliates
        elif isinstance(target, Player):
            target.take_damage(self.attack, game)  # Deal damage to the player

    # Method to apply damage to the creature
    def take_damage(self, amount, game):
        self.health -= amount
        game.turn_log.append(f"{self.name} takes {amount} damage.")
        game.game_log.append(f"{self.name} takes {amount} damage.")
        if self.health <= 0:  # If health drops to zero or below, the creature dies
            self.die(game)

    # Method to remove the creature from the battlefield when it dies
    def die(self, game):
        game.turn_log.append(f"{self.owner.name}'s {self.name} has died.")
        game.game_log.append(f"{self.owner.name}'s {self.name} has died.")
        self.owner.battlefield.remove(self)  # Remove the creature from the owner's battlefield

# Subclass for spell cards, which have effects rather than stats
class SpellCard(Card):
    def __init__(self, name, description, energy_cost, effect):
        super().__init__(name, description, energy_cost)  # Call parent constructor
        self.effect = effect  # Function to define what happens when the spell is played

    # Method to play the spell, applying its effect
    def play(self, game, player, target=None):
        success = self.effect(game, player, target)  # Apply the spell's effect
        if success:
            game.turn_log.append(f"{player.name} casts spell {self.name}.")
            game.game_log.append(f"{player.name} casts spell {self.name}.")
        return success

# Node class for linked list to represent each card in the deck or hand
class Node:
    def __init__(self, card):
        self.card = card  # Store the card
        self.next = None  # Pointer to the next node

# Linked list class to manage a deck or hand of cards
class LinkedList:
    def __init__(self):
        self.head = None  # Head (first node) of the linked list
        self.size = 0  # Number of nodes in the linked list

    # Add a card to the linked list (deck/hand)
    def add(self, card):
        new_node = Node(card)
        new_node.next = self.head  # Insert the new node at the beginning
        self.head = new_node
        self.size += 1

    # Remove a card by name from the linked list
    def remove(self, card_name):
        current = self.head
        previous = None
        while current:
            if current.card.name.lower() == card_name.lower():  # Found the card
                if previous:
                    previous.next = current.next  # Remove current node from the list
                else:
                    self.head = current.next  # Update head if the card is the first node
                self.size -= 1
                return current.card
            previous = current
            current = current.next
        return None  # Card not found

    # Draw the top card (head) from the deck/hand
    def draw(self):
        if self.head is None:
            return None  # Return None if no cards left
        card = self.head.card  # Get the card at the head
        self.head = self.head.next  # Move the head to the next node
        self.size -= 1
        return card

    # Convert the linked list of cards into a list for easier handling
    def to_list(self):
        current = self.head
        cards = []
        while current:
            cards.append(current.card)
            current = current.next
        return cards

# Class representing the player's hand, which holds cards to play
class Hand:
    def __init__(self):
        self.cards = LinkedList()  # The hand is a linked list of cards

    # Add a card to the hand
    def add_card(self, card):
        self.cards.add(card)

    # Remove a card from the hand by name
    def remove_card(self, card_name):
        return self.cards.remove(card_name)

    # Display the cards in the player's hand with energy and deck size info
    def display(self, player):
        hand_cards = self.cards.to_list()
        print(f"\nYour hand (Energy: {player.energy}/{player.max_energy}, Deck: {player.deck.size} cards left):")
        for idx, card in enumerate(hand_cards):
            print(f"{idx + 1}. {card.name} (Cost: {card.energy_cost}) - {card.description}")
        if not hand_cards:
            print("Your hand is empty.")

    # Check if there is at least one card that the player can afford to play
    def has_playable_card(self, energy):
        for card
