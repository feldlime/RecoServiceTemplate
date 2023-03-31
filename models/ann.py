class Ann():
    """Class for fit-perdict Ann model"""

    def __init__(self, label: list, distance: list):
        self.label = label
        self.distance = distance

    def predict(self, user_id: int):
        return self.label[user_id]
