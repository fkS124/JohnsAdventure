import json

from .quest import Quest


class QuestManager:

    def __init__(self, game_instance, player):
        self.game_instance = game_instance
        self.player = player

        self.quests: dict[str: Quest] = {}
        self.load_quests()

    def load_quests(self):
        with open("data/scripts/QUESTS/quests.json", "r") as quests:
            data = json.load(quests)

        for key in data:
            self.quests[key] = Quest(key, data[key]["xp"], self.player)

    def get_current_level_tag(self):
        for tag, state_type in self.game_instance.state_manager.items():
            if type(self.game_instance.game_state) is state_type:
                return tag

    def update_quests(self):

        for quest in self.quests.values():
            if quest.finished:
                continue

            # print(self.get_current_level_tag(), quest.type_step, quest.level_step, quest.target_step, self.player.interacting_with.__class__.__name__, quest.target_step)

            if self.get_current_level_tag() == quest.level_step:
                if quest.type_step == "Reach":
                    quest.complete_step()
                elif quest.type_step == "Interact":
                    if self.player.interacting_with.__class__.__name__ == quest.target_step:
                        quest.complete_step()
                elif quest.type_step == "Kill":
                    for obj in self.game_instance.game_state.objects:
                        if obj.__class__.__name__ == quest.target_step:
                            break
                    else:
                        quest.complete_step()
