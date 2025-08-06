class WrapResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data
