KLONDIKE_GAME_DESCR_GENERAL = '''
The given image represents the interface of the game Klondike Solitaire. The user interface consists of a board with 52 playing cards divided into four distinct areas:

1. **Stock Pile (Draw Pile):** Initially composed of 24 face-down cards. The player can draw one card at a time to reveal its face.

2. **Waste Pile (Dump Pile):** This pile holds the cards drawn from the Stock Pile that have not been moved to other areas. Only the topmost card in the Waste Pile is available for play.

3. **Foundation Piles:** These four piles are designated for each suit (hearts, diamonds, clubs, and spades, but not necessarily following this order). From left to right, they are referred to as foundation 1 through foundation 4. Players must build up the foundation starting with the Ace and then place cards in ascending order (2 through King) of the same suit.

4. **Tableau Piles:** There are seven tableau piles. From left to right, these piles are referred to as Tab 1 through Tab 7, and initially contain an increasing number of cards from 1 to 7. Only the topmost cards in each pile are face-up and built in descending order, alternating colors (red and black suits). Only when the topmost cards are removed to some other place (e.g. another tableau pile or the foundation pile) will the hidden card beneath be revealed. Only a King can be placed on an empty tableau pile unless it starts there at the beginning of the game.

**Objective:**
The goal of Klondike Solitaire is to move all cards to the Foundation Piles, organized by suit in ascending order from Ace to King.
'''
DEADLOCK_DESCR = '''
A deadlock occurs in Klondike Solitaire when the player reaches a state where no more effective moves can be made. To be more specific, certain moves are not considered deadlocks:
- **Draw Pile**: Drawing a new card from the draw pile can always break a deadlock.
- **Waste Pile**: Moving a card from the waste pile to the tableau or foundation can break a deadlock.
- **Foundation Pile**: Moving a card to the foundation pile can always break a deadlock.
- **Tableau Pile**: A move within the tableau pile can break a deadlock only if it relocates a card to another tableau pile while revealing a hidden card or create an empty tableau pile where a King can be placed.
If none of these moves are possible, the game is in a deadlock state.

'''

EFFECTIVE_MOVE_DESCR = '''
In the game of Klondike Solitaire, making effective moves is crucial to successfully completing the game. An effective move is one that maximizes the number of cards that can be moved to the Foundation Piles or can reveal hidden cards in tableau piles, stock pile or waste pile. This involves strategic planning and considering the current game state to make the best move possible.
'''
# For the sake of simplicity, the following constants are not used in the code
NONSENSE = '''
This can happen due to a combination of factors such as blocked tableau piles, no available moves in the stock pile or waste pile, and no cards to move to the foundation piles.
Deadlocks can be frustrating for players as they prevent progress in the game and may require restarting the game or undoing moves to continue playing.
'''

