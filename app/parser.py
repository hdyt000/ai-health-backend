import re
from typing import List
from .schemas import LabParameter


def parse_lab_text(text: str) -> List[LabParameter]:
    lines = (text or "").split("\n")
    parameters: List[LabParameter] = []

    # e-Nabız / tablo satırı: NAME VALUE UNIT LOW - HIGH
    numeric_pattern = r"""
    ^
    ([A-Za-zÇĞİÖŞÜçğıöşü#%()\-,.\s]+?)      # name
    \s+
    ([\d.]+)                               # value
    \s+
    ([A-Za-z0-9^/%µ]+)                     # unit
    \s+
    ([\d.]+)                               # ref low
    \s*-\s*
    ([\d.]+)                               # ref high
    $
    """

    # categorical lines like: Protein Negatif
    categorical_pattern = r"""
    ^
    ([A-Za-zÇĞİÖŞÜçğıöşü\s\.\(\)\-]+?)      # name
    \s+
    (Negatif|Pozitif)
    $
    """

    trash_contains = [
        "T.C.", "Sağlık", "Sayfa", "enabiz", "0 850",
        "Tarih", "Sonuç", "Birimi", "Referans", "Rapor"
    ]

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if any(x.lower() in line.lower() for x in trash_contains):
            continue

        m = re.match(numeric_pattern, line, re.VERBOSE)
        if m:
            name = m.group(1).strip()
            value = float(m.group(2))
            unit = m.group(3).strip()
            ref_low = float(m.group(4))
            ref_high = float(m.group(5))

            # ignore too-short junk tokens
            if len(name) < 2:
                continue

            parameters.append(
                LabParameter(
                    name=name,
                    value=value,
                    unit=unit,
                    reference_low=ref_low,
                    reference_high=ref_high,
                )
            )
            continue

        cm = re.match(categorical_pattern, line, re.VERBOSE)
        if cm:
            name = cm.group(1).strip()
            val = cm.group(2).strip()
            if len(name) < 2:
                continue
            parameters.append(LabParameter(name=name, value=val))
            continue

    return parameters
