from dataclasses import dataclass


@dataclass(frozen=True)
class Domino:
    left: int
    right: int

    def __str__(self):
        return f"{self.left}-{self.right}"

    def can_connect(self, number: int) -> bool:
        return self.left == number or self.right == number

    def __eq__(self, other):
        if not isinstance(other, Domino):
            return NotImplemented

        return (
            {self.left, self.right}
            ==
            {other.left, other.right}
        )

    def __hash__(self):
        return hash(frozenset((self.left, self.right)))