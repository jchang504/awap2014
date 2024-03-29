##############################################################################
# game.py - Responsible for generating moves to give to client.py            #
# Moves via stdout in the form of "# # # #" (block index, # rotations, x, y) #
# Important function is find_move, which should contain the main AI          #
##############################################################################

import sys
import json
import math

# Simple point class that supports equality, addition, and rotations
class Point:
    x = 0
    y = 0

    # Can be instantiated as either Point(x, y) or Point({'x': x, 'y': y})
    def __init__(self, x=0, y=0):
        if isinstance(x, dict):
            self.x = x['x']
            self.y = x['y']
        else:
            self.x = x
            self.y = y

    def __add__(self, point):
        return Point(self.x + point.x, self.y + point.y)

    def __eq__(self, point):
        return self.x == point.x and self.y == point.y

    # rotates 90deg counterclockwise
    def rotate(self, num_rotations):
        if num_rotations == 1: return Point(-self.y, self.x)
        if num_rotations == 2: return Point(-self.x, -self.y)
        if num_rotations == 3: return Point(self.y, -self.x)
        return self

    def distance(self, point):
        return abs(point.x - self.x) + abs(point.y - self.y)


# Given that square (a Point object) is owned by 
# the player player_number, this function returns all of the
# squares in the same connected component (or all squares in
# the same block) as square. The output is a list of Points.
def connected_squares(square, player_number):

    # Returns list of points on the board adjacent
    # to point
    def adjacent_to(point):
        x = point.x
        y = point.y
        adjacent_to_point = []
        if x + 1 <= 19:
            adjacent_to_point.append(Point(x+1,y))
        if x - 1 >= 0:
            adjacent_to_point.append(Point(x-1,y))
        if y + 1 <= 19:
            adjacent_to_point.append(Point(x,y+1))
        if y - 1 >= 0:
            adjacent_to_point.append(Point(x,y-1))
        return adjacent_to_point


    visited = []
    stack = [square]
    while len(stack) > 0:
        top_vertex = stack.pop(len(stack)-1)
        children = adjacent_to(top_vertex)
        for child in children:
            if child not in visited:
                stack.append(child)
        visited.append(top_vertex)
    return visited








# Returns the player's score on a given board
# bonus_squares is list of Points
# rep invariant: the pieces are arranged according to blokus rules
# in particular everything reachable from a square in a given block
# going up, down, left, and right is in the same block
def score(grid, bonus_squares, player_number):
    # Find number of squares in blocks containing dogecoins
    score = 0
    dogecoin_multiplier = 3
    number_squares_receiving_multiplier = 0;

    dogecoin_points_covered_by_player = []
    for dogecoin_point in bonus_squares:
        if grid[dogecoin_point[0]][dogecoin_point[1]] == player_number:
            #dogecoin_points_covered_by_player.append(dogecoin_point)
            number_squares_receiving_multiplier += 4 # assume size 4 block
    '''
    for square in dogecoin_points_covered_by_player: 
        for connected_square in connected_squares(square):
            number_squares_receiving_multiplier += 1'''

    # Find total number of squares covered by player
    total_player_squares = 0
    for i in range(20):
        for j in range(20):
            if grid[i][j] == player_number:
                total_player_squares += 1

    # Compute final score 
    return (dogecoin_multiplier - 1)*number_squares_receiving_multiplier + (total_player_squares - number_squares_receiving_multiplier)


    
# still need to implement helper function to count number of corners available



# Simple heuristic
# grid is list of lists (20x20) representing the board, with the following entries:
# -2 - crater
# -1 - empty
# 0 - player 1 block
# 1 - player 2 block
# 2 - player 3 block
# 3 - player 4 block
# Score is linear combination of current score and number of free corners
def heuristic1(grid, bonus_squares, player_number):
   # a_1 = 1
   # a_2 = 1
    current_score = score(grid, bonus_squares, player_number) # some number around 10-50 or so
    num_corners = 0 # some number around 10 or so

'''
    for i in range(40):
        for j in range(40):
            if grid[i][j] == player_number:
                if all([not isFilled(i+deltaI, j+deltaJ, player_number) for deltaI, deltaJ in [(1,0),(-1,0),(0,1),(0,-1)]]):
                    if any([isFilled(i+deltaI, j+deltaJ, player_number) for deltaI, deltaJ in [(1,1),(-1,1),(1,-1),(-1,-1)]]):
                        num_corners += 1
'''
    return 0.1 * current_score + num_corners
    
