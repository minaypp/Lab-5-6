
import random
import os
import sys

# Clear console function
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Base Card class
class Card:
    def __init__(self, name, description, energy_cost):
        self.name = name
        self.description = description
        self.energy_cost = energy_cost

    def play(self, game, player, target):
        pass

# Creature Card subclass
class CreatureCard(Card):
    def __init__(self, name, description, energy_cost, attack, health, abilities=None):
        super().__init__(name, description, energy_cost)
        self.attack = attack
        self.health = health
        self.max_health = health
        self.abilities = abilities if abilities else []
        self.can_attack = False if 'Haste' not in self.abilities else True
        self.is_taunt = 'Taunt' in self.abilities
        self.is_stealth = 'Stealth' in self.abilities
        self.owner = None

    def play(self, game, player, target=None):
        self.owner = player
        player.battlefield.append(self)
        game.log.append(f"{player.name} played creature {self.name}.")

    def attack_target(self, game, target):
        game.log.append(f"{self.owner.name}'s {self.name} attacks {target.name}.")
        self.can_attack = False
        if isinstance(target, CreatureCard):
            self.deal_damage(target, self.attack)
            target.deal_damage(self, target.attack)
            if self.health <= 0:
                self.die(game)
            if target.health <= 0:
                target.die(game)
        elif isinstance(target, Player):
            target.take_damage(self.attack, game)

    def deal_damage(self, target, damage):
        target.health -= damage

    def die(self, game):
        game.log.append(f"{self.owner.name}'s {self.name} has died.")
        self.owner.battlefield.remove(self)

# Spell Card subclass
class SpellCard(Card):
    def __init__(self, name, description, energy_cost, effect):
        super().__init__(name, description, energy_cost)
        self.effect = effect

    def play(self, game, player, target=None):
        game.log.append(f"{player.name} casts spell {self.name}.")
        self.effect(game, player, target)

# Node class for LinkedList
class Node:
    def __init__(self, card):
        self.card = card
        self.next = None

# LinkedList class for deck and hand
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
            if current.card.name == card_name:
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

# Hand class
class Hand:
    def __init__(self):
        self.cards = LinkedList()

    def add_card(self, card):
        self.cards.add(card)

    def remove_card(self, card_name):
        return self.cards.remove(card_name)

    def display(self):
        hand_cards = self.cards.to_list()
        print("Your hand:")
        for idx, card in enumerate(hand_cards):
            print(f"{idx + 1}. {card.name} (Cost: {card.energy_cost}) - {card.description}")

# Player class
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

    def draw_card(self):
        card = self.deck.draw()
        if card:
            self.hand.add_card(card)
            print(f"{self.name} draws {card.name}.")
        else:
            print(f"{self.name}'s deck is empty!")

    def take_damage(self, amount, game):
        self.hp -= amount
        game.log.append(f"{self.name} takes {amount} damage. HP is now {self.hp}.")

    def play_card(self, card_name, game, target=None):
        card = self.hand.remove_card(card_name)
        if card:
            if self.energy >= card.energy_cost:
                self.energy -= card.energy_cost
                card.play(game, self, target)
                self.discard_pile.append(card)
            else:
                print("Not enough energy to play this card.")
                self.hand.add_card(card)  # Return card to hand
        else:
            print("Card not found in hand.")

