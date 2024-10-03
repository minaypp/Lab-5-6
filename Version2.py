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
        self.can_attack = 'Haste' in self.abilities
        self.is_taunt = 'Taunt' in self.abilities
        self.is_stealth = 'Stealth' in self.abilities
        self.owner = None

    def play(self, game, player, target=None):
        self.owner = player
        player.battlefield.append(self)
        game.turn_log.append(f"{player.name} played creature {self.name}.")
        game.game_log.append(f"{player.name} played creature {self.name}.")
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

# Spell Card subclass
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
        self.has_drawn_initial_hand = False  # Track if initial hand is drawn

    def draw_card(self):
        card = self.deck.draw()
        if card:
            self.hand.add_card(card)
            print(f"{self.name} draws {card.name}.")
        else:
            print(f"{self.name}'s deck is empty!")
            self.hp = 0  # Player loses if deck is empty
            print(f"{self.name} has no more cards to draw and loses the game!")

    def take_damage(self, amount, game):
        self.hp -= amount
        game.turn_log.append(f"{self.name} takes {amount} damage. HP is now {self.hp}.")
        game.game_log.append(f"{self.name} takes {amount} damage. HP is now {self.hp}.")

    def play_card(self, card_name, game, target=None):
        card = self.hand.remove_card(card_name)
        if card:
            # Check for Sorcerer Supreme effect
            if any(c.name == 'Sorcerer Supreme' for c in self.battlefield) and isinstance(card, SpellCard):
                energy_cost = 0
            else:
                energy_cost = card.energy_cost
            if self.energy >= energy_cost:
                # Attempt to play the card
                success = card.play(game, self, target)
                if success:
                    self.energy -= energy_cost
                    self.discard_pile.append(card)
                else:
                    # If card play failed, return card to hand
                    self.hand.add_card(card)
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
        self.turn_log = []  # Log for current turn
        self.game_log = []  # Log for entire game

    def start_game(self):
        clear_console()
        print("Welcome to the Python Card Game!")
        player1_name = input("Enter name for Player 1: ")
        player2_name = input("Enter name for Player 2: ")
        self.players = [Player(player1_name), Player(player2_name)]
        self.setup_players()
        # Randomly select who goes first
        self.current_turn = random.randint(0, 1)
        print(f"{self.players[self.current_turn].name} will go first.")
        input("Press Enter to start the game...")
        self.main_game_loop()

    def setup_players(self):
        for player in self.players:
            # Initialize decks with predefined cards
            deck_cards = self.create_deck()
            random.shuffle(deck_cards)
            for card in deck_cards:
                player.deck.add(card)

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
        # Add "Draw +4" Cards
        for _ in range(4):
            deck.append(SpellCard(
                name="Draw +4",
                description="Target player draws four cards.",
                energy_cost=2,
                effect=self.draw_four_effect
            ))
        # Add "End Game" Card
        deck.append(SpellCard(
            name="End Game",
            description="Deal 20 damage to any target.",
            energy_cost=0,
            effect=self.end_game_effect
        ))
        return deck

    # Spell effects
    def fireball_effect(self, game, player, target):
        if isinstance(target, CreatureCard) or isinstance(target, Player):
            target.take_damage(5, game)
            return True
        else:
            print("Invalid target for Fireball.")
            return False

    def buff_effect(self, game, player, target):
        if isinstance(target, CreatureCard):
            target.attack += 2
            target.health += 2
            game.turn_log.append(f"{target.name} gets +2/+2.")
            game.game_log.append(f"{target.name} gets +2/+2.")
            return True
        else:
            print("Buff can only target creatures.")
            return False

    def curse_effect(self, game, player, target):
        if isinstance(target, CreatureCard):
            target.take_damage(target.health, game)
            game.turn_log.append(f"{target.name} is killed instantly.")
            game.game_log.append(f"{target.name} is killed instantly.")
            return True
        else:
            print("Curse can only target creatures.")
            return False

    def draw_four_effect(self, game, player, target):
        if isinstance(target, Player):
            for _ in range(4):
                target.draw_card()
            return True
        else:
            print("Invalid target for Draw +4.")
            return False

    def end_game_effect(self, game, player, target):
        if isinstance(target, CreatureCard) or isinstance(target, Player):
            target.take_damage(20, game)
            return True
        else:
            print("Invalid target for End Game.")
            return False

    def main_game_loop(self):
        game_over = False
        while not game_over:
            current_player = self.players[self.current_turn]
            opponent = self.players[1 - self.current_turn]
            self.start_turn(current_player)
            if current_player.hp <= 0 or opponent.hp <= 0:
                game_over = True
                break
            self.player_turn(current_player, opponent)
            if current_player.hp <= 0 or opponent.hp <= 0:
                game_over = True
                break
            self.end_turn(current_player)
            self.current_turn = 1 - self.current_turn  # Switch turns
        # Determine winner
        clear_console()
        if current_player.hp <= 0 and opponent.hp <= 0:
            print("It's a draw!")
        elif current_player.hp <= 0:
            print(f"{opponent.name} wins!")
        elif opponent.hp <= 0:
            print(f"{current_player.name} wins!")
        else:
            print("Game over!")
        print("\nGame Log:")
        for entry in self.game_log:
            print(entry)

    def start_turn(self, player):
        clear_console()
        print(f"{player.name}'s turn.")
        # Draw initial hand if not already done
        if not player.has_drawn_initial_hand:
            print(f"{player.name} draws their initial hand.")
            for _ in range(5):
                player.draw_card()
            player.has_drawn_initial_hand = True
            input("Press Enter to continue...")
            clear_console()
            print(f"{player.name}'s turn.")
        # Increment energy
        if player.max_energy < 7:
            player.max_energy += 1
        player.energy = player.max_energy
        # Check for deck empty before drawing
        if player.deck.size == 0:
            player.hp = 0
            return
        # Draw a card
        player.draw_card()
        # Hand size checks
        if player.hand.cards.size == 0:
            player.take_damage(5, self)
        elif player.hand.cards.size > 7:
            player.take_damage(5, self)
        # Reset can_attack status for creatures without Haste
        for creature in player.battlefield:
            if 'Haste' not in creature.abilities:
                creature.can_attack = True
        # Display battlefield
        self.display_battlefield()

    def player_turn(self, player, opponent):
        while True:
            print(f"\n{player.name}'s HP: {player.hp} | Energy: {player.energy}/{player.max_energy}")
            print(f"{opponent.name}'s HP: {opponent.hp}")
            self.display_battlefield()
            player.hand.display()
            print("\nChoose an action:")
            print("Play a card")
            print("Attack")
            print("End turn")
            print("Quit game")
            choice = input("Type your action: ").strip().lower()
            if choice == 'play a card':
                if not player.hand.has_playable_card(player.energy):
                    print("You don't have enough energy to play any card.")
                    continue
                self.play_card_action(player, opponent)
                if player.hp <= 0 or opponent.hp <= 0:
                    break
            elif choice == 'attack':
                self.attack_action(player, opponent)
                if player.hp <= 0 or opponent.hp <= 0:
                    break
            elif choice == 'end turn':
                break
            elif choice == 'quit game':
                print(f"{player.name} has quit the game.")
                player.hp = 0
                break
            else:
                print("Invalid choice. Please try again.")

    def play_card_action(self, player, opponent):
        if player.hand.cards.size == 0:
            print("You have no cards to play.")
            return
        while True:
            card_name = input("Enter the name of the card to play (or type 'cancel' to go back): ").strip()
            if card_name.lower() == 'cancel':
                break
            card_to_play = None
            for card in player.hand.cards.to_list():
                if card.name.lower() == card_name.lower():
                    card_to_play = card
                    break
            if card_to_play is None:
                print("You don't have that card in your hand.")
                continue
            # Check for Sorcerer Supreme effect
            if any(c.name == 'Sorcerer Supreme' for c in player.battlefield) and isinstance(card_to_play, SpellCard):
                energy_cost = 0
            else:
                energy_cost = card_to_play.energy_cost
            if player.energy < energy_cost:
                print("Not enough energy to play that card.")
                continue
            target = None
            if isinstance(card_to_play, CreatureCard):
                success = card_to_play.play(self, player)
                if success:
                    player.energy -= energy_cost
                    player.discard_pile.append(card_to_play)
                    break
                else:
                    print("Failed to play the card.")
            elif isinstance(card_to_play, SpellCard):
                if card_to_play.name not in ["Draw +4"]:
                    target = self.select_target(player, opponent)
                    if target is None:
                        print("No valid target selected.")
                        continue
                else:
                    target = self.select_player(player, opponent)
                    if target is None:
                        print("No valid player selected.")
                        continue
                success = card_to_play.play(self, player, target)
                if success:
                    player.energy -= energy_cost
                    player.discard_pile.append(card_to_play)
                    break
                else:
                    print("Failed to play the card.")
            else:
                print("Invalid card type.")

    def select_target(self, player, opponent):
        while True:
            print("Select a target:")
            print("Opponent")
            print("Opponent's creatures")
            print("Your creatures")
            choice = input("Type your choice (or 'cancel' to go back): ").strip().lower()
            if choice == 'cancel':
                return None
            if choice == 'opponent':
                return opponent
            elif choice == "opponent's creatures":
                if opponent.battlefield:
                    for idx, creature in enumerate(opponent.battlefield):
                        print(f"{idx + 1}. {creature.name} ({creature.attack}/{creature.health})")
                    idx = input("Enter the number of the creature (or 'cancel' to go back): ").strip()
                    if idx.lower() == 'cancel':
                        continue
                    try:
                        idx = int(idx) - 1
                        if 0 <= idx < len(opponent.battlefield):
                            return opponent.battlefield[idx]
                        else:
                            print("Invalid selection.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                else:
                    print("Opponent has no creatures.")
            elif choice == 'your creatures':
                if player.battlefield:
                    for idx, creature in enumerate(player.battlefield):
                        print(f"{idx + 1}. {creature.name} ({creature.attack}/{creature.health})")
                    idx = input("Enter the number of the creature (or 'cancel' to go back): ").strip()
                    if idx.lower() == 'cancel':
                        continue
                    try:
                        idx = int(idx) - 1
                        if 0 <= idx < len(player.battlefield):
                            return player.battlefield[idx]
                        else:
                            print("Invalid selection.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                else:
                    print("You have no creatures.")
            else:
                print("Invalid choice.")

    def select_player(self, player, opponent):
        while True:
            print("Select a player:")
            print(f"1. {player.name}")
            print(f"2. {opponent.name}")
            choice = input("Enter the number of your choice (or 'cancel' to go back): ").strip()
            if choice.lower() == 'cancel':
                return None
            if choice == '1':
                return player
            elif choice == '2':
                return opponent
            else:
                print("Invalid choice.")

    def attack_action(self, player, opponent):
        if not player.battlefield:
            print("You have no creatures to attack with.")
            return
        attacking_creatures = [c for c in player.battlefield if c.can_attack]
        if not attacking_creatures:
            print("No creatures can attack.")
            return
        while True:
            for idx, creature in enumerate(attacking_creatures):
                print(f"{idx + 1}. {creature.name} ({creature.attack}/{creature.health})")
            choice = input("Enter the number of the creature to attack with (or type 'cancel' to go back): ").strip()
            if choice.lower() == 'cancel':
                return
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(attacking_creatures):
                    attacker = attacking_creatures[idx]
                    if opponent.battlefield:
                        self.handle_attack(attacker, opponent)
                    else:
                        attacker.attack_target(self, opponent)
                    break  # After attack, break out of the loop
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def handle_attack(self, attacker, opponent):
        while True:
            taunt_creatures = [c for c in opponent.battlefield if c.is_taunt]
            if taunt_creatures:
                print("Opponent has Taunt creatures. You must attack them first.")
                for idx, creature in enumerate(taunt_creatures):
                    print(f"{idx + 1}. {creature.name} ({creature.attack}/{creature.health})")
                choice = input("Enter the number of the creature to attack (or 'cancel' to go back): ").strip()
                if choice.lower() == 'cancel':
                    return
                try:
                    target_idx = int(choice) - 1
                    if 0 <= target_idx < len(taunt_creatures):
                        target = taunt_creatures[target_idx]
                        attacker.attack_target(self, target)
                        return
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            else:
                print("Select target:")
                print("Opponent")
                print("Opponent's creatures")
                target_choice = input("Type your choice (or 'cancel' to go back): ").strip().lower()
                if target_choice == 'cancel':
                    return
                if target_choice == 'opponent':
                    attacker.attack_target(self, opponent)
                    return
                elif target_choice == "opponent's creatures":
                    available_targets = [c for c in opponent.battlefield if not c.is_stealth]
                    if not available_targets:
                        print("No available targets to attack.")
                        return
                    for idx, creature in enumerate(available_targets):
                        print(f"{idx + 1}. {creature.name} ({creature.attack}/{creature.health})")
                    choice = input("Enter the number of the creature to attack (or 'cancel' to go back): ").strip()
                    if choice.lower() == 'cancel':
                        continue
                    try:
                        target_idx = int(choice) - 1
                        if 0 <= target_idx < len(available_targets):
                            target = available_targets[target_idx]
                            attacker.attack_target(self, target)
                            return
                        else:
                            print("Invalid selection.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                else:
                    print("Invalid choice.")

    def end_turn(self, player):
        print(f"{player.name}'s turn has ended.")
        print("\nTurn Log:")
        for entry in self.turn_log:
            print(entry)
        self.turn_log = []  # Clear the turn log
        input("Press Enter to continue...")
        clear_console()

    def display_battlefield(self):
        print("\nBattlefield:")
        for p in self.players:
            print(f"{p.name}'s creatures:")
            if p.battlefield:
                for creature in p.battlefield:
                    status = "Ready" if creature.can_attack else "Exhausted"
                    print(f"- {creature.name} ({creature.attack}/{creature.health}) [{status}]")
            else:
                print("No creatures.")
        print("")

    def display_log(self):
        print("Game Log:")
        for entry in self.game_log:
            print(entry)
        self.game_log = []
        input("Press Enter to continue...")
        clear_console()

# Start the game
if __name__ == "__main__":
    game = Game()
    game.start_game()
