import sys
import time

import win32file
import win32pipe

from Agent import DQN_agent
from Statistic import Statistic


class Environment:
    def __init__(self, params):
        self.snake_body = []  # list[list[x, y]]
        self.apple = []  # list[x, y]
        self.obstacles = []  # list[list[x, y]]
        self.direction = "D"
        self.SIZE = 40
        self.snake_event = 0
        self.agent = DQN_agent(params)
        self.stat = Statistic()

        self.pipe_name = r'\\.\pipe\SnakePipe_'

        self.pipe_handle = win32pipe.CreateNamedPipe(
            self.pipe_name,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            win32pipe.PIPE_UNLIMITED_INSTANCES,
            65536,
            65536,
            300,
            None
        )

    def send_action(self, action):
        # Отправка данных клиенту
        response = str(action)
        print(f"response: {response}")
        try:
            pass
            win32file.WriteFile(self.pipe_handle, response.encode())
            win32file.FlushFileBuffers(self.pipe_handle)
        except Exception as e:
            self.agent.save_model(self.snake_body)
            win32pipe.DisconnectNamedPipe(self.pipe_handle)
            win32file.CloseHandle(self.pipe_handle)
            time.sleep(5)
            sys.exit(0)

    def distance(self, obj):
        """

        :param obj:
        :type obj: list[float]
        :return:
        """
        return (obj[0] - self.snake_body[0][0]) * (obj[0] - self.snake_body[0][0]) + (
                obj[1] - self.snake_body[0][1]) * (
                obj[1] - self.snake_body[0][1])

    def get_data(self):

        try:
            data = win32file.ReadFile(self.pipe_handle, 2000)
        except Exception as e:
            self.agent.save_model(self.snake_body)
            win32pipe.DisconnectNamedPipe(self.pipe_handle)
            win32file.CloseHandle(self.pipe_handle)
            time.sleep(5)
            sys.exit(0)

        data = data[1].decode("ascii")
        data.strip("\n")
        data.strip(" ")

        if data == "-1":
            return -1

        data = data.split("//")

        self.snake_body = []
        line = data[0].split("/")
        for i in line:
            x, y = i.split(".")
            x_n, x_m = x.split(",")
            y_n, y_m = y.split(",")
            x = float(x_n) + float("0." + x_m)
            y = float(y_n) + float("0." + y_m)
            self.snake_body.append([x, y])

        line = data[1].strip("/")
        x, y = line.split(".")
        x_n, x_m = x.split(",")
        y_n, y_m = y.split(",")
        x = float(x_n) + float("0." + x_m)
        y = float(y_n) + float("0." + y_m)
        self.apple = [x, y]

        self.direction = data[2]

        self.snake_event = int(data[3])

        return 0

    def get_state(self):

        # wall check
        if self.snake_body[0][0] + 4 >= self.SIZE:
            wall_up, wall_down = 1, 0
        elif self.snake_body[0][0] - 4 <= 0:
            wall_up, wall_down = 0, 1
        else:
            wall_up, wall_down = 0, 0

        if self.snake_body[0][1] + 4 >= self.SIZE:
            wall_right, wall_left = 1, 0
        elif self.snake_body[0][1] - 4 <= 0:
            wall_right, wall_left = 0, 1
        else:
            wall_right, wall_left = 0, 0

        # body close
        body_up = 0
        body_right = 0
        body_down = 0
        body_left = 0
        if len(self.snake_body) > 3:
            for body in self.snake_body[3:]:
                if self.distance(body) <= 6:
                    if body[1] < self.snake_body[0][1]:
                        body_down = 1
                        print("D")
                    elif body[1] > self.snake_body[0][1]:
                        body_up = 1
                        print("U")
                    if body[0] < self.snake_body[0][0]:
                        body_left = 1
                        print("L")
                    elif body[0] > self.snake_body[0][0]:
                        body_right = 1
                        print("R")

        # state: apple_up, apple_right, apple_down, apple_left,
        # obstacle_up, obstacle_right, obstacle_down, obstacle_left,
        # direction_up, direction_right, direction_down, direction_left
        if self.agent.env_info['state_space'] == 'coordinates':
            state = [self.apple[0], self.apple[1], self.snake_body[0][0], self.snake_body[0][1],
                     int(wall_up or body_up), int(wall_right or body_right), int(wall_down or body_down),
                     int(wall_left or body_left),
                     int(self.direction == 'U'), int(self.direction == 'R'),
                     int(self.direction == 'D'), int(self.direction == 'L'),
                     int(self.direction == 'LU'), int(self.direction == 'RU'),
                     int(self.direction == 'RD'), int(self.direction == 'LD')]
        elif self.agent.env_info['state_space'] == 'no body knowledge':
            state = [int(self.snake_body[0][1] < self.apple[1]), int(self.snake_body[0][0] < self.apple[0]),
                     int(self.snake_body[0][1] > self.apple[1]), int(self.snake_body[0][0] > self.apple[0]),
                     wall_up, wall_right, wall_down, wall_left,
                     int(self.direction == 'U'), int(self.direction == 'R'),
                     int(self.direction == 'D'), int(self.direction == 'L'),
                     int(self.direction == 'LU'), int(self.direction == 'RU'),
                     int(self.direction == 'RD'), int(self.direction == 'LD')]
        else:
            state = [int(self.snake_body[0][1] < self.apple[1]), int(self.snake_body[0][0] < self.apple[0]),
                     int(self.snake_body[0][1] > self.apple[1]), int(self.snake_body[0][0] > self.apple[0]),
                     int(wall_up or body_up), int(wall_right or body_right), int(wall_down or body_down),
                     int(wall_left or body_left),
                     int(self.direction == 'U'), int(self.direction == 'R'),
                     int(self.direction == 'D'), int(self.direction == 'L'),
                     int(self.direction == 'LU'), int(self.direction == 'RU'),
                     int(self.direction == 'RD'), int(self.direction == 'LD')]

        return state

    def reset(self):
        self.snake_body = []
        self.apple = []
        self.obstacles = []
        self.direction = "D"

    def check_reward(self, prev_dist):
        if self.snake_event == -1:
            return -100, 1
        elif self.snake_event:
            return 100, 0
        else:
            if self.distance(self.apple) > prev_dist:
                return -1, 0
            else:
                return 1, 0


