# coding=utf-8
import numpy as np
import random
import time

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0

h_5 = 20000  #连5
h_4 = 2000  #活4
c_4 = 300  #冲4
tc_4 = 250  #跳冲4
h_3 = 450  #活3
c_3 = 50  #冲3
tc_3 = 300  #跳冲3
h_2 = 100  # 活2
c_2 = 30  # 冲2
# MAX_NODE = 5
random.seed(5544)


# don't change the class name
class AI(object):
    # chessboard_size, color, time_out passed from agent
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.direction = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, -1], [-1, 1], [1, 1], [-1, -1]]
        # You are white or black
        self.chessboard = None
        self.color = color
        # the max time you should use, your algorithm's run time must not exceed the time limit.
        self.time_out = time_out
        self.max_node = 6
        # the max node in a line
        self.candidate_list = []

    # The input is current chessboard.
    def go(self, chessboard):
        # Clear candidate_list
        start_time = time.time()
        self.candidate_list.clear()
        self.chessboard = chessboard
        self.max_depth = 4
        self.global_max = -10000000
        self.position_value = np.zeros((self.chessboard_size, self.chessboard_size), dtype = 'int32')
        self.empty = np.zeros((self.chessboard_size, self.chessboard_size), dtype = 'int32')
        self.my_score = np.zeros((self.chessboard_size, self.chessboard_size), dtype = 'int32')
        self.en_score = np.zeros((self.chessboard_size, self.chessboard_size), dtype = 'int32')
        ## 给棋盘赋值
        for i in range(self.chessboard_size):
            for j in range(self.chessboard_size):
                self.position_value[i][j] = self.chessboard_size // 2 - \
                                           max(abs(i - self.chessboard_size // 2), abs(j - self.chessboard_size // 2))
        if (chessboard == self.empty).all():
            self.candidate_list.append((7,7))
        else:
            self.search(self.color, 0)
        # print("color is: ", self.color)
        # print(self.candidate_list)
        print("The time used is: ", str(time.time() - start_time))

    def search(self, color, depth, alpha= -1000000, beta = 1000000 ):
        if depth >= self.max_depth:
            # print(self.global_evaluate())
            return self.global_evaluate()
        # initiate the scores
        move_list = None
        if depth == 0:
            move_list = self.init_move()
        else:
            move_list = self.move()
        m_s = 0
        e_s = 0
            # en_mark = tuple()
        mark = tuple()
        for x, y in move_list:
            if m_s < self.my_score[x][y]:
                m_s = self.my_score[x][y]
                mark = (x, y)
                # print(mark)
            if e_s < self.en_score[x][y]:
                e_s = self.en_score[x][y]

        if m_s >= e_s and m_s >= h_4:
            if color == self.color:
                alpha = h_5
                if depth == 0:
                    self.global_max = h_5
                    self.candidate_list.append( mark )
                return alpha
            else:
                for x, y in move_list:
                    if m_s == self.my_score[x][y]:
                        self.chessboard[x][y] = color
                        self.score_reevaluate(x, y)
                        new_score = self.search(-color, depth + 1, alpha, beta)
                        self.chessboard[x][y] = COLOR_NONE
                        self.score_reevaluate(x, y)
                        if new_score < beta:
                            beta = new_score
                        if alpha >= beta:
                            return beta
                return beta
        elif m_s <= e_s and e_s >= h_4:
            # print('ok')
            if color == self.color:
                for x, y in move_list:
                    if e_s == self.en_score[x][y]:
                        self.chessboard[x][y] = color
                        self.score_reevaluate(x, y)
                        new_score = self.search(-color, depth + 1, alpha, beta)
                        if new_score > self.global_max and depth == 0:
                            self.global_max = new_score
                            self.candidate_list.append( (x,y))
                        self.chessboard[x][y] = COLOR_NONE
                        self.score_reevaluate(x, y)
                        if new_score> alpha:
                            alpha= new_score
                        if alpha >= beta:
                            return alpha
                return alpha
            else:
                # print('okay')
                beta = -h_5
                return beta
            
        for x, y in move_list:
            self.chessboard[x][y] = color
            self.score_reevaluate(x, y)
            new_score = self.search(-color, depth +1 , alpha, beta)
            if new_score > self.global_max and depth == 0 and color == self.color:
                self.candidate_list.append( (x, y) )
                self.global_max = new_score
            self.chessboard[x][y] = COLOR_NONE
            self.score_reevaluate(x,y)
            if color == self.color:
                if new_score > alpha:
                    alpha = new_score
                if alpha >= beta:
                    return alpha
            else:
                if new_score < beta:
                    beta = new_score
                if alpha >= beta:
                    return beta   
        if color == self.color:
            return alpha
        else:
            return beta

    def score_reevaluate(self, x, y):
        # when changing the color on the board, we have to reevaluate the score.
        # And the points are evaluated around the points
        for dx, dy  in self.direction:
            x1 = x + dx
            y1 = y + dy
            while 0 <= x1 < self.chessboard_size and 0 <= y1 < self.chessboard_size:
                count_ = 0
                if count_ >= 5:
                    break
                if self.chessboard[x1][y1] == COLOR_NONE:
                    m_s = self.point_evaluate(x1, y1, self.color)
                    e_s = self.point_evaluate(x1, y1, -self.color)
                    self.my_score[x1][y1] = m_s
                    self.en_score[x1][y1] = e_s
                    count_ += 1
                x1 = x1 + dx
                y1 = y1 + dy

    def init_move(self):
        protential_list  = list()
        move_list = list()
        for i in range(self.chessboard_size):
            for j in range(self.chessboard_size):
                if self.chessboard[i][j] == COLOR_NONE:
                    m_s = self.point_evaluate(i, j, self.color)
                    e_s = self.point_evaluate(i, j, -self.color)
                    self.my_score[i][j] = m_s
                    self.en_score[i][j] = e_s
                    protential_list.append((self.my_score[i][j]+self.en_score[i][j]+e_s+self.position_value[i][j], i, j))

        protential_list.sort( reverse = True)
        # print(protential_list)
        max_length = len(protential_list)
        for i in range(self.max_node):
            if i == max_length:
                break
            move_list.append((protential_list[i][1], protential_list[i][-1]) )
            # print(self.en_score[protential_list[i][1]][protential_list[i][-1]])
        # print(move_list)
        return move_list


    def move(self):
        protential_list = list()
        move_list = list()
        for i in range(self.chessboard_size):
            for j in range(self.chessboard_size):
                if self.chessboard[i][j] == COLOR_NONE:
                    protential_list.append((self.my_score[i][j]+self.en_score[i][j]+self.position_value[i][j], i, j))
        protential_list.sort(reverse = True)
        n = len(protential_list)
        for i in range(self.max_node):
            if i == n:
                break
            move_list.append( (protential_list[i][1], protential_list[i][-1]) )
        # print(protential_list)
        return move_list


    def global_evaluate(self):
        s = 0
        for i in range(self.chessboard_size):
            for j in range(self.chessboard_size):
                if self.chessboard[i][j] == COLOR_NONE:
                    s += self.my_score[i][j] - self.en_score[i][j]
        return s


    def point_evaluate(self, x, y, color):
        counter = {
            'h_5': 0,  
            'h_4': 0,  
            'c_4': 0,  
            'tc_4': 0,   
            'h_3': 0,  
            'c_3': 0,  
            'tc_3': 0,  
            'h_2': 0,  
            'c_2': 0 
        }
        self.evaluate_horizontal(x, y, counter, color)
        self.evaluate_vertical(x, y, counter, color)
        self.evaluation_left(x, y, counter, color)
        self.evaluation_right(x, y, counter, color)
        # 必杀局面
        c_4 = counter['tc_4'] + counter['c_4']
        c_3 = counter['h_3'] + counter['tc_3']
        sum = 0
        if counter['h_5'] >= 1:
            # 连5
            return h_5
        # 冲4，活4，冲4加活3
        elif counter['h_4'] >= 1:
            return (h_4 + 100)
        elif c_4 and c_3:
            return (h_4 + 50)
        elif c_4 >= 2:
            return (h_4 + 100)
        elif c_3 >= 2:
            # 双冲3
            return h_4
        else:
            # 普通局面
            sum = counter['c_2'] * c_2 + counter['h_2'] * h_2 \
                  + counter['h_3'] * h_3 + counter['tc_3'] * tc_3 \
                  + counter['c_3'] * c_3 + counter['tc_4'] * tc_4 \
                  + counter['c_4'] * c_4 + counter['h_5'] * h_5 + counter['h_4'] * h_4
        return sum


    def evaluate_horizontal(self, x, y, counter, color):
        line = np.zeros((self.chessboard_size, 1))
        for i in range(self.chessboard_size):
            line[i] = self.chessboard[x][i]
        self.evaluation_line(line, self.chessboard_size, y, counter, color)

    def evaluate_vertical(self, x, y, counter, color):
        line = np.zeros((self.chessboard_size, 1))
        for i in range(self.chessboard_size):
            line[i] = self.chessboard[i][y]
        self.evaluation_line(line, self.chessboard_size, x, counter, color)

    def evaluation_left(self, x, y, counter, color):
        line = np.zeros((self.chessboard_size, 1))
        v = h = 0
        if x > y:
            v = 0
            h = x - y
        else:
            v = y - x
            h = 0
        num = 0
        for i in range(self.chessboard_size+1):
            num = i
            x_ = h + i
            y_ = v + i
            if x_ > self.chessboard_size -1 or y_ > self.chessboard_size -1:
                # print("test")
                break
            line [i] = self.chessboard[x_][y_]
        
        self.evaluation_line(line, num, y - v, counter, color)

    def evaluation_right(self, x, y, counter, color):
        line = np.zeros((self.chessboard_size, 1))
        v = h = 0
        if  (self.chessboard_size -1)- x> y  :
            v = 0
            h = x + y
            num = 0
            for i in range(self.chessboard_size+1):
                num = i
                x_ = h-i
                y_ = v+i
                if x_ < 0 or y_ > self.chessboard_size -1:
                    break
                line[i] = self.chessboard[x_][y_]
            self.evaluation_line(line, num, y-v, counter, color)
        else:
            v = y - (self.chessboard_size -1) + x
            h = self.chessboard_size - 1
            num = 0
            for i in range(self.chessboard_size+1):
                num = i
                x_ = h-i
                y_ = v+i
                if x_ < 0 or y_ > self.chessboard_size -1:
                    break
                line[i] = self.chessboard[x_][y_]
            self.evaluation_line(line, num, y-v, counter, color)

    def evaluation_line(self, line, num, position, counter, color):
        if num < 5:
            return
        for i in range(num, self.chessboard_size):
            line[i] = 15
        color1 = color
        left_color = [0, 0]
        left_empty = [0, 0]
        right_color = [0, 0]
        right_empty = [0, 0]
        p1 = position - 1
        while p1 >= 0 and line[p1] == color1:
            p1 = p1 - 1
            left_color[0] += 1
        while p1 >= 0 and line[p1] == COLOR_NONE:
            p1 = p1 - 1
            left_empty[0] += 1
        while p1 >= 0 and line[p1] == color1:
            p1 = p1 - 1
            left_color[1] += 1
        while p1 >= 0 and line[p1] ==COLOR_NONE:
            p1 = p1 -1
            left_empty[1] += 1

        p2 = position +1 
        while p2 < num and line[p2] == color1:
            p2 = p2 + 1
            right_color[0] += 1
        while p2 < num and line[p2] == COLOR_NONE:
            p2 = p2 + 1
            right_empty[0] += 1
        while p2 < num and line[p2] == color1:
            p2 = p2 + 1
            right_color[1] += 1
        while p2 < num and line[p2] == COLOR_NONE:
            p2 = p2 + 1
            right_empty[1] += 1

        linked_range = left_color[0] + right_color[0] + 1
        # The first linked points appear on the board.
        if linked_range >= 5:
            counter['h_5'] += 1

        elif linked_range == 4:
            if left_empty[0] >= 1 and right_empty[0] >= 1:
                counter['h_4'] += 1
            elif left_empty[0] >= 1 or right_empty[0] >= 1:
                counter['c_4'] += 1

        elif linked_range == 3:
            tc_4 = False
            if ( left_color[1] >= 1 and left_empty[0] == 1 ) or (right_empty[0] == 1 and right_color[1] >= 1 ):
                counter['tc_4'] += 1
                tc_4 = True
            if ( tc_4 == False) and (left_empty[0] + right_empty[0] >= 3) and left_empty[0] >= 1 and right_empty[0] >= 1:
                counter['h_3'] += 1
            elif left_color[0] + right_empty[0] >= 1:
                counter['c_3'] += 1
        elif linked_range == 2:
            # Here comes to the hardest part
            tc_4 = False
            if (left_empty[0] == 1 and left_color[1] >= 2) or (right_empty[0] == 1 and right_color[1] >= 2):
                counter['tc_4'] += 1
                # 跳冲4
                tc_4 = True
            if (tc_4 == False) and (
                    (left_color[1] == 1 and left_empty[0] == 1 and right_empty[0] >= 1 and left_empty[1] >= 1) or
                    (right_color[1] == 1 and right_empty[0] == 1 and left_empty[0] >= 1 and right_empty[1] >= 1)):
                counter['tc_3'] += 1
                # 跳冲3
            elif (left_empty[0] == 1 and left_color[1] == 1 and right_empty[0] + left_empty[1] >= 1) or (
                    right_empty[0] == 1 and right_color[1] == 1 and right_empty[1] + left_empty[0] >= 1):
                counter['c_3'] += 1
                # 冲3
            if (left_empty[0] + right_empty[0] >= 4 and left_empty[0] >= 1 and right_empty[0] >= 1):
                counter['h_2'] += 1
                # 活2
        elif linked_range == 1:
            tc_4 = False
            if (left_empty[0] == 1 and left_color[1] >= 3) or (right_empty[0] == 1 and right_color[1] >= 3):
                counter['tc_4'] += 1
                tc_4 = True
            if (not tc_4) and (
                    left_empty[0] == 1 and left_color[1] == 2 and left_empty[1] >= 1 and right_empty[0] >= 1) or (
                    right_empty[0] == 1 and right_color[1] == 2 and right_empty[1] >= 1 and left_empty[0] >= 1):
                counter['tc_3'] += 1
                #跳冲3
            elif (right_empty[0] == 1 and right_color[1] == 2 and left_empty[0] + right_empty[1] >= 1) or (
                    left_empty[0] == 1 and left_color[1] == 2 and left_empty[1] + right_empty[0] >= 1):
                counter['c_3'] += 1
                #冲3
            if (left_empty[0] == 1 and left_color[1] == 1 and right_empty[0] + left_empty[1] >= 3 and right_empty[
                0] >= 1 and left_empty[1] >= 1) or (
                    right_empty[0] == 1 and right_color[1] == 1 and left_empty[0] + right_empty[1] >= 3 and left_empty[
                0] >= 1 and right_empty[1] >= 1):
                counter['c_2'] += 1
            if (left_empty[0] == 2 and left_color[1] == 1 and right_empty[0] >= 1 and left_empty[1] >= 1) or (
                    right_empty[0] == 2 and right_color[1] == 1 and left_empty[0] >= 1 and right_empty[1] >= 1):
                counter['c_2'] += 1

