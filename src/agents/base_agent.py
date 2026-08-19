from abc import ABC, abstractmethod


class BaseAgent(ABC):

    def __init__(self, name, goal):
        self.name = name
        self.goal = goal

    @abstractmethod
    def run(self, context):
        pass