from typing import List, Dict, Tuple, Optional
from .schemas import LabParameter, PatternMatch


def _num(p: LabParameter) -> Optional[float]:
    return p.value if isinstance(p.value, (int, float)) else None


def _is_high(p: LabParameter) -> bool:
    v = _num(p)
    return v is not None and p.reference_high is not None and v > p.reference_high


def _is_low(p: LabParameter) -> bool:
    v = _num(p)
    return v is not None and p.reference_low is not None and v < p.reference_low


def _find(param_map: Dict[str, LabParameter], keys: List[str]) -> Optional[LabParameter]:
    for k in keys:
        if k in param_map:
            return param_map[k]
    return None


def detect_patterns(parameters: List[LabParameter]) -> List[PatternMatch]:
    # normalize keys for lookup
    param_map = {p.name.strip(): p for p in parameters}

    patterns: List[PatternMatch] = []

    # --- Infection / inflammation pattern ---
    wbc = _find(param_map, ["WBC", "Lökosit", "Leukocyte"])
    ne_abs = _find(param_map, ["NE#", "NE#", "Nötrofil#", "Neut#", "NE#"])
    crp = _find(param_map, ["CRP", "CRP (Türbidimetrik)", "CRP (Turbidimetrik)"])

    evidence = []
    score_hits = 0
    if wbc and _is_high(wbc):
        evidence.append(f"WBC yüksek ({_num(wbc)})")
        score_hits += 1
    if ne_abs and _is_high(ne_abs):
        evidence.append(f"NE# yüksek ({_num(ne_abs)})")
        score_hits += 1
    if crp and _is_high(crp):
        evidence.append(f"CRP yüksek ({_num(crp)})")
        score_hits += 1

    if score_hits >= 2:
        patterns.append(PatternMatch(
            code="INFLAMMATION_PATTERN",
            title="İnflamasyon / enfeksiyon paterni olasılığı",
            severity="high" if score_hits == 3 else "medium",
            evidence=evidence
        ))

    # --- Kidney function pattern ---
    creat = _find(param_map, ["Kreatinin", "Creatinine"])
    urea = _find(param_map, ["Üre", "Ure", "Urea"])
    gfr = _find(param_map, ["GFR", "eGFR"])

    evidence = []
    hits = 0
    if creat and _is_high(creat):
        evidence.append(f"Kreatinin yüksek ({_num(creat)})")
        hits += 1
    if urea and _is_high(urea):
        evidence.append(f"Üre yüksek ({_num(urea)})")
        hits += 1
    if gfr and _is_low(gfr):
        evidence.append(f"GFR düşük ({_num(gfr)})")
        hits += 1

    if hits >= 2:
        patterns.append(PatternMatch(
            code="KIDNEY_FUNCTION_PATTERN",
            title="Böbrek fonksiyonlarında azalma paterni olasılığı",
            severity="high" if (gfr and _is_low(gfr) and (creat and _is_high(creat))) else "medium",
            evidence=evidence
        ))

    # --- Glucose / metabolic pattern ---
    glu = _find(param_map, ["Glukoz", "Glucose"])
    if glu and _is_high(glu):
        patterns.append(PatternMatch(
            code="GLUCOSE_ELEVATION",
            title="Kan şekeri yüksekliği",
            severity="medium",
            evidence=[f"Glukoz yüksek ({_num(glu)})"]
        ))

    # --- Tissue stress pattern (LDH) ---
    ldh = _find(param_map, ["LDH"])
    if ldh and _is_high(ldh):
        patterns.append(PatternMatch(
            code="LDH_ELEVATION",
            title="LDH yüksekliği (doku stresi / hücresel yıkım ile ilişkili olabilir)",
            severity="medium",
            evidence=[f"LDH yüksek ({_num(ldh)})"]
        ))

    return patterns
