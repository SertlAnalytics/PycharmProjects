class Test:
    def __init__(self):
        self._test_str = ''

    @property
    def set_test_str(self):
        return self._test_str

    def set_test_str_with_new_value(self, value: str):
        self._test_str = value

