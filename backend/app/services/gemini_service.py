import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure Gemini once at module level
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
_model = genai.GenerativeModel("gemini-3.5-flash")


def _build_prompt(context: dict) -> str:
    """
    Build a detailed prompt from alert context.
    context keys: pump_part, risk_level, equipment_name,
                  sensor_values, z_scores, trend
    """
    sensor_block = "\n".join([
        f"  - {k.replace('_', ' ').title()}: {v['value']} "
        f"(z-score: {v['z_score']}, trend: {v['trend']})"
        for k, v in context["sensors"].items()
    ])

    prompt = f"""
You are an expert maintenance engineer specializing in centrifugal pumps.

Equipment   : {context['equipment_name']}
Affected Part: {context['pump_part'].upper()}
Risk Level  : {context['risk_level'].upper()}

Current Sensor Readings:
{sensor_block}

Based on the sensor data above, provide a concise maintenance recommendation.
Structure your response in exactly three sections:

1. ROOT CAUSE: Most likely cause of this anomaly (1-2 sentences)
2. IMMEDIATE ACTION: What the operator should do right now (2-3 sentences)
3. PREVENTIVE MEASURE: Long-term action to prevent recurrence (1-2 sentences)

Keep the total response under 200 words. Be specific to centrifugal pump mechanics.
""".strip()

    return prompt


def get_recommendation(context: dict) -> str:
    """
    Call Gemini API and return the recommendation text.
    Raises an exception if the API call fails.
    """
    prompt   = _build_prompt(context)
    response = _model.generate_content(prompt)
    return response.text.strip()