from dataclasses import dataclass


@dataclass(frozen=True)
class Domino:
    left: int
    right: int

    def __str__(self):
        return f"{self.left}-{self.right}"

    def can_connect(self, number):
        return self.left == number or self.right == number