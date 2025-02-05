import os
from rich import print
import numpy as np
import math


"""
A class that represents a configuration object.

Attributes:
    * Any attributes that are passed to the `__init__` method.

Methods:
    * Any methods that are needed to access or modify the attributes of the object.
"""

class Config:
    def __init__(self, **kwargs):
        """
        Initializes a Config object.

        Args:
            * Any attributes that are passed to the `__init__` method.
        """

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        """
        Prints all attributes each in a separate line.
        """

        string = ""
        for key, value in self.__dict__.items():
            string += f"{key}: {value}\n"
        return string




class Preprocess:
    def __init__(self, n_emission: int = 10) -> None:
        self.n_emission = n_emission

    def extract_observations(self, sample):
        sample_points = sample["points"]
        
        # Add first point to the end of array
        sample_points = np.concatenate((sample_points, sample_points[0:1]))
        n_points = len(sample_points)
        
        #? Calculate the degree of each point regarding the next point
        degrees = []
        for i in range(1,n_points):
            x0,y0 = sample_points[i-1]
            x1,y1 = sample_points[i]
            degree = math.atan2(y1-y0, x1-x0) * 180 / np.pi
            if degree < 0:
                degree += 360
            degrees.append(degree)

        diff_degrees = []
        degrees = np.concatenate((degrees, degrees[0:1]))
        for i in range(1,n_points):
            diff_degree = degrees[i-1] - degrees[i]
            if diff_degree < 0:
                diff_degree += 360

            if diff_degree > 180:
                diff_degree -= 180

            diff_degrees.append(diff_degree)
        return diff_degrees


    def quantize_observation(self, features):
        emmision_span = 180 // self.n_emission + 1
        features = [f"E{int(f // emmision_span)}" for f in features]
        return features
    
    def preprocess_single_sample(self, sample):
        observations = self.extract_observations(sample)
        observations = self.quantize_observation(observations)
        return {"observations": observations, "label": sample["label"]}


    def __call__(self, data_path: str = None):
        # Load the data
        data = np.load(data_path, allow_pickle=True)

        self.raw_train_samples = []
        for points, label in zip(data["points_train"], data["labels_train"]):
            self.raw_train_samples.append({"points": points, "label": label})

        self.raw_test_samples = []
        for points, label in zip(data["points_test"], data["labels_test"]):
            self.raw_test_samples.append({"points": points, "label": label})

        self.train_samples = [self.preprocess_single_sample(sample) for sample in self.raw_train_samples]
        np.random.shuffle(self.train_samples)
        self.test_samples = [self.preprocess_single_sample(sample) for sample in self.raw_test_samples]

if __name__ == "__main__":
    pp = Preprocess("./dataset/data.npz")
    pp.preprocess()
    print(pp.train_samples)
