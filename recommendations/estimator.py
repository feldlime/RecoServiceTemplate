from typing import (
    List,
    Optional,
    Protocol,
    runtime_checkable,
)

import numpy as np
import pandas as pd


@runtime_checkable
class Estimator(Protocol):
    """Recommendation estimator trait."""

    name: str

    def fit(self, df: pd.DataFrame) -> "Estimator":
        ...  # fmt: skip

    def recommend(
        self, users_ids: Optional[List[int]] = None, k: int = 10
    ) -> np.ndarray:
        ...  # fmt: skip
