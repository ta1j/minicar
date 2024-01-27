import numpy as np


file_name = "training_data.npy"
training_data = np.load(file_name, allow_pickle=True)

np.random.shuffle(training_data)
print("final_data size:", len(training_data))
np.save("BGR2GRAY.npy", training_data[0])
np.save("STEERING.npy", training_data[2])