def isFilled(i, j, grid, player_number):
    return (i >= 0 and i < 20 and j >= 0 and j < 20 and grid[i][j] == player_number)

def play(grid, playerNumber, blocks, move):
    (block_index, num_rot, x, y) = move
    removed_block = blocks[block_index]
    #removed_block = blocks.pop(block_index)
    block_rot = [offset.rotate(num_rot) for offset in removed_block]
    for (i,j) in block_rot:
        grid[x+i,y+j] = playerNumber
    return block_rot

# takes the already rotated block
def unplay(grid, block, point, blocks):
    x = point.x
    y = point.y
    for (i,j) in block:
        grid[x+i,y+j] = -1
    #blocks.append(block)

# important: block is the already rotated form
def can_play(grid, playerNumber, block, point):

    N = len(grid) - 1

    onAbsCorner = False
    onRelCorner = False

    corners = [Point(0, 0), Point(N, 0), Point(N, N), Point(0, N)]
    corner = corners[playerNumber]

    for offset in block:
        p = point + offset
        x = p.x
        y = p.y
        if (x > N or x < 0 or y > N or y < 0 or grid[x][y] != -1 or
            (x > 0 and grid[x - 1][y] == playerNumber) or
            (y > 0 and grid[x][y - 1] == playerNumber) or
            (x < N and grid[x + 1][y] == playerNumber) or
            (y < N and grid[x][y + 1] == playerNumber)
        ): return False

        onAbsCorner = onAbsCorner or (p == corner)
        onRelCorner = onRelCorner or (
            (x > 0 and y > 0 and grid[x - 1][y - 1] == playerNumber) or
            (x > 0 and y < N and grid[x - 1][y + 1] == playerNumber) or
            (x < N and y > 0 and grid[x + 1][y - 1] == playerNumber) or
            (x < N and y < N and grid[x + 1][y + 1] == playerNumber)
        )

    if grid[corner.x][corner.y] < 0 and not onAbsCorner: return False
    if not onAbsCorner and not onRelCorner: return False

def get_next_moves(grid, playerNumber, blocks):

    # first we create an ordering of the blocks, largest-first
    indexToLen = enumerate([len(b) for b in blocks])
    blockIndices = [x for (x,y) in sorted(indexToLen, key=(lambda x : x[1]), reverse=True)]

    result = []
    
    N = len(grid)
    for i in range(N):
      for j in range(N):
        for block_index in blockIndices:
          for r in range(4):
            block_rot = [offset.rotate(r) for offset in blocks[block_index]]
            if can_play(grid, playerNumber, block_rot, Point(i,j)):
              result.append((block_index, r, i, j))

    return result


