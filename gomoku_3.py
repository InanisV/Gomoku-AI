import numpy as np
import random
import copy
import time

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
random.seed(0)

MAX = 200000
FREE_FOUR = 3000
FREE_THREE = 450
FREE_TWO = 100
FREE_ONE = 1

BLOCKED_FOUR = 300
BLOCKED_THREE = 100
BLOCKED_TWO = 30

BLOCKED_POKED_FOUR = 280
BLOCKED_POKED_THREE = 150
FREE_POKED_FOUR = 1000
FREE_POKED_THREE = 350

class AI(object):
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.candidate_list = []

        self.chessboard = np.ones((self.chessboard_size, self.chessboard_size))
        self.line_judge = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.current = 0
        self.step_count = 0
        self.width = 0
        self.depth = 0
        self.saving_point = (-1, 0)

    def go(self, chessboard):
        self.candidate_list.clear()

        # decide which color to go
        white_num = np.where(chessboard == COLOR_WHITE)[0]
        black_num = np.where(chessboard == COLOR_BLACK)[0]
        self.current = COLOR_BLACK if len(black_num) == len(white_num) else COLOR_WHITE
        self.step_count = len(black_num) if self.current == COLOR_BLACK else len(white_num)

        # algorithm part
        idx = np.where(chessboard == COLOR_NONE)
        idx = list(zip(idx[0], idx[1]))
        # pos_idx = random.random(0, len(idx) - 1)
        # new_pos = idx[pos_idx]

        if len(idx) == 225:
            pos_idx = 112
            new_pos = idx[pos_idx]
        elif len(idx) == 223 and self.current == COLOR_BLACK \
                and (chessboard[6, 7] == COLOR_WHITE or chessboard[7, 8] == COLOR_WHITE
                     or chessboard[7, 6] == COLOR_WHITE or chessboard[8, 7] == COLOR_WHITE
                     or chessboard[6, 6] == COLOR_WHITE or chessboard[8, 8] == COLOR_WHITE
                     or chessboard[6, 8] == COLOR_WHITE or chessboard[8, 6] == COLOR_WHITE):
            if chessboard[6, 7] == COLOR_WHITE or chessboard[7, 8] == COLOR_WHITE:
                new_pos = (6, 8)
            elif chessboard[7, 6] == COLOR_WHITE or chessboard[8, 7] == COLOR_WHITE:
                new_pos = (8, 6)
            elif chessboard[6, 6] == COLOR_WHITE or chessboard[8, 8] == COLOR_WHITE:
                new_pos = (6, 8)
            elif chessboard[6, 8] == COLOR_WHITE or chessboard[8, 6] == COLOR_WHITE:
                new_pos = (8, 8)
        else:
            self.chessboard = chessboard
            # if self.current == COLOR_BLACK:
            #     self.width, self.depth = random.randint(4, 7), random.randint(3, 4)
            # else:
            if self.step_count < 5:
                self.width, self.depth = 1, 1
            else:
                # self.width, self.depth = 20, 2
                self.width, self.depth = random.randint(3, 7), random.randint(3, 4)
            #     elif self.step_count < 10:
            #         self.width, self.depth = random.randint(4, 7), random.randint(3, 4)
            #     else:
            #         self.width, self.depth = random.randint(3, 5), random.randint(3, 5)
            new_pos = self.emergency_check()
            if new_pos == (-1, -1):
                minimax_result = self.minimax(self.chessboard, self.depth, -MAX*100, MAX*100, self.current, [])
                new_pos = minimax_result[1]
            if new_pos == (-1, -1):
                pos_idx = 0
                score_idx = -1
                i = 0
                # for i, point in enumerate(idx):
                for point in idx:
                    if point == (4, 10) or point == (4, 2):
                        print(self.assess(point, 0 - self.current, self.chessboard), self.assess(point, self.current, self.chessboard))
                    defense_score = self.assess(point, 0 - self.current, self.chessboard)
                    attack_score = self.assess(point, self.current, self.chessboard)
                    if self.current == -1:
                        temp_score = defense_score + attack_score * 1.2
                    else:
                        temp_score = defense_score + attack_score
                    if temp_score > score_idx:
                        score_idx = temp_score
                        pos_idx = i
                    i += 1
                new_pos = idx[pos_idx]

        print(new_pos)
        assert chessboard[new_pos[0], new_pos[1]] == COLOR_NONE
        self.candidate_list.append(new_pos)

    def emergency_check(self):
        candidate = np.where(self.chessboard == COLOR_NONE)
        candidate = list(zip(candidate[0], candidate[1]))

        emergency = -1
        pos_emergency = 0
        i = 0
        for point in candidate:
            defense_score = self.assess(point, 0 - self.current, self.chessboard)
            attack_score = self.assess(point, self.current, self.chessboard)
            if point == (13, 5) or point == (8, 11):
                print(defense_score, attack_score)
            if defense_score >= 1000 or attack_score >= 1000:
                if attack_score >= MAX or (attack_score >= FREE_FOUR and emergency < MAX):
                    emergency = attack_score
                    pos_emergency = i
                if (defense_score > emergency or attack_score >= emergency) \
                        and (defense_score - emergency >= 200 or attack_score - emergency >= 200):
                    emergency = defense_score if defense_score > attack_score else attack_score
                    pos_emergency = i
            i += 1
        if emergency != -1:
            point_t = candidate[pos_emergency]
            return point_t
        else:
            return -1, -1

    def minimax(self, chessboard_t, depth, alpha, beta, current_t, tracer_t):
        point_t = (-1, -1)
        mark = -1 if current_t == self.current else MAX * 100
        if depth == 0 or self.evaluate(tracer_t) >= MAX:#or self.is_end(tracer_t)
            mark = self.evaluate(tracer_t)
            return [mark, point_t]
        board = copy.deepcopy(chessboard_t)
        tracer = copy.deepcopy(tracer_t)
        candidate = np.where(board == COLOR_NONE)
        candidate = list(zip(candidate[0], candidate[1]))

        score_idx = []
        emergency = -1
        pos_emergency = 0
        i = 0
        for point in candidate:
            defense_score = self.assess(point, 0 - self.current, board)
            attack_score = self.assess(point, self.current, board)
            if defense_score >= 1000 or attack_score >= 1000:
                if attack_score >= MAX or (attack_score >= FREE_FOUR and emergency < MAX):
                    emergency = attack_score
                    pos_emergency = i
                if (defense_score > emergency or attack_score >= emergency) \
                        and (defense_score - emergency >= 200 or attack_score - emergency >= 200):
                    emergency = defense_score if defense_score > attack_score else attack_score
                    pos_emergency = i
            # if self.current == -1 and self.current == current_t:
            #     temp_score = defense_score + attack_score * 1.2
            # else:
            temp_score = defense_score - attack_score
            score_idx.append((i, temp_score))
            i += 1
        if emergency != -1:
            mark = MAX
            point_t = candidate[pos_emergency]
            return [mark, point_t]
        else:
            score_idx.sort(reverse=True, key=self.take_second)
            score_idx = score_idx[:self.width]

        for pp in score_idx:
            p = candidate[pp[0]]
            if current_t == self.current:
                board[p[0], p[1]] = current_t
                tracer.append(p)
                temp_result = self.minimax(board, depth - 1, alpha, beta, 0 - current_t, tracer)
                if temp_result[0] >= mark:
                    mark = temp_result[0]
                    point_t = p
                alpha = max(alpha, mark)
                board[p[0], p[1]] = COLOR_NONE
                tracer.pop()
                if beta < alpha:
                    break
            else:
                board[p[0], p[1]] = current_t
                tracer.append(p)
                temp_result = self.minimax(board, depth - 1, alpha, beta, 0 - current_t, tracer)
                if temp_result[0] <= mark:
                    mark = temp_result[0]
                    point_t = p
                beta = min(beta, mark)
                board[p[0], p[1]] = COLOR_NONE
                tracer.pop()
                if beta < alpha:
                    break
        return [mark, point_t]

    @staticmethod
    def take_second(elem):
        return elem[1]

    def evaluate(self, tracing):
        result = 0
        temp_board = copy.deepcopy(self.chessboard)
        i = 0
        for point in tracing:
            color = ((-1)**i) * self.current
            temp_board[point[0], point[1]] = color
            # if i % 2 == 0:
            result += ((-1)**i) * (self.assess(point, 0 - color, temp_board) + self.assess(point, color, temp_board))
            i += 1
        return result

    def assess(self, point, current, board):
        score, consecutive, block, consecutive_2d, empty = 0, 1, 0, 0, -1
        length = len(board)

        # 左右
        i, j = point[0], point[1]
        while True:
            j += 1
            if j >= length:
                block += 1
                break
            elif board[i, j] == COLOR_NONE:
                if empty == -1 and j < length - 1 and board[i, j + 1] == current:
                    empty = consecutive
                    continue
                else:
                    break
            elif board[i, j] == current:
                consecutive += 1
            else:
                block += 1
                break

        i, j = point[0], point[1]
        while True:
            j -= 1
            if j < 0:
                block += 1
                break
            elif board[i, j] == COLOR_NONE:
                if empty == -1 and j > 0 and board[i, j - 1] == current:
                    empty = 0
                    continue
                else:
                    break
            elif board[i, j] == current:
                consecutive_2d += 1
                if empty != -1:
                    empty += 1
            else:
                block += 1
                break

        consecutive += consecutive_2d
        score += self.search_type(consecutive, block, empty)

        # 上下
        consecutive, block, consecutive_2d, empty = 1, 0, 0, -1

        i, j = point[0], point[1]
        while True:
            i += 1
            if i >= length:
                block += 1
                break
            elif board[i, j] == COLOR_NONE:
                if empty == -1 and i < length - 1 and board[i + 1, j] == current:
                    empty = consecutive
                    continue
                else:
                    break
            elif board[i, j] == current:
                consecutive += 1
            else:
                block += 1
                break

        i, j = point[0], point[1]
        while True:
            i -= 1
            if i < 0:
                block += 1
                break
            elif board[i, j] == COLOR_NONE:
                if empty == -1 and i > 0 and board[i - 1, j] == current:
                    empty = 0
                    continue
                else:
                    break
            elif board[i, j] == current:
                consecutive_2d += 1
                if empty != -1:
                    empty += 1
            else:
                block += 1
                break

        consecutive += consecutive_2d
        score += self.search_type(consecutive, block, empty)

        # 左上
        consecutive, block, consecutive_2d, empty = 1, 0, 0, -1

        i, j = point[0], point[1]
        while True:
            i += 1
            j += 1
            if i >= length or j >= length:
                block += 1
                break
            elif board[i, j] == COLOR_NONE:
                if empty == -1 and i < length - 1 and j < length - 1 and board[i + 1, j + 1] == current:
                    empty = consecutive
                    continue
                else:
                    break
            elif board[i, j] == current:
                consecutive += 1
            else:
                block += 1
                break

        i, j = point[0], point[1]
        while True:
            i -= 1
            j -= 1
            if i < 0 or j < 0:
                block += 1
                break
            elif board[i, j] == COLOR_NONE:
                if empty == -1 and i > 0 and j > 0 and board[i - 1, j - 1] == current:
                    empty = 0
                    continue
                else:
                    break
            elif board[i, j] == current:
                consecutive_2d += 1
                if empty != -1:
                    empty += 1
            else:
                block += 1
                break

        consecutive += consecutive_2d
        score += self.search_type(consecutive, block, empty)

        # 右上左下
        consecutive, block, consecutive_2d, empty = 1, 0, 0, -1

        i, j = point[0], point[1]
        while True:
            i += 1
            j -= 1
            if i >= length or j < 0:
                block += 1
                break
            elif board[i, j] == COLOR_NONE:
                if empty == -1 and i < length - 1 and j > 0 and board[i + 1, j - 1] == current:
                    empty = consecutive
                    continue
                else:
                    break
            elif board[i, j] == current:
                consecutive += 1
            else:
                block += 1
                break

        i, j = point[0], point[1]
        while True:
            i -= 1
            j += 1
            if i < 0 or j >= length:
                block += 1
                break
            elif board[i, j] == COLOR_NONE:
                if empty == -1 and i > 0 and j < length - 1 and board[i - 1, j + 1] == current:
                    empty = 0
                    continue
                else:
                    break
            elif board[i, j] == current:
                consecutive_2d += 1
                if empty != -1:
                    empty += 1
            else:
                block += 1
                break

        consecutive += consecutive_2d
        score += self.search_type(consecutive, block, empty)

        return self.type_analysis(score)

    @staticmethod
    def search_type(consecutive, block, empty):
        if empty <= 0:
            if consecutive >= 5:
                return MAX
            elif block == 0:
                if consecutive == 4:
                    return FREE_FOUR
                elif consecutive == 3:
                    return FREE_THREE
                elif consecutive == 2:
                    return FREE_TWO
            elif block == 1:
                if consecutive == 4:
                    return BLOCKED_FOUR
                elif consecutive == 3:
                    return BLOCKED_THREE
                elif consecutive == 2:
                    return BLOCKED_TWO
        elif empty == 1 or empty == consecutive - 1:  # *()*** / ***()* 两头第一个为空格
            if consecutive >= 6:
                return MAX
            elif block == 0:
                if consecutive == 5:
                    return FREE_FOUR
                elif consecutive == 4:
                    return FREE_POKED_FOUR
                elif consecutive == 3:
                    return FREE_POKED_THREE
                elif consecutive == 2:
                    return int(FREE_TWO / 2)
            elif block == 1:
                if consecutive == 5:
                    return FREE_FOUR
                elif consecutive == 4:
                    return BLOCKED_POKED_FOUR
                elif consecutive == 3:
                    return BLOCKED_POKED_THREE
                elif consecutive == 2:
                    return BLOCKED_TWO
        elif empty == 2 or empty == consecutive - 2:
            if consecutive >= 7:
                return MAX
            elif block == 0:
                if consecutive == 6:
                    return FREE_FOUR
                elif consecutive == 5:
                    return BLOCKED_FOUR
                elif consecutive == 4:
                    return FREE_THREE
            elif block == 1:
                if consecutive == 6:
                    return FREE_FOUR
                elif consecutive == 5:
                    return BLOCKED_FOUR
                elif consecutive == 4:
                    return BLOCKED_POKED_FOUR
                elif consecutive == 3:
                    return BLOCKED_THREE
            elif block == 2:
                if consecutive == 6:
                    return BLOCKED_FOUR
                if consecutive == 5:
                    return BLOCKED_POKED_FOUR
                if consecutive == 4:
                    return BLOCKED_POKED_FOUR
        elif empty == 3 or empty == consecutive - 3:
            if consecutive >= 8:
                return MAX
            elif block == 0:
                if consecutive == 7:
                    return FREE_FOUR
                elif consecutive == 6:
                    return BLOCKED_FOUR
                elif consecutive == 5:
                    return FREE_THREE
            elif block == 1:
                if consecutive == 7:
                    return FREE_FOUR
                elif consecutive == 6:
                    return BLOCKED_FOUR
            elif block == 2:
                if consecutive == 7:
                    return BLOCKED_FOUR
                if consecutive == 5:
                    return BLOCKED_POKED_FOUR
        elif empty == 4 or empty == consecutive - 4:
            if consecutive >= 9:
                return MAX
            elif block == 0:
                if consecutive == 8:
                    return FREE_FOUR
            elif block == 1:
                if consecutive == 8:
                    return FREE_FOUR
                elif consecutive == 7:
                    return BLOCKED_FOUR
            elif block == 2:
                if consecutive == 8:
                    return BLOCKED_FOUR
        elif empty == 5 or empty == consecutive - 5:
            return MAX
        return 0

    def type_analysis(self, score):
        if score == FREE_TWO * 2:
            return score + 200
        if score == BLOCKED_FOUR + BLOCKED_THREE:
            return score + 500
        if score == BLOCKED_POKED_FOUR + FREE_POKED_THREE or score == BLOCKED_POKED_FOUR * 2:
            return 2000
        if MAX > score >= FREE_FOUR + BLOCKED_THREE:
            return FREE_FOUR * 2
        if 500 <= score < BLOCKED_FOUR * 2 or score == BLOCKED_POKED_THREE + FREE_THREE:
            return score + 500
        elif BLOCKED_FOUR * 2 <= score < FREE_FOUR:
            return 2500
        else:
            return score