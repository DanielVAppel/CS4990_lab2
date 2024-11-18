from hanabi import *
import util
import agent
import numpy as np
import random

class InnerStatePlayer(agent.Agent):
    def __init__(self, name, pnr):
        self.name = name
        self.explanation = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints, hits, cards_left):
        my_knowledge = knowledge[nr]
        
        potential_discards = []
        for i,k in enumerate(my_knowledge):
            if util.is_playable(k, board):
                return Action(PLAY, card_index=i)
            if util.is_useless(k, board):    
                potential_discards.append(i)
                
        if potential_discards:
            return Action(DISCARD, card_index=random.choice(potential_discards))

        if hints > 0:
            for player,hand in enumerate(hands):
                if player != nr:
                    for card_index,card in enumerate(hand):
                        if card.is_playable(board):                              
                            if random.random() < 0.5:
                                return Action(HINT_COLOR, player=player, color=card.color)
                            return Action(HINT_RANK, player=player, rank=card.rank)

            hints = util.filter_actions(HINT_COLOR, valid_actions) + util.filter_actions(HINT_RANK, valid_actions)
            return random.choice(hints)

        return random.choice(util.filter_actions(DISCARD, valid_actions))
        
def format_hint(h):
    if h == HINT_COLOR:
        return "color"
    return "rank"
        
class OuterStatePlayer(agent.Agent):
    def __init__(self, name, pnr):
        self.name = name
        self.hints = {}
        self.pnr = pnr
        self.explanation = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints, hits, cards_left):
        for player,hand in enumerate(hands):
            for card_index,_ in enumerate(hand):
                if (player,card_index) not in self.hints:
                    self.hints[(player,card_index)] = set()
        known = [""]*5
        for h in self.hints:
            pnr, card_index = h 
            if pnr != nr:
                known[card_index] = str(list(map(format_hint, self.hints[h])))
        self.explanation = [["hints received:"] + known]

        my_knowledge = knowledge[nr]
        
        potential_discards = []
        for i,k in enumerate(my_knowledge):
            if util.is_playable(k, board):
                return Action(PLAY, card_index=i)
            if util.is_useless(k, board):    
                potential_discards.append(i)
                
        if potential_discards:
            return Action(DISCARD, card_index=random.choice(potential_discards))
         
        playables = []        
        for player,hand in enumerate(hands):
            if player != nr:
                for card_index,card in enumerate(hand):
                    if card.is_playable(board):                              
                        playables.append((player,card_index))
        
        playables.sort(key=lambda which: -hands[which[0]][which[1]].rank)
        while playables and hints > 0:
            player,card_index = playables[0]
            knows_rank = True
            real_color = hands[player][card_index].color
            real_rank = hands[player][card_index].rank
            k = knowledge[player][card_index]
            
            hinttype = [HINT_COLOR, HINT_RANK]
            
            
            for h in self.hints[(player,card_index)]:
                hinttype.remove(h)
            
            t = None
            if hinttype:
                t = random.choice(hinttype)
            
            if t == HINT_RANK:
                for i,card in enumerate(hands[player]):
                    if card.rank == hands[player][card_index].rank:
                        self.hints[(player,i)].add(HINT_RANK)
                return Action(HINT_RANK, player=player, rank=hands[player][card_index].rank)
            if t == HINT_COLOR:
                for i,card in enumerate(hands[player]):
                    if card.color == hands[player][card_index].color:
                        self.hints[(player,i)].add(HINT_COLOR)
                return Action(HINT_COLOR, player=player, color=hands[player][card_index].color)
            
            playables = playables[1:]
 
        if hints > 0:
            hints = util.filter_actions(HINT_COLOR, valid_actions) + util.filter_actions(HINT_RANK, valid_actions)
            hintgiven = random.choice(hints)
            if hintgiven.type == HINT_COLOR:
                for i,card in enumerate(hands[hintgiven.player]):
                    if card.color == hintgiven.color:
                        self.hints[(hintgiven.player,i)].add(HINT_COLOR)
            else:
                for i,card in enumerate(hands[hintgiven.player]):
                    if card.rank == hintgiven.rank:
                        self.hints[(hintgiven.player,i)].add(HINT_RANK)
                
            return hintgiven

        return random.choice(util.filter_actions(DISCARD, valid_actions))

    def inform(self, action, player):
        if action.type in [PLAY, DISCARD]:
            if (player,action.card_index) in self.hints:
                self.hints[(player,action.card_index)] = set()
            for i in range(5):
                if (player,action.card_index+i+1) in self.hints:
                    self.hints[(player,action.card_index+i)] = self.hints[(player,action.card_index+i+1)]
                    self.hints[(player,action.card_index+i+1)] = set()

