from langchain_core.messages import HumanMessage, SystemMessage


def analyze_symptoms(chat_model, user_input):
    """
    AI-driven symptom analyzer that returns detected symptoms,
    possible conditions, severity level and dynamic risk score.
    """

    try:

        system_prompt = """
You are an AI Medical Symptom Analyzer.

Your task is to analyze patient symptoms and provide safe medical guidance
for educational purposes only.

Important Instructions:
- Do NOT return internal reasoning or analysis steps.
- Do NOT show step-by-step thinking.
- Only return the final structured result.
- Do NOT provide a definitive diagnosis.
- Do NOT recommend prescription medicines.

You must estimate a dynamic risk score between 0 and 100 based on symptom severity.

Return the output in the following structure:

Symptoms Detected:
<List symptoms extracted from the user input>

Possible Conditions:
<List possible medical conditions>

Severity Level:
Low / Moderate / High

Risk Score:
<number between 0 and 100>

Recommended Actions:
<safe health advice>

When To Seek Medical Help:
<explain when the patient should see a doctor>
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Patient symptoms: {user_input}")
        ]

        response = chat_model.invoke(messages)

        return response.content

    except Exception as e:
        return f"Symptom analysis failed: {str(e)}"