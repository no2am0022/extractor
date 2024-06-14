import pathlib

import pandas as pd


def to_csv(target_file: pathlib.Path, data: list[dict]) -> None:
    df = pd.DataFrame.from_records(data)

    print(df.head(5))

    with open(target_file, "w") as f:
        df.to_csv(f, index=False)
