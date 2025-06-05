class LimitedStack:
    def __init__(self, length: int, div: int = 13):
        """Initialize a LimitedStack with fixed capacity.
        
        Args:
            length (int): The maximum capacity of the stack
            div (int, optional): Number of elements to show in preview. Defaults to 13.
        """
        self.div = div
        self.halfDiv = div // 2
        self.stack = []
        self.curr = 0
        self.filled = False
        self.capacity = length  # Store actual capacity without -1

    def append(self, item: any) -> None:
        """Append an item to the stack. If stack is full, overwrites oldest item.

        Args:
            item: The item to append
        """
        if self.filled:
            self.stack[self.curr] = item
        else:
            self.stack.append(item)
            if len(self.stack) == self.capacity:
                self.filled = True

        self.curr += 1
        if self.curr >= self.capacity:
            self.curr = 0

    def clear(self) -> None:
        """Clear all items from the stack."""
        self.stack.clear()
        self.filled = False
        self.curr = 0

    def delete(self, index: int) -> None:
        """Delete an item at the specified index.

        Args:
            index (int): Index of item to delete

        Raises:
            IndexError: If index is out of range
        """
        if index >= len(self.stack):
            raise IndexError("Index out of range")

        self.stack.pop(index)
        if self.curr > 0:
            self.curr -= 1
        self.filled = len(self.stack) == self.capacity

    @property
    def preview(self) -> str:
        """Get a preview of the stack contents.

        Returns:
            str: String representation with middle items truncated if stack is large
        """
        if not self.stack:
            return "[]"
            
        if len(self.stack) <= self.div or (not self.filled and self.curr < self.div):
            return str(self.stack)

        if self.halfDiv >= len(self.stack):
            return str(self.stack)

        start = str(self.stack[: self.halfDiv])[:-1]
        end = str(self.stack[-self.halfDiv + 1 :])[1:]
        return f"{start}, ... , {end}"

    def __repr__(self) -> str:
        return str(self.stack)

    def __str__(self) -> str:
        return self.preview

    def __len__(self) -> int:
        return len(self.stack)

    def __getitem__(self, index: int) -> any:
        """Get item at specified index.

        Args:
            index (int): Index of item to retrieve

        Raises:
            IndexError: If index is out of range

        Returns:
            any: Item at specified index
        """
        if index >= len(self.stack):
            raise IndexError("Index out of range")
        return self.stack[index]