# Game class
class Game:
    def __init__(self):
        self.players = []
        self.current_turn = 0
        self.log = []

    def start_game(self):
        clear_console()
        print("Welcome to the Python Card Game!")
        player1_name = input("Enter name for Player 1: ")
        player2_name = input("Enter name for Player 2: ")
        self.players = [Player(player1_name), Player(player2_name)]
        self.setup_players()
        self.main_game_loop()

    def setup_players(self):
        for player in self.players:
            # Initialize decks with predefined cards
            deck_cards = self.create_deck()
            random.shuffle(deck_cards)
            for card in deck_cards:
                player.deck.add(card)
            # Draw starting hand
            for _ in range(5):
                player.draw_card()

    def create_deck(self):
        # Create deck with the specified cards
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
            health=2,
            abilities=[]
        ))
        deck.append(CreatureCard(
            name="Dragon",
            description="Battlecry: Deal 2 damage to all enemy creatures.",
            energy_cost=6,
            attack=6,
            health=6,
            abilities=["Battlecry"]
        ))
        deck.append(CreatureCard(
            name="Ancient Golem",
            description="A powerful creature.",
            energy_cost=7,
            attack=10,
            health=10,
            abilities=[]
        ))
        # Spell Cards
        for _ in range(2):
            deck.append(SpellCard(
                name="Fireball",
                description="Deal 5 damage to any target.",
                energy_cost=3,
                effect=self.fireball_effect
            ))
        for _ in range(3):
            deck.append(SpellCard(
                name="Buff",
                description="Give a creature +2/+2.",
                energy_cost=2,
                effect=self.buff_effect
            ))
        for _ in range(3):
            deck.append(SpellCard(
                name="Curse",
                description="Kill a creature instantly.",
                energy_cost=3,
                effect=self.curse_effect
            ))
        for _ in range(2):
            deck.append(SpellCard(
                name="Draw +2",
                description="Draw two cards.",
                energy_cost=2,
                effect=self.draw_two_effect
            ))
        return deck

    # Spell effects
    def fireball_effect(self, game, player, target):
        if isinstance(target, CreatureCard):
            target.deal_damage(target, 5)
            game.log.append(f"{target.name} takes 5 damage.")
            if target.health <= 0:
                target.die(game)
        elif isinstance(target, Player):
            target.take_damage(5, game)

    def buff_effect(self, game, player, target):
        if isinstance(target, CreatureCard):
            target.attack += 2
            target.health += 2
            game.log.append(f"{target.name} gets +2/+2.")

    def curse_effect(self, game, player, target):
        if isinstance(target, CreatureCard):
            target.health = 0
            target.die(game)
            game.log.append(f"{target.name} is killed instantly.")

    def draw_two_effect(self, game, player, target=None):
        player.draw_card()
        player.draw_card()

    def main_game_loop(self):
        game_over = False
        while not game_over:
            current_player = self.players[self.current_turn]
            opponent = self.players[1 - self.current_turn]
            self.start_turn(current_player)
            self.player_turn(current_player, opponent)
            if opponent.hp <= 0:
                game_over = True
                clear_console()
                print(f"{current_player.name} wins!")
            else:
                self.end_turn(current_player)
                self.current_turn = 1 - self.current_turn  # Switch turns

    def start_turn(self, player):
        clear_console()
        print(f"{player.name}'s turn.")
        # Increment energy
        if player.max_energy < 7:
            player.max_energy += 1
        player.energy = player.max_energy
        # Draw a card
        player.draw_card()
        # Reset can_attack status
        for creature in player.battlefield:
            creature.can_attack = True
        # Display battlefield
        self.display_battlefield()

    def player_turn(self, player, opponent):
        while True:
            print(f"\n{player.name}'s HP: {player.hp} | Energy: {player.energy}/{player.max_energy}")
            print(f"Opponent {opponent.name}'s HP: {opponent.hp}")
            self.display_battlefield()
            player.hand.display()
            print("\nChoose an action:")
            print("1. Play a card")
            print("2. Attack")
            print("3. End turn")
            choice = input("Enter the number of your choice: ")
            if choice == '1':
                self.play_card_action(player, opponent)
            elif choice == '2':
                self.attack_action(player, opponent)
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please try again.")

    def play_card_action(self, player, opponent):
        card_name = input("Enter the name of the card to play: ")
        card_in_hand = False
        for card in player.hand.cards.to_list():
            if card.name.lower() == card_name.lower():
                card_in_hand = True
                break
        if not card_in_hand:
            print("You don't have that card in your hand.")
            return
        if player.energy < card.energy_cost:
            print("Not enough energy to play that card.")
            return
        if isinstance(card, CreatureCard):
            player.play_card(card_name, self)
            # Handle Battlecry abilities
            if 'Battlecry' in card.abilities:
                if card.name == 'Mage Apprentice':
                    target = self.select_target(player, opponent)
                    if target:
                        target.take_damage(1, self)
                elif card.name == 'Dragon':
                    for creature in opponent.battlefield:
                        creature.take_damage(2)
                        if creature.health <= 0:
                            creature.die(self)
            # Handle Goblin's ability
            if card.name == 'Goblin':
                for creature in player.battlefield:
                    if creature.name == 'Goblin' and creature != card:
                        creature.attack += 1
                        self.log.append(f"{creature.name} gains +1 Attack due to another Goblin.")
        elif isinstance(card, SpellCard):
            target = None
            if card.name != "Draw +2":
                target = self.select_target(player, opponent)
            player.play_card(card_name, self, target)

    def select_target(self, player, opponent):
        print("Select a target:")
        print("1. Opponent")
        print("2. Opponent's creatures")
        print("3. Your creatures")
        choice = input("Enter the number of your choice: ")
        if choice == '1':
            return opponent
        elif choice == '2':
            if opponent.battlefield:
                for idx, creature in enumerate(opponent.battlefield):
                    print(f"{idx + 1}. {creature.name} ({creature.attack}/{creature.health})")
                idx = int(input("Enter the number of the creature: ")) -1
                if 0 <= idx < len(opponent.battlefield):
                    return opponent.battlefield[idx]
                else:
                    print("Invalid selection.")
                    return None
            else:
                print("Opponent has no creatures.")
                return None
        elif choice == '3':
            if player.battlefield:
                for idx, creature in enumerate(player.battlefield):
                    print(f"{idx + 1}. {creature.name} ({creature.attack}/{creature.health})")
                idx = int(input("Enter the number of the creature: ")) -1
                if 0 <= idx < len(player.battlefield):
                    return player.battlefield[idx]
                else:
                    print("Invalid selection.")
                    return None
            else:
                print("You have no creatures.")
                return None
        else:
            print("Invalid choice.")
            return None

    def attack_action(self, player, opponent):
        if not player.battlefield:
            print("You have no creatures to attack with.")
            return
        for idx, creature in enumerate(player.battlefield):
            if creature.can_attack:
                print(f"{idx + 1}. {creature.name} ({creature.attack}/{creature.health})")
            else:
                print(f"{idx + 1}. {creature.name} (Cannot attack)")
        idx = int(input("Enter the number of the creature to attack with: ")) -1
        if 0 <= idx < len(player.battlefield):
            attacker = player.battlefield[idx]
            if not attacker.can_attack:
                print("This creature cannot attack this turn.")
                return
            if opponent.battlefield:
                taunt_creatures = [c for c in opponent.battlefield if c.is_taunt]
                if taunt_creatures:
                    print("Opponent has Taunt creatures. You must attack them first.")
                    for idx, creature in enumerate(taunt_creatures):
                        print(f"{idx + 1}. {creature.name} ({creature.attack}/{creature.health})")
                    target_idx = int(input("Enter the number of the creature to attack: ")) -1
                    if 0 <= target_idx < len(taunt_creatures):
                        target = taunt_creatures[target_idx]
                        attacker.attack_target(self, target)
                    else:
                        print("Invalid selection.")
                else:
                    print("Select target:")
                    print("1. Opponent")
                    print("2. Opponent's creatures")
                    target_choice = input("Enter the number of your choice: ")
                    if target_choice == '1':
                        attacker.attack_target(self, opponent)
                    elif target_choice == '2':
                        available_targets = [c for c in opponent.battlefield if not c.is_stealth]
                        if not available_targets:
                            print("No available targets to attack.")
                            return
                        for idx, creature in enumerate(available_targets):
                            print(f"{idx + 1}. {creature.name} ({creature.attack}/{creature.health})")
                        target_idx = int(input("Enter the number of the creature to attack: ")) -1
                        if 0 <= target_idx < len(available_targets):
                            target = available_targets[target_idx]
                            attacker.attack_target(self, target)
                        else:
                            print("Invalid selection.")
                    else:
                        print("Invalid choice.")
            else:
                attacker.attack_target(self, opponent)
        else:
            print("Invalid selection.")

    def end_turn(self, player):
        print(f"{player.name}'s turn has ended.")
        input("Press Enter to continue...")
        clear_console()
        self.display_log()

    def display_battlefield(self):
        print("\nBattlefield:")
        for player in self.players:
            print(f"{player.name}'s creatures:")
            if player.battlefield:
                for creature in player.battlefield:
                    status = "Ready" if creature.can_attack else "Exhausted"
                    print(f"- {creature.name} ({creature.attack}/{creature.health}) [{status}]")
            else:
                print("No creatures.")
        print("")

    def display_log(self):
        print("Game Log:")
        for entry in self.log:
            print(entry)
        self.log = []
        input("Press Enter to continue...")
        clear_console()

# Start the game
if __name__ == "__main__":
    game = Game()
    game.start_game()

