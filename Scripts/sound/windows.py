import winsound


def play(filename: str):
    winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_ASYNC)