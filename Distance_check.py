import numpy as np
class distance_check():

    def __init__(self, distance_limit, items_considered) -> None:
        self.distance_limit = distance_limit
        self.distance_all = []
        self.items_considered = items_considered

    def distance_store(self, distance: float) -> list:
        self.distance_all.append(distance)

    def avg_distance(self) -> float:
        return np.mean(self.distance_all[-self.items_considered:])

    def check_distance_exception(self) -> bool:

        if self.avg_distance() < self.distance_limit:
            return True
        else: return False

    def correct_large_distance(self, distance: float) -> float:
        last_distance = self.distance_all[-1]
        if distance >= last_distance * 1.7:
            return last_distance
        else:
            return distance
