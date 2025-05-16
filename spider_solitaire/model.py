# model.py Model for spider solitaire

import random
import itertools
import pickle
import datetime
from collections import namedtuple
import json
import os
from typing import List, Tuple

ACE = 1
JACK = 11
QUEEN = 12
KING = 13
ALLRANKS = range(1, 14)      # one more than the highest value

# Only includes 'spade'
SUITNAMES = ('spade',)
RANKNAMES = ["", "Ace"] + list(map(str, range(2, 11))) + ["Jack", "Queen", "King"]
# Only includes 'blue'
COLORNAMES = ("blue",)     # back colors

# DEAL constant remains as (0, 0, 10, 0) representing a dealing operation
DEAL = (0, 0, 10, 0)     # used in undo/redo stacks

class Stack(list):
    '''
    A pile of cards.
    The base class deals with the essential facilities of a stack, and the derived 
    classes deal with presentation.
    '''
    def __init__(self):
        super().__init__()
            
    def add(self, card, faceUp=True):
        self.append(card)
        if faceUp:
            self[-1].showFace()
            
    def isEmpty(self):
        return not self
            
    def clear(self):
        self[:] = []  
          
    def find(self, code):
        '''
        If the card with the given code is in the stack,
        return its index.  If not, return -1.
        '''
        for idx, card in enumerate(self):
            if card.code == code:
                return idx
        return -1
            
class SelectableStack(Stack):
    '''
    A stack from which cards can be chosen, if they are face up and in sequence,
    from the top of the stack.  When cards are removed, the top card is automatically
    turned up, if it is not already face up.
    '''
    def __init__(self):
        super().__init__()
        
    def grab(self, n):
        '''
        Remove the card at index n and all those on top of it.
        '''    
        answer = self[n:]
        del self[n:]
        return answer
            
    def replace(self, cards):
        '''
        Move aborted.  Replace these cards on the stack.
        '''
        self.extend(cards)
        self.moving = None
            
    def canSelect(self, idx):
        if idx >= len(self):
            return False
        if self[idx].faceDown():
            return False
        if not Card.isDescending(self[idx:]):
            return False
        return True
          
class OneWayStack(Stack):
    '''
    Used for the stock and the foundations.
    No cards can be selected.
    Cards are either all face up, or all face down.
    '''
    def __init__(self, faceUp):
        super().__init__()
        self.faceUp = faceUp
        
    def add(self, card):
        super().add(card, self.faceUp)

class Card:
    '''
    A card is identified by its rank, suit, and back color.
    A card knows whether it is face up or down, but does not know 
    which stack it is in.
    '''
    circular = False
    def __init__(self, rank, suit, back, code):
        self.rank = rank
        self.suit = suit
        self.back = back
        self.up = False   # all cards are initially face down
        self.code = code  
    
    def showFace(self):
        self.up = True
        
    def showBack(self):
        self.up = False
        
    def faceUp(self):
        return self.up
          
    def faceDown(self):
        return not self.faceUp()
      
    # Overloaded operators for predecessor and successor
    
    def __lt__(self, other):
        if self.suit != other.suit:
            return False
        answer = (self.rank == other.rank - 1 or 
                  (self.circular and self.rank == KING and other.rank == ACE))
        return answer 
    
    def __gt__(self, other):
        return other < self
      
    def __repr__(self):
        return f'{self.suit} {RANKNAMES[self.rank]} {self.back}'
      
    def __str__(self):
        return self.__repr__()
      
    @staticmethod
    def isDescending(seq):
        '''
        Are the cards in a descending sequence of the same suit?
        '''
        return all(x > y for x, y in zip(seq, seq[1:]))  
    

