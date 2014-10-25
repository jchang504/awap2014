##############################################################################
# game.py - Responsible for generating moves to give to client.py            #
# Moves via stdout in the form of "# # # #" (block index, # rotations, x, y) #
# Important function is find_move, which should contain the main AI          #
##############################################################################

import sys
import json

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
    dogecoin_multiplier = 3
    dogecoin_points_covered_by_player = []
    for dogecoin_point in bonus_squares:
        if grid[dogecoin_point.x][dogecoin_point.y] == player_number:
            dogecoin_points_covered_by_player.append(dogecoin_point)

    return 0


    




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
    a_1 = 1
    a_2 = 1

    return 0

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

        return (0, 0, 0, 0)

    # Minimax search
    def minimax(board, depth, eval_fn = simon_evaluate,
            get_next_moves_fn = get_all_next_moves,
            turn = 0, is_terminal_fn = is_terminal,
            verbose = True):

    
    best_val = None
    
    for move, new_board in get_next_moves_fn(board):
        val = -1 * minimax_find_board_value(new_board, depth-1, eval_fn,
                                            get_next_moves_fn,
                                            is_terminal_fn)
        if best_val == None or val > best_val[0]:
            best_val = (val, move, new_board)
            
    if verbose:
        print "MINIMAX: Decided on column %d with rating %d" % (best_val[1], best_val[0])

    return best_val[1]

    

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

