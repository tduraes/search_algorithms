import fileinput
import copy
import time
from Queue import PriorityQueue
from sys import getsizeof


def manhattan(state, goal_state):
    md = 0
    for line in state:
        for item in line:
            if item is not 'x':
                for line2 in goal_state:
                    for item2 in line2:
                        if item2 == item:
                            md += abs(line2.index(item2)-line.index(item)) + abs(goal_state.index(line2)-state.index(line))
    return md


def a_search(init_state, goal_state):
    tests = 0
    nodes = PriorityQueue()
    nodes.put((0, Node(init_state, None, None)))
    while not nodes.empty():
        node = nodes.get()[1]
        tests += 1
        if tests % 10000 == 0:
            print tests, "tests..."
        if node.state == goal_state:
            print "Tested", tests, "nodes."
            print "Queue final size:", getsizeof(nodes)
            print "Path size: ", len(node.path)
            return node.path
        new_nodes = node.expand('A', 0)
        for n in new_nodes:
            nodes.put((n.depth + manhattan(n.state, goal_state), n))
    return False


def general_search(init_state, goal_state, method, limit):
    root = Node(init_state, None, None)
    nodes = Queue(root)
    tests = 0
    visited = []
    while not nodes.is_empty():
        node = nodes.remove_front()
        if method != 'IDDFS':
            if node.state not in visited:
                visited.append(node.state)
        tests += 1
        if tests % 100000 == 0:
            print tests, "tests..."
        if node.state == goal_state:
            print "Tested", tests, "nodes."
            print "Queue final size:", getsizeof(nodes.contents)
            print "Path size: ", len(node.path)
            return node.path

        new_nodes = []
        for n in node.expand(method, limit):
            if method != 'IDDFS':
                if n.state not in visited:
                    new_nodes.append(n)
            else:
                new_nodes.append(n)
        if method != 'G':
            nodes.queueing_fn(new_nodes, method)
        else:
            nodes.informed_queue(new_nodes, method, manhattan, goal_state)
    return False


def ids(init_state, goal_state):
    d = 1
    while d < 1000:
        print d
        result = general_search(init_state, goal_state, 'IDDFS', d)
        if result is not None and result is not False:
            return result
        d += 1
    return False


class Node:
    def __init__(self, state, parent, operator):
        self.state = state
        self.parent = parent
        self.operator = operator
        if parent is None:
            self.path = []
            self.depth = 0
        else:
            self.path = copy.deepcopy(parent.path)
            self.path.append(operator)
            self.depth = parent.depth + 1
        self.path_cost = 0

    def expand(self, method, limit):
        if method == 'IDDFS':
            states = next_states(self.state)
            nodes = []
            for s in states:
                node = Node(s[0], self, s[1])
                if node.depth <= limit:
                    nodes.append(node)
            return nodes
        else:
            states = next_states(self.state)
            nodes = []
            for s in states:
                node = Node(s[0], self, s[1])
                nodes.append(node)
            return nodes

    def output_node(self):
        print "Node State:", self.state
        print "Node Parent:", self.parent
        print "Node Operator:", self.operator


class Queue:
    def __init__(self, node):
        self.contents = [node]

    def remove_front(self):
        return self.contents.pop(0)

    def is_empty(self):
        return self.contents == []

    def queueing_fn(self, new_content, queue_type):
        if queue_type == 'BFS':
            for node in new_content:
                self.contents.append(node)
        elif queue_type == 'DFS' or queue_type == 'IDDFS':
            self.contents.reverse()
            new_content.reverse()
            for node in new_content:
                self.contents.append(node)
            self.contents.reverse()

    def informed_queue(self, new_content, method, eval_f, goal_state):
        evaluated = []
        for node in new_content:
            if method == 'G':
                evaluated.append(eval_f(node.state, goal_state))
            else:
                evaluated.append(node.depth+eval_f(node.state, goal_state))
        new_sorted = [x for (y, x) in sorted(zip(evaluated, new_content))]
        self.contents.reverse()
        new_sorted.reverse()
        for node in new_sorted:
            self.contents.append(node)
        self.contents.reverse()


def display_state(state):
    for line in state:
        for item in line:
            print item,
        print "\n"


def whitespace_position(state):
    for line in state:
        if 'x' in line:
            return state.index(line), line.index('x')


def next_states(state):
    next_s = []
    (x, y) = whitespace_position(state)
    if x != 0:
        tmp = copy.deepcopy(state)
        tmp[x-1][y], tmp[x][y] = tmp[x][y], tmp[x-1][y]
        next_s.append((tmp, 'D'))
    if x != 2:
        tmp = copy.deepcopy(state)
        tmp[x+1][y], tmp[x][y] = tmp[x][y], tmp[x+1][y]
        next_s.append((tmp, 'U'))
    if y != 0:
        tmp = copy.deepcopy(state)
        tmp[x][y-1], tmp[x][y] = tmp[x][y], tmp[x][y-1]
        next_s.append((tmp, 'R'))
    if y != 2:
        tmp = copy.deepcopy(state)
        tmp[x][y+1], tmp[x][y] = tmp[x][y], tmp[x][y+1]
        next_s.append((tmp, 'L'))
    return next_s


def is_solvable(state, goal):
    inversions = 0
    item_list = []
    for line in state:
        item_list += line
    item_list.remove('x')
    goal_list = []
    for line in goal:
        goal_list += line
    goal_list.remove('x')
    for i in range(0, 8):
        for j in range(i, 8):
            if goal_list.index(item_list[i]) > goal_list.index(item_list[j]):
                inversions += 1
    return inversions % 2 == 0


def main():
    init_state = []
    goal_state = []

    input_file = fileinput.input()

    for line in range(3):
        row = list(input_file[line].strip())
        init_state.append(row)
    for line in range(3, 6):
        row = list(input_file[line].strip())
        goal_state.append(row)

    method = input_file[6].strip()

    if is_solvable(init_state, goal_state):
        if method == 'IDDFS':
            print ids(init_state, goal_state)
        elif method == 'A':
            print a_search(init_state, goal_state)
        else:
            print general_search(init_state, goal_state, method, 0)
    else:
        print "The problem is unsolvable."


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print "Time: ", end - start, "ms."