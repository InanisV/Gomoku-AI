import time

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0

PLAYER_RADIO = 0.7

weights = {"11111": 50000, "011110": 4320, "011100": 720, "001110": 720, "011010": 720, "010110": 720,
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
            self.candidate_list.append(self.evaluate_chessboard(chessboard, self.color))
        # ==================================================================

    def evaluate_chessboard(self, chessboard, color):
        data, x, y = 0, 0, 0
        for i in range(self.chessboard_size):
            for j in range(self.chessboard_size):
                if chessboard[i][j] != COLOR_NONE:
                    continue
                tmp = self.evaluate_dot(i, j, chessboard, color) + PLAYER_RADIO * self.evaluate_dot(i, j, chessboard, -color)
                if tmp > data:
                    data, x, y = tmp, i, j
        return x, y

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
                if tmp_color == color:
                    line += '1'
                elif tmp_color == COLOR_NONE:
                    line += '0'
                else:
                    line += '2'
        return evaluate_line(line)

    def evaluate_vertical(self, chessboard, x, y, color):
        line = str()
        for offset in range(-4, 5):
            if 0 <= x + offset < self.chessboard_size:
                tmp_color = chessboard[x + offset][y]
                if tmp_color == color:
                    line += '1'
                elif tmp_color == COLOR_NONE:
                    line += '0'
                else:
                    line += '2'
        return evaluate_line(line)

    def evaluate_left_diag(self, chessboard, x, y, color):
        line = str()
        for offset in range(-4, 5):
            if 0 <= y + offset < self.chessboard_size and 0 <= x + offset < self.chessboard_size:
                tmp_color = chessboard[x + offset][y + offset]
                if tmp_color == color:
                    line += '1'
                elif tmp_color == COLOR_NONE:
                    line += '0'
                else:
                    line += '2'
        return evaluate_line(line)

    def evaluate_right_diag(self, chessboard, x, y, color):
        line = str()
        for offset in range(-4, 5):
            if 0 <= y + offset < self.chessboard_size and 0 <= x - offset < self.chessboard_size:
                tmp_color = chessboard[x - offset][y + offset]
                if tmp_color == color:
                    line += '1'
                elif tmp_color == COLOR_NONE:
                    line += '0'
                else:
                    line += '2'
        return evaluate_line(line)
