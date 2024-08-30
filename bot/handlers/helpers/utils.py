class LimitedStack:
    def __init__(self, length: int, div: int = 13):
        self.div = div
        self.halfDiv = div // 2

        self.stack = []
        self.curr = 0
        self.filled = False
        self.length = length - 1

    def append(self, item):
        if self.filled:
            self.stack[self.curr] = item
        else:
            self.stack.append(item)
            if len(self.stack) - 1 == self.length:
                self.filled = True

        self.curr += 1
        if self.curr > self.length:
            self.curr = 0

    def clear(self) -> None:
        self.stack.clear()
        self.filled = False
        self.curr = 0

    def delete(self, index: int):
        if index >= self.length:
            raise IndexError("Index out of range")

        self.stack.pop(index)
        if self.curr > 0:
            self.curr -= 1
        self.filled = len(self.stack) == self.length

    @property
    def preview(self):
        if self.length < self.div or (not self.filled and self.curr < 13):
            return str(self.stack)

        start = str(self.stack[: self.halfDiv])[:-1]
        end = str(self.stack[-self.halfDiv + 1 :])[1:]
        return f"{start}, ... , {end}"

    def __repr__(self):
        return str(self.stack)

    def __str__(self):
        return self.preview

    def __len__(self):
        return len(self.stack)

    def __getitem__(self, index):
        return self.stack[index]
