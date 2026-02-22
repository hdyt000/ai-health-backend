from typing import List
from .schemas import LabParameter


def calculate_risk(parameters: List[LabParameter]):

    abnormal = []

    for p in parameters:

        # Numeric case
        if isinstance(p.value, float):
            if p.reference_low and p.value < p.reference_low:
                abnormal.append(f"{p.name} düşük")
            elif p.reference_high and p.value > p.reference_high:
                abnormal.append(f"{p.name} yüksek")

        # Categorical case
        elif isinstance(p.value, str):
            if p.value in ["Pozitif", "+", "++", "+++"]:
                abnormal.append(f"{p.name} pozitif")

    count = len(abnormal)

    if count == 0:
        risk = "low"
    elif count == 1:
        risk = "medium"
    else:
        risk = "high"

    return risk, abnormal