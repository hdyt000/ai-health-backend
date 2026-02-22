import json
from openai import OpenAI
from .config import OPENAI_API_KEY, MODEL
from .schemas import LabParameter, RiskResult

client = OpenAI(api_key=OPENAI_API_KEY)


def _system_prompt(lang: str) -> str:
    if lang == "tr":
        return """
Sen bir laboratuvar sonuçlarını açıklayan asistansın.

KURALLAR:
- Asla teşhis koyma.
- Asla tedavi/prescription önerme.
- Kesin hüküm kullanma.
- Her zaman: "Bu bilgiler bilgilendirme amaçlıdır." de.
- Sana verilen risk skoru, risk seviyesi, anormal parametreler ve pattern’leri temel al.
- Yanıtı SADECE geçerli JSON olarak ver.

JSON:
{
  "summary": "string",
  "recommendation": "string"
}
"""
    return """
You are a lab-results explanation assistant.

RULES:
- Do NOT diagnose.
- Do NOT prescribe treatment/medication.
- Use cautious language.
- Always say this is informational only.
- Base your explanation on provided risk score/level, abnormal parameters, and patterns.
- Respond ONLY as valid JSON.

JSON:
{
  "summary": "string",
  "recommendation": "string"
}
"""


def generate_explanation(parameters, risk: RiskResult, language: str = "en") -> dict:
    payload = {
        "risk": risk.model_dump(),
        "abnormal_parameters": risk.abnormal_parameters,
        "patterns": [p.model_dump() for p in risk.patterns],
        "parameters": [p.model_dump() for p in parameters],
    }

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": _system_prompt(language)},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=2)},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