class myAgent(agent.Agent):
    def __init__(self, name, pnr):
        self.name = name
        self.hints = {}
        self.pnr = pnr
        self.explanation = []

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints, hits, cards_left):
        for player, hand in enumerate(hands):
            for card_index, _ in enumerate(hand):
                if (player, card_index) not in self.hints:
                    self.hints[(player, card_index)] = set()
        known = [""] * 5
        for h in self.hints:
            pnr, card_index = h
            if pnr != nr:
                known[card_index] = str(list(map(format_hint, self.hints[h])))
        self.explanation = [["hints received:"] + known]

        my_knowledge = knowledge[nr]
        potential_discards = []

        for i, k in enumerate(my_knowledge):
            if util.is_playable(k, board):
                return Action(PLAY, card_index=i)
            if util.is_useless(k, board):
                potential_discards.append(i)

        if potential_discards:
            return Action(DISCARD, card_index=random.choice(potential_discards))

        playables = []
        for player, hand in enumerate(hands):
            if player != nr:
                for card_index, card in enumerate(hand):
                    if card.is_playable(board):
                        playables.append((player, card_index))


        playables.sort(key=lambda which: -hands[which[0]][which[1]].rank)
        while playables and hints > 0:
            player, card_index = playables[0]
            knows_rank = True
            real_color = hands[player][card_index].color
            real_rank = hands[player][card_index].rank
            k = knowledge[player][card_index]

            hinttype = [HINT_COLOR, HINT_RANK]

            for h in self.hints[(player, card_index)]:
                hinttype.remove(h)

            t = None
            if hinttype:
                t = random.choice(hinttype)

            if t == HINT_RANK and util.is_playable(k, board):
                for i, card in enumerate(hands[player]):
                    if card.rank == hands[player][card_index].rank:
                        self.hints[(player, i)].add(HINT_RANK)
                return Action(HINT_RANK, player=player, rank=hands[player][card_index].rank)
            if t == HINT_COLOR and util.is_playable(k, board):
                for i, card in enumerate(hands[player]):
                    if card.color == hands[player][card_index].color:
                        self.hints[(player, i)].add(HINT_COLOR)
                return Action(HINT_COLOR, player=player, color=hands[player][card_index].color)

            if t == HINT_RANK:
                for i, card in enumerate(hands[player]):
                    if card.rank == hands[player][card_index].rank:
                        self.hints[(player, i)].add(HINT_RANK)
                return Action(HINT_RANK, player=player, rank=hands[player][card_index].rank)
            if t == HINT_COLOR:
                for i, card in enumerate(hands[player]):
                    if card.color == hands[player][card_index].color:
                        self.hints[(player, i)].add(HINT_COLOR)
                return Action(HINT_COLOR, player=player, color=hands[player][card_index].color)

            playables = playables[1:]

            # Finesse Strategy
            for player, hand in enumerate(hands):
                if player != nr:
                    for card_index, card in enumerate(hand):
                        if util.is_playable(knowledge[player][card_index], board):
                            # Give a hint that indirectly suggests playability
                            if hints > 0:
                                if any(action.type == HINT_COLOR for action in valid_actions):
                                    return Action(HINT_COLOR, player=player, color=card.color)
                                elif any(action.type == HINT_RANK for action in valid_actions):
                                    return Action(HINT_RANK, player=player, rank=card.rank)

            # Reverse Finesse Strategy
            for player, hand in enumerate(hands):
                if player != nr:
                    for card_index, card in enumerate(hand):
                        if util.maybe_playable(knowledge[player][card_index], board):
                            # Give a hint that another player can interpret
                            if hints > 0:
                                if any(action.type == HINT_COLOR for action in valid_actions):
                                    return Action(HINT_COLOR, player=player, color=card.color)
                                elif any(action.type == HINT_RANK for action in valid_actions):
                                    return Action(HINT_RANK, player=player, rank=card.rank)

            # Enhanced Hint Logic
            if hints > 0:
                # Prioritize hints that apply to multiple cards
                for player, hand in enumerate(hands):
                    if player != nr:
                        color_counts = {}
                        rank_counts = {}
                        for card_index, card in enumerate(hand):
                            color_counts[card.color] = color_counts.get(card.color, 0) + 1
                            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1

                        # Find the most common color and rank
                        most_common_color = max(color_counts, key=color_counts.get)
                        most_common_rank = max(rank_counts, key=rank_counts.get)

                        # Give a hint about the most common color or rank
                        if color_counts[most_common_color] > 1:
                            if any(action.type == HINT_COLOR for action in valid_actions):
                                return Action(HINT_COLOR, player=player, color=most_common_color)
                        if rank_counts[most_common_rank] > 1:
                            if any(action.type == HINT_RANK for action in valid_actions):
                                return Action(HINT_RANK, player=player, rank=most_common_rank)

        return random.choice(util.filter_actions(DISCARD, valid_actions))

    def inform(self, action, player):
        if action.type in [PLAY, DISCARD]:
            if (player, action.card_index) in self.hints:
                self.hints[(player, action.card_index)] = set()
            for i in range(5):
                if (player, action.card_index + i + 1) in self.hints:
                    self.hints[(player, action.card_index + i)] = self.hints[(player, action.card_index + i + 1)]
                    self.hints[(player, action.card_index + i + 1)] = set()


agent.register("inner", "Inner State Player", InnerStatePlayer)
agent.register("outer", "Outer State Player", OuterStatePlayer)
agent.register("mine", "My agent", myAgent)
