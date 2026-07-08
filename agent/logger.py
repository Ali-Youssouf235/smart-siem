from pathlib import Path
from config import LOCAL_LOG_FILE


def save_local(message):

    Path(LOCAL_LOG_FILE).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        LOCAL_LOG_FILE,
        "a",
        encoding="utf8"
    ) as f:

        f.write(message + "\n")