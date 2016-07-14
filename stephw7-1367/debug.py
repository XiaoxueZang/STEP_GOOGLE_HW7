import copy
import json
#import webapp2

global myside

class Tree:
    def __init__(self, board, which_side, move=None):
        self.board = board
        self.value = None
        self.children = []
        self.side = which_side  # 0 means my turn, 1 means the opposite's turn
        self.move = move

    def add_children(self, board, move):
        self.children.append(Tree(board, 1 - self.side, move=move))

    def get_board(self):
        return self.board

    def refresh(self):
        if self.side == 0:
            self.value = max([i.value for i in self.children])
        else:
            self.value = min([i.value for i in self.children])


def evaluate(board):
    global myside
    evaluation_func = [[30, -12, 0, -1, -1, 0, -12, 30], [-12, -15, -3, -3, -3, -3, -15, -12],
                       [0, -3, 0, -1, -1, 0, -3, 0],
                       [-1, -3, -1, -1, -1, -1, -3, -1], [-1, -3, -1, -1, -1, -1, -3, -1],
                       [0, -3, 0, -1, -1, 0, -3, 0],
                       [-12, -15, -3, -3, -3, -3, -15, -12], [30, -12, 0, -1, -1, 0, -12, 30]]
    sum = 0
    for x in range(1, 8):
        for y in range(1, 8):
            if board[y - 1][x - 1] == myside:
                sum += evaluation_func[y - 1][x - 1]
            elif board[y - 1][x - 1] == 3 - myside:
                sum -= evaluation_func[y - 1][x - 1]
    return sum

def construct_tree(g):
    depth = 5
    root = Tree(g.board_["board"]["Pieces"], 0)
    new_game = {'board': g.board_["board"]["Pieces"], 'side': g.Next()}#'valid_moves': [i['Where'] for i in g.ValidMoves()]}
    global myside
    myside = new_game['side']
    print("the root is")
    #print(new_game)
    expand_tree(root, new_game, depth, None)
    print("go to the root")
    for x in root.children:
        print(x)
        if x.value == root.value:
            return x

def continue_construct_tree(x, root_value = None):
    if x.children !=[]:
        x.value = None
        for child in x.children:
            child.value = None
            continue_construct_tree(child, x.value)
            x.refresh()
            if x.value is not None:
                if child.side == 0 and child.value >=x.value:
                    return
                elif child.side == 1 and child.value <= x.value:
                    return
    else:
        new_game = {'board': x.board, 'side': x.side}
        expand_tree(x, new_game, 4, root_value)



def expand_tree(root, g, depth, root_value):
    temp = root
    if depth > 0:
        g['valid_moves'] = FindValidMove(g['board'], g['side'])
        #print ("the g is {0}".format(g))
        for x in g['valid_moves']:
            new_game = {}
            new_game['board'] = NextBoardPosition(g['board'], x, g['side'])
            new_game['side'] = 3-g['side']
            #print(new_game)
            #print("depth is {0}".format(depth))
            temp.add_children(new_game['board'], x)
            expand_tree(temp.children[-1], new_game, depth - 1, temp.value)
            temp.refresh()

            # alpha and beta algorithm
            if root_value is not None:
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
        SetPos( new_board, x, y, player)
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


def isValid(i,d,board):
    opponent = board[i[1]-1][i[0]-1]
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
        #print("pose is {0}".format(Pos(board, look_x, look_y)))
        #print("opponent is {0}, look_x is {1}, look_y is {2}".format(opponent, look_x, look_y))
        return True
    return False

def FindValidMove(board, side):
    opponent = 3-side
    opponent_loc = []
    valid_loc = []
    directions = [[0,1],[1,0],[-1,0],[0,-1],[1,1],[-1,1],[1,-1],[-1,-1]]
    for x in range(1, 8):
        for y in range(1, 8):
            if board[y-1][x-1] == opponent:
                opponent_loc.append([x, y])

    #print("the opponent_loc is {0}".format(opponent_loc))
    for i in opponent_loc:
        for d in directions:
            x = i[0]+d[0]
            y = i[1]+d[1]
            #print("x is {0}, y is {1}".format(x,y))
            if board[y-1][x-1] == 0 and ([x, y] not in valid_loc) and isValid(i, d, board):
                valid_loc.append([x, y])
    #print("valid_loc is ")
    #print(valid_loc)
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


class start:
    def __init__(self, a):
        g = Game(a)
        self.tree = None
        self.pickMove(g)

    def pickMove(self, g):
        # Gets all valid moves.
        valid_moves = g.ValidMoves()
        if len(valid_moves) == 0:
            # Passes if no valid moves.
            print("PASS")
        else:
            # Chooses a valid move randomly if available.
            if self.tree == None:
                self.tree = construct_tree(g)
                print(self.tree.move)
                print(ParseMove(self.tree.move))
            else:
                print('not NOne')
                for x in self.tree.children:
                    if x.move == g.board_["history"][-1]['Where']:
                        print([i.value for i in x.children])
                        # print(g.board_["board"]["Pieces"])
                        continue_construct_tree(x)
                        print("jkl")
                        print(x.board)
                        print(x.move, x.board, x.value)
                        print([i.value for i in x.children])



b2 = """{"board":{"Pieces":[[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,2,0,0,0,0,0],[0,0,1,2,1,0,0,0],[0,0,0,1,2,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]],"Next":1},"gamekey":"ag5zfnN0ZXAtb3RoZWxsb3IRCxIER2FtZRiAgICA3eudCQw","history":[{"Where":[3,4],"As":1},{"Where":[3,3],"As":2}],"valid_moves":[{"Where":[3,2],"As":1},{"Where":[4,3],"As":1},{"Where":[6,5],"As":1},{"Where":[5,6],"As":1}]}"""

b1 = """{"board":{"Pieces":[[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,2,1,0,0,0],[0,0,0,1,2,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]],"Next":1},"gamekey":"ag5zfnN0ZXAtb3RoZWxsb3IRCxIER2FtZRiAgICA3caECQw","history":null,"valid_moves":[{"Where":[4,3],"As":1},{"Where":[3,4],"As":1},{"Where":[6,5],"As":1},{"Where":[5,6],"As":1}]}"""

a = start(b1)

a.pickMove(Game(b2))