class Game:
    blocks = []
    grid = []
    bonus_squares = []
    my_number = -1
    dimension = -1 # Board is assumed to be square
    turn = -1

    def __init__(self, args):
        self.interpret_data(args)

    # find_move is your place to start. When it's your turn,
    # find_move will be called and you must return where to go.
    # You must return a tuple (block index, # rotations, x, y)
    def find_move(self):
        print (type (self.bonus_squares))# TODO: remove
        print (type (self.bonus_squares[0]))# TODO: remove
        move, score = minimax(self.grid, self.blocks, self.bonus_squares, 1, eval_fn = heuristic1, # heuristic1(grid, bonus_squares, player_number):
                            get_next_moves_fn = get_next_moves,
                            player_number=self.my_number, verbose = False)
        if move is not None:
          return move
        else:
          return (0,0,0,0) # TODO: fix

        '''
        moves = []
        N = self.dimension
        for index, block in enumerate(self.blocks):
            for i in range(0, N * N):
                x = i / N
                y = i % N

                for rotations in range(0, 4):
                    new_block = self.rotate_block(block, rotations)
                    if self.can_place(new_block, Point(x, y)):
                        return (index, rotations, x, y)

        return (0, 0, 0, 0)  '''  

    # Checks if a block can be placed at the given point
    def can_place(self, block, point):
        onAbsCorner = False
        onRelCorner = False
        N = self.dimension - 1

        corners = [Point(0, 0), Point(N, 0), Point(N, N), Point(0, N)]
        corner = corners[self.my_number]

        for offset in block:
            p = point + offset
            x = p.x
            y = p.y
            if (x > N or x < 0 or y > N or y < 0 or self.grid[x][y] != -1 or
                (x > 0 and self.grid[x - 1][y] == self.my_number) or
                (y > 0 and self.grid[x][y - 1] == self.my_number) or
                (x < N and self.grid[x + 1][y] == self.my_number) or
                (y < N and self.grid[x][y + 1] == self.my_number)
            ): return False

            onAbsCorner = onAbsCorner or (p == corner)
            onRelCorner = onRelCorner or (
                (x > 0 and y > 0 and self.grid[x - 1][y - 1] == self.my_number) or
                (x > 0 and y < N and self.grid[x - 1][y + 1] == self.my_number) or
                (x < N and y > 0 and self.grid[x + 1][y - 1] == self.my_number) or
                (x < N and y < N and self.grid[x + 1][y + 1] == self.my_number)
            )

        if self.grid[corner.x][corner.y] < 0 and not onAbsCorner: return False
        if not onAbsCorner and not onRelCorner: return False

        return True

    # rotates block 90deg counterclockwise
    def rotate_block(self, block, num_rotations):
        return [offset.rotate(num_rotations) for offset in block]

    # updates local variables with state from the server
    def interpret_data(self, args):
        if 'error' in args:
            debug('Error: ' + args['error'])
            return

        if 'number' in args:
            self.my_number = args['number']

        if 'board' in args:
            self.dimension = args['board']['dimension']
            self.turn = args['turn']
            self.grid = args['board']['grid']
            self.blocks = args['blocks'][self.my_number]
            self.bonus_squares = args['board']['bonus_squares']

            for index, block in enumerate(self.blocks):
                self.blocks[index] = [Point(offset) for offset in block]

        if (('move' in args) and (args['move'] == 1)):
            send_command(" ".join(str(x) for x in self.find_move()))

    def is_my_turn(self):
        return self.turn == self.my_number


# Minimax search
def minimax(grid, blocks, bonus_squares, depth, eval_fn = heuristic1, # heuristic1(grid, bonus_squares, player_number):
            get_next_moves_fn = get_next_moves,
            player_number = 0, verbose=True):
    """
    Do a minimax search to the specified depth on the specified board.

    board -- the 2D array board to evaluate. 
    depth -- the depth of the search tree (measured in maximum distance from a leaf to the root)
    eval_fn -- the evaluation function to use to give a value to a leaf of the tree

    Returns (move, score). move and score are both 4-tuples. move is what we're interested in
    """
    
    best = None
    next_moves = get_next_moves_fn(grid, player_number, blocks)

    if depth == 0: # If at the leaf, evaluate.
        return (None, [eval_fn(grid, bonus_squares, p) for p in range(4)])
    
    if len(next_moves) == 0: # Can't move anywhere; essentially skips the turn.
        # Evaluate next player's moves
        new_move, new_score = minimax(grid, blocks, bonus_squares, depth-1, eval_fn, get_next_moves_fn,
                                        (player_number + 1)%4, verbose)
        if best == None or new_score[player_number] > best[1][player_number]:
            best = (None, new_score)
        
    for move in next_moves:
        # Play move. grid should now be a different grid.
        block_played = play(grid, player_number, blocks, move)

        # Evaluate next player's moves.
        new_move, new_score = minimax(grid, blocks, bonus_squares, depth-1, eval_fn, get_next_moves_fn,
                                        (player_number + 1)%4, verbose)
        if best == None or new_score[player_number] > best[1][player_number]:
            best = (move, new_score)

        # Unplay move. grid should now be back to original.
        unplay(grid, block_played, Point(move[2],move[3]), blocks)
        
    if verbose:
        print "MINIMAX: Decided on move %d with rating %d" % (best[0], best[1])

    return best


def get_state():
    return json.loads(raw_input())

def send_command(message):
    print message
    sys.stdout.flush()

def debug(message):
    send_command('DEBUG ' + str(message))

def main():
    setup = get_state()
    game = Game(setup)

    while True:
        state = get_state()
        game.interpret_data(state)




if __name__ == "__main__":
    main()

