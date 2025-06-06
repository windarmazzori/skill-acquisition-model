import numpy as np
import skills

class Monster:
    def __init__(self, hp, combat_skill_name):
        """
        Paramters:
        - hp: An integer containing the hp the monster will have
        - combat_skill_name: A string containing the name of the skill used by the monster,
        not used in any way except for printing.
        """
        self.hp = hp
        self.combat_skill_name = combat_skill_name

    def take_damage(self, damage):
        """
        Handles damage taken by the monster.
        """
        self.hp -= int(damage)
        print(f"The monster takes {int(damage)} damage! HP remaining: {self.hp}")

    def is_defeated(self):
        """
        Checks if the monster is alive.
        """
        return self.hp <= 0

class Player:
    def __init__(self, name):
        """
        Parameter:
        - name: The player's name

        Side effects:
        - Adds default attributes to skill list, initializes all skills as beginner.
        Set its own hp and maxhp to 10, maxhp only increasing based on endurance. Keeps
        track of which combat skill the player has.
        """
        self.name = name
        self.skills = {
            "Strength": skills.Attribute(1),
            "Dexterity": skills.Attribute(1),
            "Intelligence": skills.Attribute(1),
            "Endurance": skills.Attribute(1) 
        }
        self.skill_rankings = {name : "beginner" for name in self.skills.keys()}
        self.combat_skills = []
        self.rankings_to_level = {
                      "beginner": 0, 
                      "amateur": 15,
                      "intermediate": 30,
                      "seasoned": 45,
                      "advanced": 60,
                      "expert": 75,
                      "professional": 90
                      }
        self.hp = 10
        self.maxhp = 10
        self.rank = "beginner"
        self.money = 0

    def skill_check(self, skill_name, rank):
        """
        Performs a skill check on a given name on a given rank

        Input:
        - skill_name: String containing the name of the skill
        - rank: String containing the rank at which the skill is practiced at.

        Output: 
        - The results of the skill check

        Side effects:
        - If the player performs a skill at a higher rank than they are currently at,
        and performs a critical success, the rank of that skill will increase accordingly.
        If the increasing skill is endurance, the player's max hp will increase.
        Additionally prints the result (in the form of "critical success", "success",
        "failure", or "critical failure") to stdout.
        """
        if skill_name in self.skills:
            level = self.rankings_to_level[rank]
            result = self.skills[skill_name].check(level)
            print(f"\n{self.name} attempts a {skill_name} skill check at {rank} level...")
            if result >= level + 2:
                print("Critical success!")
                # A critical success at a higher rank should mean the player is at that rank
                if self.rankings_to_level[self.skill_rankings[skill_name]] < self.rankings_to_level[rank]:
                    self.skill_rankings[skill_name] = rank
                    if skill_name == "Endurance":
                        self.maxhp += 20
                        self.hp = self.maxhp
                    print(f"Your mastery over {skill_name} improved! You are now at {rank} level.")
            elif result >= level:
                print("Success.")
            elif result < level:
                print("Failure.")
            elif result < level - 2:
                print("Critical failure!")
            return result
        else:
            print(f"\n{self.name} has not learned {skill_name} yet!")

    def learn_skill(self, skill_name, skill, combat=True):
        """
        Lets a player learn a given skill

        Input: 
        - skill_name: String containing the skill name to be learned
        - skill: skills.Skill object of the skill that will be learned
        - combat: A boolean denoting if the given skill is a combat skill or not. Defaults
        to True.

        Side effects:
        - Adds the skill to self.skills and self.skill_rankings and self.combat_skills,
        should combat=True.
        """
        if skill_name in self.skills:
            print(f"\n{self.name} has already learned {skill_name}!")
        else:
            self.skills[skill_name] = skill
            self.skill_rankings[skill_name] = "beginner"
            if combat:
                self.combat_skills.append(skill_name)
            print(f"\n{self.name} learned {skill_name}!")

    def train_skill(self, skill_name, rank):
        """
        Attempts to practice a certain skill

        Input:
        - skill_name: String containing the name of the skill to be trained.
        - rank: The target rank the player wishes to achieve.

        Side effects:
        - Calls skill_check() to perform the skill check.
        """
        if skill_name in self.skills:
            print(f"\nTraining {skill_name}...")
            self.skill_check(skill_name, rank)
        else:
            print(f"\nYou haven't learned {skill_name} yet!")

    def fight_monster(self):
        """ 
        Performs combat against a monster. The monster spawned is based on the player's
        stats.

        Enters a gameplay loop where the player can choose to fight, defend or flee. These
        actions all depend on attributes or skills the player has.
        """
        if not self.combat_skills:
            print("\nYou don't know how to fight yet! The monster attacks!")
            self.hp -= 3
            if self.hp <= 0:
                print("\nYou have fallen in battle... Game Over.")
                exit()
            return
        
        # Monster will be the rank of the player, one below or one above
        monster_level = min(max(0, self.rankings_to_level[self.rank] + np.random.choice([-15, 0, 15])), 90)
        monster_hp = (monster_level + 1) * 2
        monster = Monster(hp=monster_hp, combat_skill_name=np.random.choice(self.combat_skills))

        # Get the monster rank based on the level.
        monster_rank = [key for key, val in self.rankings_to_level.items() if val == monster_level][0]
        print(f"\nA monster of {monster_rank} rank with {monster.hp} HP appears, using {monster.combat_skill_name}!")

        while self.hp > 0 and not monster.is_defeated():
            print("\nYour turn!")
            print("1. Attack")
            print("2. Defend")
            print("3. Flee")
            action = input("Choose an action: ")

            if action == "1":
                # Handle attacks
                print("What skill would you like to attack with?")
                [print(f"{i}) {skill_name}") for i, skill_name in enumerate(self.combat_skills)]
                while True:
                    attack = input("Input a number for the skill you want to use: ")
                    try:
                        attack = int(attack)
                        if attack < 0 or attack >= len(self.combat_skills):
                            raise ValueError
                        break
                    except ValueError:
                        print("Please input a valid number")
                damage = self.skill_check(self.combat_skills[attack], monster_rank)
                monster.take_damage(damage)
            elif action == "2":
                # Handle defense
                block_amount = self.skills["Endurance"].check(monster_level) // 2
                reduced_damage = max(0, np.random.randint(0, monster_level + 1) - block_amount)
                self.hp -= reduced_damage
                print(f"\nYou brace yourself, reducing damage by {block_amount}! Incoming damage: {reduced_damage}")
                print(f"You have {self.hp} remaining HP.")
            elif action == "3":
                # Handle fleeing (only possible if the player has the stealth skill)
                print("\nYou attempt to sneak away...")
                if not "stealth" in self.skills:
                    print("But you have not learned stealth yet!")
                    continue
                escape_chance = self.skill_check("stealth", monster_rank)
                if escape_chance >= monster_level:
                    print("You successfully escape!")
                    return
                elif escape_chance < monster_level:
                    print("Failed to escape! The monster gets attack you!")
                    block_amount = self.skills["Endurance"].get_mean() // 2
                    reduced_damage = max(0, np.random.randint(1, monster_level + 1) - block_amount)
                    self.hp -= reduced_damage
                    print(f"\nYou take {reduced_damage} damage")
                    print(f"You have {self.hp} remaining HP.")
            else:
                print("Invalid action")


        if monster.is_defeated():
            money_earned = np.random.randint((1+self.rankings_to_level[monster_rank]) // 2,
                                             1+self.rankings_to_level[monster_rank])
            print("\nYou have defeated the monster!")
            print(f"You gained {money_earned} money!")
            self.money += money_earned


