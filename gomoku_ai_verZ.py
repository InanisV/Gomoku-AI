import random

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0

THINK_DEPTH = 2
THINK_BREADTH = 7
PLAYER_RADIO = 0.6
ATTACK = False

weights = {"11111": 500000, "011110": 43200, "011100": 720, "001110": 720, "011010": 720, "010110": 720,
           "11110": 720, "01111": 720, "11011": 720, "10111": 720, "11101": 720, "001100": 120,
           "001010": 120, "010100": 120, "000100": 20, "001000": 20}


def is_empty(chessboard):
    for row in chessboard:
        for color in row:
            if color != COLOR_NONE:
                return False
    return True


def evaluate_line(line):
    score = 1
    for key in weights.keys():
        if key in line:
            score += weights[key]
    return score


def evaluate_trace(trace):
    value, i = 0, 1 if ATTACK else -1
    for dot in trace:
        value += i * dot[0]
        i *= -1
    return value


def symbol(chessboard_color, my_color):
    if chessboard_color == COLOR_NONE:
        return '0'
    if chessboard_color == my_color:
        return '1'
    return '2'


class AI(object):

    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.candidate_list = []

    def go(self, chessboard):
        self.candidate_list.clear()
        # ==================================================================
        if is_empty(chessboard):
            self.candidate_list.append([7, 7])
        else:
            dot = self.evaluate_chessboard(chessboard)
            self.candidate_list.append((dot[1], dot[2]))
        # ==================================================================

    def get_dot_list(self, chessboard, color):
        dot_list = []
        for i in range(self.chessboard_size):
            for j in range(self.chessboard_size):
                if chessboard[i][j] != COLOR_NONE:
                    continue
                tmp = self.evaluate_dot(i, j, chessboard, color) + PLAYER_RADIO * self.evaluate_dot(i, j, chessboard, -color)
                dot_list.append((tmp, i, j))
        dot_list.sort(reverse=True)
        return dot_list[0: min(random.randint(2, THINK_BREADTH), len(dot_list))]

    def evaluate_dot(self, x, y, chessboard, color):
        chessboard[x][y] = color
        score = self.evaluate_horizontal(chessboard, x, y, color) + \
                self.evaluate_vertical(chessboard, x, y, color) + \
                self.evaluate_left_diag(chessboard, x, y, color) + \
                self.evaluate_right_diag(chessboard, x, y, color)
        chessboard[x][y] = COLOR_NONE
        return score

    def evaluate_horizontal(self, chessboard, x, y, color):
        line = str()
        for offset in range(-4, 5):
            if 0 <= y + offset < self.chessboard_size:
                tmp_color = chessboard[x][y + offset]
                line += symbol(tmp_color, color)
        return evaluate_line(line)

    def evaluate_vertical(self, chessboard, x, y, color):
        line = str()
        for offset in range(-4, 5):
            if 0 <= x + offset < self.chessboard_size:
                tmp_color = chessboard[x + offset][y]
                line += symbol(tmp_color, color)
        return evaluate_line(line)

    def evaluate_left_diag(self, chessboard, x, y, color):
        line = str()
        for offset in range(-4, 5):
            if 0 <= y + offset < self.chessboard_size and 0 <= x + offset < self.chessboard_size:
                tmp_color = chessboard[x + offset][y + offset]
                line += symbol(tmp_color, color)
        return evaluate_line(line)

    def evaluate_right_diag(self, chessboard, x, y, color):
        line = str()
        for offset in range(-4, 5):
            if 0 <= y + offset < self.chessboard_size and 0 <= x - offset < self.chessboard_size:
                tmp_color = chessboard[x - offset][y + offset]
                line += symbol(tmp_color, color)
        return evaluate_line(line)

    def evaluate_chessboard(self, chessboard):
        dot_list = self.get_dot_list(chessboard, self.color)
        if dot_list[0][0] >= 1440:
            return dot_list[0]
        best_val, best_dot = -1e15, dot_list[0]
        for dot in dot_list:
            chessboard[dot[1]][dot[2]] = self.color
            value = self.minmax(chessboard, 2 * THINK_DEPTH, False, -1e15, 1e15, [[dot[1], dot[2]]])
            chessboard[dot[1]][dot[2]] = COLOR_NONE
            if value > best_val:
                best_val, best_dot = value, dot
        return best_dot

    def minmax(self, chessboard, depth, is_max_player, alpha, beta, trace):
        if depth == 0:
            return evaluate_trace(trace)
        best_val = -1e15 if is_max_player else 1e15
        color = self.color if is_max_player else -self.color
        dot_list = self.get_dot_list(chessboard, color)
        for dot in dot_list:
            trace.append(dot)
            chessboard[dot[1]][dot[2]] = color
            value = self.minmax(chessboard, depth - 1, not is_max_player, alpha, beta, trace)
            chessboard[dot[1]][dot[2]] = color
            trace.remove(dot)
            if (is_max_player and value > best_val) or (not is_max_player and value < best_val):
                best_val = value
            if is_max_player:
                alpha = max(best_val, alpha)
            else:
                beta = min(best_val, beta)
            if beta <= alpha:
                break
        return best_val