def train_dqn(params):
    episode = 0
    sum_of_rewards = []
    ENV = Environment(params)

    print('Ожидание подключения клиента...')
    win32pipe.ConnectNamedPipe(ENV.pipe_handle, None)
    print('Клиент подключен.')
    try:
        ENV.get_data()
        state = ENV.get_state()
        prev_dist = ENV.distance(ENV.apple)

        score = 0
        max_steps = 100000
        for i in range(max_steps):
            action = ENV.agent.get_action(state)
            ENV.send_action(action)

            prev_state = state.copy()
            ENV.get_data()
            next_state = ENV.get_state()

            reward, done = ENV.check_reward(prev_dist)

            prev_dist = ENV.distance(ENV.apple)

            score += reward
            ENV.agent.remember(state, action, reward, next_state, done)
            state = next_state
            if params['batch_size']:
                ENV.agent.replay()
            if done:
                print(f'final state before dying: {str(prev_state)}')
                print(f'episode: {episode + 1}, score: {score}')
                episode += 1
                sum_of_rewards.append(score)
                ENV.stat.update_stat(sum_of_rewards)
                ENV.stat.plot_stat()
                score = 0

        ENV.agent.save_model(ENV.snake_body)
        win32pipe.DisconnectNamedPipe(ENV.pipe_handle)
        win32file.CloseHandle(ENV.pipe_handle)
        return sum_of_rewards

    except Exception as e:
        print(f"Exception: {e}")
        ENV.agent.save_model(ENV.snake_body)
        win32pipe.DisconnectNamedPipe(ENV.pipe_handle)
        win32file.CloseHandle(ENV.pipe_handle)
        time.sleep(5)
        sys.exit(0)


def play_loaded(params):
    ENV = Environment(params)

    print('Ожидание подключения клиента...')
    win32pipe.ConnectNamedPipe(ENV.pipe_handle, None)
    print('Клиент подключен.')

    while True:
        ENV.get_data()
        state = ENV.get_state()
        action = ENV.agent.get_action(state)
        ENV.send_action(action)


def main():
    params = dict()
    params['name'] = None # r"C:\Users\andry\PycharmProjects\snake_game_ai\Best_models\m21a9.keras"
    params['epsilon'] = 1  # 1
    params['gamma'] = 0.95
    params['batch_size'] = 100
    params['epsilon_min'] = 0.001
    params['epsilon_decay'] = .995
    params['learning_rate'] = 0.0002
    params['layer_sizes'] = [128, 128, 128]
    params['state_space'] = ""

    # play_loaded(params)
    train_dqn(params)


if __name__ == '__main__':
    main()
