from enum import StrEnum


class CommentReaction(StrEnum):
    CONFUSED = "CONFUSED"
    EYES = "EYES"
    HEART = "HEART"
    HOORAY = "HOORAY"
    LAUGH = "LAUGH"
    ROCKET = "ROCKET"
    THUMBS_DOWN = "THUMBS_DOWN"
    THUMBS_UP = "THUMBS_UP"

    def __str__(self) -> str:
        return str(self.value)
