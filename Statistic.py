import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
from collections import OrderedDict


class Statistic:
    def __init__(self):
        self.score_data = OrderedDict()
        self.batch_data = []
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.ax.set_title("Learning Curve", fontsize=15)
        self.ax.set_xlabel('Episodes', fontsize=14)
        self.ax.set_ylabel("Sum of\nreward\nduring\nepisode", rotation=0, labelpad=40, fontsize=14)

    def save_stat(self):
        pass # сохранение статистики в файл

    def load_stat(self):
        pass #  по имени файла взять стату

    def smooth(self, data, k):
        if isinstance(data, pd.DataFrame):
            num_episodes = data.shape[1]
            num_runs = data.shape[0]

            smoothed_data = np.zeros((num_runs, num_episodes))

            for i in range(num_episodes):
                if i < k:
                    smoothed_data[:, i] = np.mean(data[:, :i + 1], axis=1)
                else:
                    smoothed_data[:, i] = np.mean(data[:, i - k:i + 1], axis=1)

            return smoothed_data
        else:
            num_episodes = len(data)
            num_runs = 1

            smoothed_data = np.zeros((num_runs, num_episodes))

            for i in range(num_episodes):
                if i < k:
                    smoothed_data[:, i] = np.mean(data[:i + 1])
                else:
                    smoothed_data[:, i] = np.mean(data[i - k:i + 1])

            return smoothed_data

    def plot_stat(self, k=5):
        plt_agent_sweeps = []
        max_list = []
        plt.ion()
        plt.show()

        for data_name in self.score_data:
            sum_reward_data = self.score_data[data_name]

            smoothed_sum_reward = self.smooth(data=sum_reward_data, k=k)
            max_list.append(max(smoothed_sum_reward[0]))
            mean_smoothed_sum_reward = np.mean(smoothed_sum_reward, axis=0)

            plot_x_range = np.arange(0, mean_smoothed_sum_reward.shape[0])
            graph_current_agent_sum_reward, = self.ax.plot(plot_x_range, mean_smoothed_sum_reward[:], label=data_name)
            plt_agent_sweeps.append(graph_current_agent_sum_reward)

        max_to_hundred = int(math.ceil(max(max_list) / 100.0)) * 100

        self.ax.legend(handles=plt_agent_sweeps, fontsize=13)
        self.ax.set_ylim([-250, max_to_hundred])
        plt.draw()
        plt.pause(0.001)

    def update_stat(self, sum_rewards):
        self.score_data["stat"] = sum_rewards

