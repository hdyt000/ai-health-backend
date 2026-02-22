from typing import List, Tuple
from .schemas import LabParameter, RiskResult
from .clinical_patterns import detect_patterns


def _is_num(v) -> bool:
    return isinstance(v, (int, float))


def _num(p: LabParameter):
    return p.value if _is_num(p.value) else None


def _is_high(p: LabParameter) -> bool:
    v = _num(p)
    return v is not None and p.reference_high is not None and v > p.reference_high


def _is_low(p: LabParameter) -> bool:
    v = _num(p)
    return v is not None and p.reference_low is not None and v < p.reference_low


def _abnormal_label(p: LabParameter) -> str:
    if _is_high(p):
        return f"{p.name} yüksek"
    if _is_low(p):
        return f"{p.name} düşük"
    # categorical positive
    if isinstance(p.value, str) and p.value.strip().lower() in ["pozitif", "+", "++", "+++"]:
        return f"{p.name} pozitif"
    return ""


def calculate_risk(parameters: List[LabParameter]) -> RiskResult:
    abnormal: List[str] = []
    score = 0

    # --- Scoring rules (simple but clinical-weighted) ---
    # You can expand this map over time.
    # Points are assigned when abnormal.
    weighted_rules = [
        (["CRP", "CRP (Türbidimetrik)", "CRP (Turbidimetrik)"], 3, "high"),
        (["Kreatinin", "Creatinine"], 3, "high"),
        (["GFR", "eGFR"], 4, "low"),
        (["WBC", "Lökosit", "Leukocyte"], 2, "high"),
        (["NE#", "Nötrofil#"], 2, "high"),
        (["LDH"], 2, "high"),
        (["Glukoz", "Glucose"], 1, "high"),
        (["Kalsiyum", "Calcium"], 1, "high"),
    ]

    # Fast lookup
    by_name = {p.name: p for p in parameters}

    # Abnormal list + general scoring for anything outside range
    for p in parameters:
        label = _abnormal_label(p)
        if label:
            abnormal.append(label)

            # default points for “generic abnormal”
            if _is_high(p) or _is_low(p):
                score += 1
            elif isinstance(p.value, str) and "pozitif" in p.value.lower():
                score += 1

    # Apply weighted rules (additional points)
    for keys, points, direction in weighted_rules:
        for k in keys:
            if k in by_name:
                p = by_name[k]
                if direction == "high" and _is_high(p):
                    score += points
                elif direction == "low" and _is_low(p):
                    score += points

    patterns = detect_patterns(parameters)

    # Pattern-based bonus (deterministic)
    for pat in patterns:
        if pat.severity == "high":
            score += 3
        elif pat.severity == "medium":
            score += 2
        else:
            score += 1

    # Risk level thresholds (tune later with real data)
    if score >= 10:
        risk_level = "high"
    elif score >= 4:
        risk_level = "medium"
    else:
        risk_level = "low"

    # De-dup abnormalities (keep order)
    seen = set()
    abnormal_unique = []
    for a in abnormal:
        if a not in seen:
            seen.add(a)
            abnormal_unique.append(a)

    return RiskResult(
        score=score,
        risk_level=risk_level,
        abnormal_parameters=abnormal_unique,
        patterns=patterns
    )
