import copy
import json
import random

import webapp2

global myside # this is the global variable that records whichside is me(white or black)
global phase # this is the global variable that records the phase of the whole game
            #  by counting the number of history records


class Tree:
    def __init__(self, board, which_side, move=None):
        self.board = board  # records the board
        self.value = None  # the point of the board
        self.children = []
        self.side = which_side  # 0 means my turn, 1 means the opposite's turn
        self.move = move  # the last move to reach this situation

    def add_children(self, board, move): # add children
        self.children.append(Tree(board, 1 - self.side, move=move))

    def get_board(self):
        return self.board

    def refresh(self):  # refresh the point of this board by the points of its children
        if self.side == 0:
            self.value = max([i.value for i in self.children])
        else:
            self.value = min([i.value for i in self.children])


# function to evaluate the board
def evaluate(board):
    global myside
    global phase

    evaluation_func1 = [[30, -12, 0, -1, -1, 0, -12, 30], [-12, -15, -3, -3, -3, -3, -15, -12],
                       [0, -3, 0, -1, -1, 0, -3, 0],
                       [-1, -3, -1, -1, -1, -1, -3, -1], [-1, -3, -1, -1, -1, -1, -3, -1],
                       [0, -3, 0, -1, -1, 0, -3, 0],
                       [-12, -15, -3, -3, -3, -3, -15, -12], [30, -12, 0, -1, -1, 0, -12, 30]]

    evaluation_func2 = [[100, -40, 20, 5, 5, 20, -40, 100], [-40, -80, -1, -1, -1, -1, -80, -40],
                       [20, -1, 5, 1, 1, 5, -1, 20],
                       [5, -1, 1, 0, 0, 1, -1, 5], [5, -1, 1, 0, 0, 1, -1, 5],
                       [20, -1, 5, 1, 1, 5, -1, 20],
                       [-40, -80, -1, -1, -1, -1, -80, -40], [100, -40, 20, 5, 5, 20, -40, 100]]

    if phase <= 40:  # the game just starts, use a method to calculate the score.
        # when the game is at the final phase, use another method to calculate the score.
        evaluation_func = evaluation_func2
    else:
        evaluation_func = evaluation_func1
    sum = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if board[y - 1][x - 1] == myside:
                sum += evaluation_func[y - 1][x - 1]
            elif board[y - 1][x - 1] == 3 - myside:
                sum -= evaluation_func[y - 1][x - 1]
    return sum

# function to evaluate the final state of the board
def final_evaluate(board):
    global myside
    my_score = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if board[y-1][x-1] == myside:
                my_score += 1
            else:
                my_score -= 1
    if my_score > 0:
        return float('inf')
    elif my_score < 0:
        return float('-inf')
    else:
        return 0

def construct_tree(g):
    # to prevent that the calculation time transcends 15 seconds, I constraine depth of the tree.
    if len(g.ValidMoves()) <= 4:
        depth = 5
    else:
        depth = 4
    root = Tree(g.board_["board"]["Pieces"], 0)  # the root of the tree

    new_game = {'board': g.board_["board"]["Pieces"], 'side': g.Next(),
                'valid_moves': [i['Where'] for i in g.ValidMoves()]}
    global myside
    myside = new_game['side'] # set my side( white or black)

    expand_tree(root, new_game, depth, None)  # expand the tree based on the info of new_game

    pick_best = []
    for x in root.children:
        print(x.move, x.value)
        if x.value == root.value:
            pick_best.append(x.move)

    # if there are several moves of the same score, pick one randomly
    index = random.randint(0, len(pick_best) - 1)
    return pick_best[index]


def expand_tree(root, g, depth, root_value):  # DFS algorithm, alpha-beta pruning
    temp = root
    if depth > 0:  # if this is not the deepest depth, expand the tree
        g['valid_moves'] = FindValidMove(g['board'], g['side'])  # find the next valid move from the board
        if g['valid_moves'] == []: # if there is no valid moves
            g['side'] = 3 - g['side']
            temp.add_children(g['board'], 'pass')
            expand_tree(temp.children[-1], g, depth - 1, temp.value)
            temp.refresh()

        elif g['valid_moves'] == True: # if the board is filled with pieces, evaluate which side wins
            temp.value = final_evaluate(temp.board)
            #print("inside ")
            #print('move is {0}, board is {1}, value is {2}'.format(temp.move, temp.board, temp.value))
        else:
            for x in g['valid_moves']:
                new_game = {}
                new_game['board'] = NextBoardPosition(g['board'], x, g['side'])  # refresh the board after one valid move
                new_game['side'] = 3 - g['side']

                temp.add_children(new_game['board'], x)  # add children
                expand_tree(temp.children[-1], new_game, depth - 1, temp.value)  # do Depth-first search
                temp.refresh()

                # alpha-beta pruning
                if root_value is not None:  # if root has value
                    if temp.side == 0 and temp.value > root_value:
                        return
                    elif temp.side == 1 and temp.value < root_value:
                        return
        return
    elif depth == 0:
        temp.value = evaluate(temp.board)
        #print('move is {0}, board is {1}, value is {2}'.format(temp.move, temp.board, temp.value))
    return


class Game:
    # Takes json.
    def __init__(self, body):
        self.board_ = json.loads(body)

    # Returns underlying board object.
    def Object(self):
        return self.board_

    # Returns piece on the board.
    # 0 for no pieces, 1 for player 1, 2 for player 2.
    # None for coordinate out of scope.

    def Pos(self, x, y):
        return Pos(self.board_["board"]["Pieces"], x, y)

    # Returns who plays next.
    def Next(self):
        return self.board_["board"]["Next"]

    # Returns the array of valid moves for next player.
    # Each move is a dict
    #   "Where": [x,y]
    #   "As": player number
    def ValidMoves(self):
        if self.board_["valid_moves"]:
            return self.board_["valid_moves"]
        return []

        # Helper function of NextBoardPosition.
        # It looks towards (delta_x, delta_y) direction and flip if valid.