class Model:
    '''
    The cards are all in self.deck, and are copied into the appropriate stacks:
        the stock
        waste piles, where all the action is
        foundation piles for completed suits
    All entries on the undo and redo stacks are in the form (source, target, n, f), where
        waste piles are numbered 0 to (num_waste-1) and foundations 10 to (10 + 7)
        n is the number of cards moved, and f is a boolean indicating whether or not the top
        card of the source stack is flipped, except that the entry (0, 0, 10, 0) connotes 
        dealing a row of cards. 
    '''
    def __init__(self, num_waste=10):
        random.seed()
        self.deck = []
        self.selection = []
        self.undoStack = []
        self.redoStack = []
        self.circular = False  # Initialize to prevent AttributeError
        self.open = False      # Initialize to prevent AttributeError
        self.num_waste = num_waste
        self.createCards()
        self.stock = OneWayStack(False)
        self.foundations = [OneWayStack(True) for _ in range(8)]
        self.waste = [SelectableStack() for _ in range(self.num_waste)]
        self.deal()
        
    def shuffle(self):
        self.stock.clear()
        for f in self.foundations:
            f.clear()
        for w in self.waste:
            w.clear()
        random.shuffle(self.deck)
        for card in self.deck:
            card.showBack()
        self.stock.extend(self.deck)
          
    def createCards(self):
        code = 0
        for _ in range(8):  # 8 decks, ensuring a total of 104 cards
            for rank in ALLRANKS:
                suit = 'spade'
                back = 'blue'
                self.deck.append(Card(rank, suit, back, code))
                code += 1
        print(f"Total cards in deck after creation: {len(self.deck)}")  # Should output 104
    
    def reset(self, circular, open):
        self.circular = Card.circular = circular
        self.open = open    
    
    def deal(self, circular=False, open=False):
        self.reset(circular, open)
        self.shuffle()
        self.dealDown()
        self.dealUp()
        self.undoStack = []
        self.redoStack = []    
        self.statsSaved = False    
    
    def adjustOpen(self, up):
        '''
        Adjust the open mode if the user changes the option
        '''
        self.open = up
        for w in self.waste:
            for card in w[:-1]:
                if up:
                    card.showFace()
                else:
                    card.showBack()
                    
    def dealDown(self):
        '''
        Deal the face down cards into the initial layout, unless the
        user has specified open spider.
        '''
        # Calculate the total initial number of face-down cards based on num_waste
        total_face_down = max(104 - self.num_waste * 6, 0)
        
        for n in range(total_face_down):
            if not self.stock:
                print(f"Stock is empty while dealing down at card index {n}")
                continue
            card = self.stock.pop()
            # Correct the faceUp parameter: when open=False, faceUp=False (face down)
            # when open=True, faceUp=True (face up)
            self.waste[n % self.num_waste].add(card, faceUp=self.open)
        print("After dealDown:")
        for i, w in enumerate(self.waste):
            print(f"Waste {i}: {len(w)} cards")
    
    def dealUp(self, redo=False):
        '''
        Deal one row of face up cards
        redo is True if we are redoing a deal
        '''
        for n in range(self.num_waste):
            if not self.stock:
                print(f"Stock is empty while dealing up at card index {n}")
                continue
            card = self.stock.pop()
            self.waste[n].add(card, True)
        if not redo:
            # Use (0, 0, 10, 0) as the DEAL record
            DEAL_RECORD = DEAL
            self.undoStack.append(DEAL_RECORD)
            self.redoStack = []
        print("After dealUp:")
        for i, w in enumerate(self.waste):
            print(f"Waste {i}: {len(w)} cards")
        print(f"Stock has {len(self.stock)} cards remaining.")
          
    def canDeal(self):
        '''
        Face up cards can be dealt only if no waste pile is empty
        '''
        return all(not w.isEmpty() for w in self.waste)
             
    def gameWon(self):
        '''
        The game is won when all foundation piles are used
        '''
        return all(len(f) == 13 for f in self.foundations)
    
    # Ensure that the downUp method exists and works correctly
    def downUp(self, pile_index: int) -> Tuple[int, int]:
        """
        Returns a tuple containing the number of face-down and face-up cards in the specified waste pile.
        """
        pile = self.waste[pile_index]
        down = sum(1 for card in pile if card.faceDown())
        up = len(pile) - down
        return down, up
      
    def grab(self, k, idx):
        '''
        Initiate a move between waste 
        Grab card at index idx and those on top of it from waste pile k
        Return the selected cards.
        We need to remember the data, since the move may fail.
        '''
        w = self.waste[k]
        if not w.canSelect(idx):
            return []
        self.moveOrigin = k
        self.moveIndex = idx
        self.selection = w[idx:]
        return self.selection
      
    def abortMove(self):
        self.selection = []
        
    def moving(self):
        return bool(self.selection)
      
    def getSelected(self):
        return self.selection
      
    def canDrop(self, k):
        '''
        Can the moving cards be dropped on waste pile k?
        '''
        dest = self.waste[k]
        source = self.selection
        
        if not source:
            return False
        if dest.isEmpty():      # can always drop on empty pile
            return True
        if dest[-1].rank - source[0].rank == 1:  
            return True       # e.g. can drop a 4 on a 5
        if self.circular:   # can place King on ACE
            return dest[-1].rank == ACE and source[0].rank == KING
        return False
          
    def completeMove(self, dest):
        '''
        Complete a legal move.
        Transfer the moving cards to the destination stack.
        Turn the top card of the source stack face up, if need be.
        '''
        source = self.waste[self.moveOrigin]
        target = self.waste[dest] if dest < self.num_waste else self.foundations[dest - self.num_waste]

        # If it is moved to the foundation pile, verify that the sequence is complete
        if dest >= self.num_waste:
            if len(self.selection) != 13:
                print("Error: Attempted to move a non-complete sequence to foundation.")
                return  # or trigger an error
            # Check that all cards are in descending order and of the same suit
            if not Card.isDescending(self.selection):
                print("Error: Attempted to move a non-descending sequence to foundation.")
                return
            suit = self.selection[0].suit
            if any(card.suit != suit for card in self.selection):
                print("Error: Attempted to move a sequence with mixed suits to foundation.")
                return

        target.extend(self.selection)
        del source[self.moveIndex:]
        self.undoStack.append(self.flipTop(self.moveOrigin, dest, len(self.selection)))
        self.selection = []
        self.redoStack = []
        
    def selectionToFoundation(self, dest):
        '''
        Complete a legal move to foundation pile
        '''
        self.completeMove(dest + self.num_waste)
        
    def selectionToWaste(self, dest):
        '''
        Complete a legal move to waste pile
        '''
        self.completeMove(dest)  
            
    def completeSuit(self, pile):
        '''
        Does the pile have a complete suit, face up, sorted from King 
        downwards, on top?
        '''
        w = self.waste[pile]
        if len(w) < 13 or w[-13].faceDown():
            return False
        return Card.isDescending(w[-13:])
      
    def firstFoundation(self):
        # return index of first empty foundation pile
        for i, f in enumerate(self.foundations):
            if f.isEmpty(): return i    
      
    def flipTop(self, src, dest, n):
        '''
        Turn the top card of waste pile src face up, if need be
        Return appropriate undo tuple
        '''
        w = self.waste[src]
        flip = w and w[-1].faceDown()
        if flip:
            w[-1].showFace()
        return (src, dest, n, flip)
      
    def movingCompleteSuit(self):
        return len(self.selection) == 13
        
    def win(self):
        return all(len(f) == 13 for f in self.foundations)
      
    def undo(self):
        ''''
        Pop a record off the undo stack and undo the corresponding move.
        '''
        if not self.undoStack:
            return
        record = self.undoStack.pop()
        self.redoStack.append(record)
        s, t, n, f = record
        if record == DEAL:
            self.undeal()
        else:
            if f:   # flip top card back
                self.waste[s][-1].showBack()
            source = self.waste[s] if s < self.num_waste else self.foundations[s - self.num_waste]
            target = self.waste[t] if t < self.num_waste else self.foundations[t - self.num_waste]
            moved_cards = target[-n:]
            del target[-n:]
            source.extend(moved_cards)
        
    def undeal(self):
        '''
        Undo a deal of a row of cards
        '''
        for w in reversed(self.waste):
            if w:
                card = w.pop()
                card.showBack()
                self.stock.append(card)
    
    def redo(self):
        ''''
        Pop a record off the redo stack and redo the corresponding move.
        ''' 
        if not self.redoStack:
            return
        record = self.redoStack.pop()
        self.undoStack.append(record)
        s, t, n, f = record
        if record == DEAL:
            self.dealUp(True) 
        else:
            source = self.waste[s] if s < self.num_waste else self.foundations[s - self.num_waste]
            target = self.waste[t] if t < self.num_waste else self.foundations[t - self.num_waste]
            moved_cards = source[-n:]
            del source[-n:]
            target.extend(moved_cards)     
            if f and s < self.num_waste:  # flip top card face up
                self.waste[s][-1].showFace()
                
    def canUndo(self):
        return bool(self.undoStack)
      
    def canRedo(self):
        return bool(self.redoStack)  
        
    def save(self, filename):
        with open(filename, 'wb') as fn:
            pickle.dump((
                self.deck, 
                self.undoStack, 
                self.redoStack, 
                self.stock, 
                self.foundations,
                self.waste, 
                self.circular, 
                self.open, 
                getattr(self, 'statsSaved', False)
            ), fn)
      
    def load(self, filename):
        '''
        Read a saved game from filename
        '''
        with open(filename, 'rb') as fin:
            (self.deck, self.undoStack, self.redoStack, self.stock, self.foundations, 
             self.waste, self.circular, self.open, self.statsSaved) = pickle.load(fin)
        self.statsSaved = True
        
    def dealsLeft(self) -> int:
        """
        Returns the number of times the stockpile can still deal cards.
        """
        return len(self.stock) // self.num_waste
    
    def moves(self):
        return len([m for m in self.undoStack if m != DEAL])
      
    def downCards(self):
        return sum(self.downUp(k)[0] for k in range(self.num_waste))
    
    def stats(self):
        # variant is 'Standard,' 'Circular,' 'Open,' or 'Both'
        # win is boolean
        # Moves is number of moves made
        # up is total face down cards turned up
        # upFirst is cards turned up on first deal
        
        date = datetime.date.today().strftime('%x')
        circ = self.circular
        op = self.open
        if not circ:
            variant = 'Standard' if not op else 'Open'
        else:
            variant = 'Circular' if not op else 'Both'
        win = self.win()
        moves = self.moves()
        undo = self.undoStack
        up = len([m for m in undo if m != DEAL and m[3]])
        try:
            first_deal_index = next(i for i, m in enumerate(undo) if m == DEAL)
            upFirst = len([m for m in undo[:first_deal_index] if m != DEAL and m[3]])
        except StopIteration:
            upFirst = 0
        return Stats(variant, win, moves, up, upFirst, date)
      
    def save_to_json(self, file_path, file_name):
        '''
        Save the current game state to a JSON file.
        
        Parameters:
            file_path (str): The directory path where the JSON file will be saved.
            file_name (str): The name of the JSON file (e.g., "game_state.json").
        
        The JSON file will include the state of the stock pile and all waste piles.
        '''
        try:
            # Construct the data structure to save
            data = {
                "stock": [
                    {
                        "code": card.code,
                        "rank": card.rank,
                        "suit": card.suit,
                        "faceUp": card.faceUp()
                    }
                    for card in self.stock
                ],
                "waste": [
                    [
                        {
                            "code": card.code,
                            "rank": card.rank,
                            "suit": card.suit,
                            "faceUp": card.faceUp()
                        }
                        for card in pile
                    ]
                    for pile in self.waste
                ]
            }
            
            # Ensure the output path exists
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            
            # Full file path
            full_path = os.path.join(file_path, file_name)
            
            # Write data to JSON file
            with open(full_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            
            print(f"Game state saved to {full_path}")
        except Exception as e:
            print(f"Error in saving game state: {e}")
        
    def is_complete_sequence(self, seq: List[Card]) -> bool:
        """
        Check if the sequence is a complete descending sequence from King to Ace
        and all cards are of the same suit.
        """
        if len(seq) != 13:
            return False
        expected_rank = KING
        suit = seq[0].suit
        for card in seq:
            if card.rank != expected_rank or card.suit != suit:
                return False
            expected_rank -= 1
        return True

    def get_all_possible_moves(self) -> List[Tuple[int, int, int]]:
        """
        Retrieve all possible legal moves in the current game state.
        Returns a list of tuples (source_pile_index, target_pile_index, card_idx).
        """
        possible_moves = []
        num_waste = self.num_waste

        # Iterate over all waste piles to find movable sequences
        for src_index, src_pile in enumerate(self.waste):
            if src_pile.isEmpty():
                continue
            # Find the index from where a movable sequence starts
            for card_idx in range(len(src_pile)):
                if src_pile.canSelect(card_idx):
                    selected_sequence = src_pile[card_idx:]
                    # Try to move to any other waste pile
                    for dest_index, dest_pile in enumerate(self.waste):
                        if dest_index == src_index:
                            continue
                        # Check if the move is legal
                        if dest_pile.isEmpty() or (dest_pile[-1].rank - selected_sequence[0].rank == 1):
                            possible_moves.append((src_index, dest_index, card_idx))
                    # Try to move to foundations only if the sequence is complete
                    if self.is_complete_sequence(selected_sequence):
                        for foundation_index in range(len(self.foundations)):
                            if self.foundations[foundation_index].isEmpty() or (self.foundations[foundation_index][-1].rank + 1 == selected_sequence[0].rank):
                                possible_moves.append((src_index, num_waste + foundation_index, card_idx))
                        # If circular, check for King to Ace moves
                        if self.circular:
                            for foundation_index in range(len(self.foundations)):
                                if self.foundations[foundation_index].isEmpty() and selected_sequence[0].rank == KING:
                                    possible_moves.append((src_index, num_waste + foundation_index, card_idx))
                    break  # Only consider the topmost movable sequence
        return possible_moves

Stats = namedtuple('Stats', ['variant', 'win', 'moves', 'up', 'up1', 'date'])
SummaryStats = namedtuple('SummaryStats', ['variant', 'games', 'win', 'moves', 'up', 'up1']) 
