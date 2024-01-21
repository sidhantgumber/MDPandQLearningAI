import random
import sys

DEFAULT_STATE = '       | ###  -| # #  +| # ####|       '

class Action:
    def __init__(self, name, dx, dy):
        self.name = name
        self.dx = dx
        self.dy = dy

ACTIONS = [
    Action('UP', 0, -1),
    Action('RIGHT', +1, 0),
    Action('DOWN', 0, +1),
    Action('LEFT', -1, 0)
]

class State:
    def __init__(self, env, x, y):
        self.env = env
        self.x = x
        self.y = y

    def clone(self):
        return State(self.env, self.x, self.y)

    def is_legal(self, action):
        new_x = self.x + action.dx
        new_y = self.y + action.dy

        if 0 <= new_x < self.env.x_size and 0 <= new_y < self.env.y_size:
            cell = self.env.get(new_x, new_y)
            return cell is not None and cell in ' +-'
        else:
            return False

    def legal_actions(self, actions):
        legal = []
        for action in actions:
            if self.is_legal(action):
                legal.append(action)
        return legal

    def reward(self):
        cell = self.env.get(self.x, self.y)
        if cell is None:
            return None
        elif cell == '+':
            return +10
        elif cell == '-':
            return -10
        else:
            return 0

    def at_end(self):
        return self.reward() != 0

    def execute(self, action):
        self.x += action.dx
        self.y += action.dy
        return self

    def __str__(self):
        tmp = self.env.get(self.x, self.y)
        self.env.put(self.x, self.y, 'A')
        s = ' ' + ('-' * self.env.x_size) + '\n'
        for y in range(self.env.y_size):
            s += '|' + ''.join(self.env.row(y)) + '|\n'
        s += ' ' + ('-' * self.env.x_size)
        self.env.put(self.x, self.y, tmp)
        return s

class Env:
    def __init__(self, string):
        self.grid = [list(line) for line in string.split('|')]
        self.x_size = len(self.grid[0])
        self.y_size = len(self.grid)
        self.string = string

    def get(self, x, y):
        if 0 <= x < self.x_size and 0 <= y < self.y_size:
            return self.grid[y][x]
        else:
            return None

    def put(self, x, y, val):
        if 0 <= x < self.x_size and 0 <= y < self.y_size:
            self.grid[y][x] = val

    def row(self, y):
        return self.grid[y]

    def random_state(self):
        valid_states = [(x, y) for y in range(self.y_size) for x in range(self.x_size)
                        if self.get(x, y) == ' ']
        x, y = random.choice(valid_states)
        return State(self, x, y)

class QTable:
    def __init__(self, env, actions):
        self.actions = actions
        self.q_table = {}
        self.env = env
        for y in range(env.y_size):
            for x in range(env.x_size):
                if env.get(x, y) == ' ':
                    self.q_table[(x, y)] = [0.0 for _ in range(len(actions))]

    def check_state_exist(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0 for _ in self.actions]

    def get_q(self, state, action):
        state_key = (state.x, state.y) if isinstance(state, State) else state
        self.check_state_exist(state_key)
        return self.q_table[state_key][self.actions.index(action)]

    def get_q_row(self, state):
        state_key = (state.x, state.y) if isinstance(state, State) else state
        self.check_state_exist(state_key)
        return self.q_table[state_key]

    def set_q(self, state, action, val):
        state_key = (state.x, state.y) if isinstance(state, State) else state
        self.check_state_exist(state_key)
        self.q_table[state_key][self.actions.index(action)] = val

    def learn_episode(self, alpha=.10, gamma=.90):
        state = self.env.random_state()
        while not state.at_end():
            legal_actions = state.legal_actions(self.actions)
            if not legal_actions:
                break
            action = random.choice(legal_actions)
            old_state = state.clone()
            state.execute(action)
            reward = state.reward()
            old_state_key = (old_state.x, old_state.y)
            state_key = (state.x, state.y)
            old_q = self.get_q(old_state_key, action)
            next_max_q = max(self.get_q_row(state_key), default=0)
            new_q = (1 - alpha) * old_q + alpha * (reward + gamma * next_max_q)
            self.set_q(old_state_key, action, new_q)
            print(state)

    def learn(self, episodes, alpha=.10, gamma=.90):
        for _ in range(episodes):
            self.learn_episode(alpha, gamma)

    def __str__(self):
        actions_header = '\t'.join([action.name for action in self.actions])
        q_table_str = f"State\t{actions_header}\n"
        for state in sorted(self.q_table.keys()):
            q_values = ['{:.2f}'.format(q) if q != 0 else '----' for q in self.q_table[state]]
            q_table_str += f"{state}: {'\t'.join(q_values)}\n"
        return q_table_str



def getStateFromEnvironment(env):
    state = State(env,1,0)
    return state


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        env = Env(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_STATE)
        if cmd == 'learn':
            qt = QTable(env, ACTIONS)
            qt.learn(100)
            print(qt)

        if cmd == 'print':
            print(getStateFromEnvironment(env))
