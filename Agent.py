from collections import deque
import random
import numpy as np
from keras import Sequential

from keras.layers import Dense
from keras.optimizers import Adam


class DQN_agent:
    def __init__(self, params):
        self.env_info = {"state_space": params["state_space"]}
        self.epsilon = params['epsilon']
        self.gamma = params['gamma']
        self.batch_size = params['batch_size']
        self.epsilon_min = params['epsilon_min']
        self.epsilon_decay = params['epsilon_decay']
        self.learning_rate = params['learning_rate']
        self.layer_sizes = params['layer_sizes']
        self.memory = deque(maxlen=2500)
        self.action_space = 8
        self.state_space = 16
        if params["name"]:
            self.load_model(params.get("name"))
        else:
            self.model = self.build_model()

    def build_model(self):
        model = Sequential()
        model.add(Dense(self.layer_sizes[0], input_shape=(self.state_space,), activation='relu'))
        for i in range(1, len(self.layer_sizes)):
            model.add(Dense(self.layer_sizes[i], activation='relu'))
        model.add(Dense(self.action_space, activation='softmax'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        model.summary()
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def get_action(self, state):

        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_space)
        act_values = self.model.predict([state])
        return np.argmax(act_values[0])

    def replay(self):

        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)

        states = np.array([i[0] for i in minibatch])
        actions = np.array([i[1] for i in minibatch])
        rewards = np.array([i[2] for i in minibatch])
        next_states = np.array([i[3] for i in minibatch])
        dones = np.array([i[4] for i in minibatch])

        states = np.squeeze(states)
        next_states = np.squeeze(next_states)

        targets = rewards + self.gamma * (np.amax(self.model.predict_on_batch(next_states), axis=1)) * (1 - dones)
        targets_full = self.model.predict_on_batch(states)

        print(f"targets: {targets}")

        ind = np.array([i for i in range(self.batch_size)])
        targets_full[[ind], [actions]] = targets

        print(f"targets full: {targets_full}")

        self.model.fit(states, targets_full, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_model(self, data):
        from os import mkdir
        from zlib import crc32

        try:
            mkdir("../models/")
        except Exception:
            pass

        tmp = ""
        for i in data:
            tmp += str(i[0]+i[1])

        name = crc32(bytes(tmp, "utf-8"))
        name = str(name) + "model.keras"
        self.model.save(name)
        print("model saved")

    def load_model(self, name):
        from tensorflow import keras
        self.model = keras.models.load_model(name)
        print("loaded")

    def convert_onnx(self, data):
        import keras2onnx
        from os import mkdir
        from zlib import crc32
        import onnx

        try:
            mkdir("../models/")
        except Exception:
            pass

        tmp = ""
        for i in data:
            tmp += str(i[0]+i[1])

        name = crc32(bytes(tmp, "utf-8"))

        onnx_model = keras2onnx.convert_keras(self.model,  # keras model
                                              name="Snake_model_"+str(name/1000),
                                              # the converted ONNX model internal name
                                              target_opset=9,  # the ONNX version to export the model to
                                              channel_first_inputs=None  # which inputs to transpose from NHWC to NCHW
                                              )
        name = "Snake_model_"+str(name)+".onnx"
        onnx.save_model(onnx_model, name)
        print("onnx model saved")