def main():
    player_name = input("Enter your name: ")
    player = Player(player_name)

    # Define combat skills dependent on attributes
    archery_skill = skills.Composite(ancestors={
        player.skills["Dexterity"]: 1.2,
        player.skills["Strength"]: 0.5}, exp=20)
    swordsmanship_skill = skills.Composite(ancestors={
        player.skills["Strength"]: 1.2,
        player.skills["Dexterity"]: 0.5}, exp=20)
    magic_skill = skills.Composite(ancestors={
        player.skills["Intelligence"]: 1.1,
        player.skills["Dexterity"]: 0.4}, exp=20)
    stealth_skill = skills.Composite(ancestors={
        player.skills["Dexterity"]: 1.4,
        player.skills["Intelligence"]: 0.3}, exp=20)
    
    learnable_skills = [("Archery", archery_skill), 
                        ("Swordsmanship", swordsmanship_skill),
                        ("Magic", magic_skill),
                        ("Stealth", stealth_skill)]

    while True:
        print("\n" + ("-" * 26))
        print("What would you like to do?")
        print("1. Learn a skill")
        print("2. Train a skill")
        print("3. Fight a monster")
        print("4. Rest")
        print("5. Check status")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            # Learning a skill
            while True:
                [print(f"{i+1}: {skill_name}") for i, (skill_name, _) in enumerate(learnable_skills)]
                skill_num = input("\nChoose a skill (input a number):")
                try:
                    skill_num = int(skill_num)
                    break
                except ValueError:
                    print("Not a number.")
            if skill_num <= len(learnable_skills) and int(skill_num) > 0:
                skill_name = learnable_skills[skill_num-1][0]
                skill = learnable_skills[skill_num-1][1]
                combat = True
                if skill_name == "Stealth":
                    combat = False
                player.learn_skill(skill_name, skill, combat=combat)
            else:
                print("Unknown skill.")
        elif choice == "2":
            # Training a skill
            while True:
                [print(f"{i}: {name}") for i, name in enumerate(player.skills.keys())]
                skill_name = input("\nEnter skill to train (enter a number): ")
                try:
                    skill_name = int(skill_name)
                    if skill_name < 0 or skill_name >= len(player.skills.keys()):
                        raise ValueError
                    break
                except ValueError:
                    print("Please input a valid number.")
            while True:
                [print(f"{i}: {rank}") for i, rank in enumerate(player.rankings_to_level.keys())]
                rank_num = input("Enter the skill rank to train at (enter a number): ")
                try:
                    rank_num = int(rank_num)
                    break
                except ValueError:
                    print("Invalid input. Please enter a valid number.")

            player.train_skill(list(player.skills.keys())[skill_name],
                               list(player.rankings_to_level.keys())[rank_num])
        elif choice == "3":
            # Fighting a monster
            player.fight_monster()
            if player.hp <= 0:
                print("\nYou died in combat...")
                break
        elif choice == "4":
            # Resting at an inn
            if player.money > 10:
                print("\nYou rest at the inn for the day and wake up revitalized.")
                print("10 HP restored!")
                player.hp += 10
                player.money -= 10
            else:
                print("\nYou do not have enough money to rest at the inn")
                print(f"you have {player.money} and you need at least 10.")
        elif choice == "5":
            # Player status
            print(f"\n{player.name}'s Status:")
            print(f"HP: {player.hp}")
            for skill, rank in player.skill_rankings.items():
                print(f"{skill}: {rank}")
        elif choice == "6":
            # Exiting
            print("\nExiting")
            break
        else:
            print("\nInvalid choice")

if __name__ == "__main__":
    main()
