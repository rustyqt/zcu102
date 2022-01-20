class demo():
    def __init__(self, value : int = 0):
        self.value = value

    def echo(self, message : str) -> str:
        return message

    def set_val(self, value : int) -> int:
        self.value = value
        return 0

    def get_val(self) -> int:
        return self.value