def UpdateBoardDirection(new_board, x, y, delta_x, delta_y, side):
    player = side
    opponent = 3 - player
    look_x = x + delta_x
    look_y = y + delta_y
    flip_list = []
    while Pos(new_board, look_x, look_y) == opponent:
        flip_list.append([look_x, look_y])
        look_x += delta_x
        look_y += delta_y
    if Pos(new_board, look_x, look_y) == player:
        SetPos(new_board, x, y, player)
        for flip_move in flip_list:
            flip_x = flip_move[0]
            flip_y = flip_move[1]
            SetPos(new_board, flip_x, flip_y, player)


def NextBoardPosition(board, move, side):
    x = move[0]
    y = move[1]

    new_board = copy.deepcopy(board)
    UpdateBoardDirection(new_board, x, y, 1, 0, side)
    UpdateBoardDirection(new_board, x, y, 0, 1, side)
    UpdateBoardDirection(new_board, x, y, -1, 0, side)
    UpdateBoardDirection(new_board, x, y, 0, -1, side)
    UpdateBoardDirection(new_board, x, y, 1, 1, side)
    UpdateBoardDirection(new_board, x, y, -1, 1, side)
    UpdateBoardDirection(new_board, x, y, 1, -1, side)
    UpdateBoardDirection(new_board, x, y, -1, -1, side)
    return new_board

# check if location i is a valid place. i is one location (x,y) on the board. d is the direction to check
def isValid(i, d, board):
    opponent = board[i[1] - 1][i[0] - 1]
    player = 3 - opponent
    if d[0] != 0:
        delta_x = -d[0]
    else:
        delta_x = 0
    if d[1] != 0:
        delta_y = -d[1]
    else:
        delta_y = 0
    look_x = i[0] + delta_x
    look_y = i[1] + delta_y

    while Pos(board, look_x, look_y) == opponent:
        look_x += delta_x
        look_y += delta_y
    if Pos(board, look_x, look_y) == player:
        # print("pose is {0}".format(Pos(board, look_x, look_y)))
        # print("opponent is {0}, look_x is {1}, look_y is {2}".format(opponent, look_x, look_y))
        return True
    return False

# find all the next valid moves, given board and the next side to move
def FindValidMove(board, side):
    opponent = 3 - side
    opponent_loc = []
    valid_loc = []
    is_full = 1  # flag. whether the board is filled with pieces
    directions = [[0, 1], [1, 0], [-1, 0], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1]]
    for x in range(1, 9):
        for y in range(1, 9):
            if board[y - 1][x - 1] == 0:
                is_full = 0
            if board[y - 1][x - 1] == opponent:
                opponent_loc.append([x, y])
    #print("board is {0}, idfull is {1}, opponent loc is {2}.".format(board, is_full, opponent_loc))

    if is_full == 1:
        return True  # if the board is filled with pieces, return True

    # print("the opponent_loc is {0}".format(opponent_loc))
    for i in opponent_loc:
        for d in directions:
            x = i[0] + d[0]
            y = i[1] + d[1]

            # check if (x,y) is a valid place
            if 1 <= x <= 8 and 1 <= y <= 8 and board[y - 1][x - 1] == 0 and ([x, y] not in valid_loc) and isValid(i, d,
                                                                                                                  board):
                valid_loc.append([x, y])

    return valid_loc


def Pos(board, x, y):
    if 1 <= x and x <= 8 and 1 <= y and y <= 8:
        return board[y - 1][x - 1]
    return None


# Set piece on the board at (x,y) coordinate
def SetPos(board, x, y, piece):
    if x < 1 or 8 < x or y < 1 or 8 < y or piece not in [0, 1, 2]:
        return False
    board[y - 1][x - 1] = piece


# Debug function to pretty print the array representation of board.
def PrettyPrint(board, nl="<br>"):
    s = ""
    for row in board:
        for piece in row:
            s += str(piece)
        s += nl
    return s


def ParseMove(move):
    m = move
    return '%s%d' % (chr(ord('A') + m[0] - 1), m[1])

class MainHandler(webapp2.RequestHandler):
    # Handling GET request, just for debugging purposes.
    # If you open this handler directly, it will show you the
    # HTML form here and let you copy-paste some game's JSON
    # here for testing.

    def get(self):
        if not self.request.get('json'):
            self.response.write("""
                <body><form method=get>
                Paste JSON here:<p/><textarea name=json cols=80 rows=24></textarea>
                <p/><input type=submit></form></body>""")
            return

        else:
            g = Game(self.request.get('json'))
            self.pickMove(g)

    def post(self):
        # Reads JSON representation of the board and store as the object.
        g = Game(self.request.body)
        # Do the picking of a move and print the result.
        self.pickMove(g)

    def pickMove(self, g):
        global phase
        # Gets all valid moves.
        valid_moves = g.ValidMoves()
        if g.board_['history'] is not None:
            phase = len(g.board_['history'])
        else:
            phase = 0
        if len(valid_moves) == 0:
            # Passes if no valid moves.
            self.response.write("PASS")
        else:
            # Chooses a valid move randomly if available.
            move = construct_tree(g)
            print(move)
            self.response.write(ParseMove(move))


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
