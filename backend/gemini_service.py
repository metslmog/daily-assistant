import google.generativeai as genai, os
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_recommendation(weather):
    # Defensive: check for required keys
    if not weather or "conditions" not in weather or "temp" not in weather:
        return "Unable to generate outfit suggestion: weather data unavailable."
    prompt = f"""
        Given the current weather conditions: {weather["conditions"]} with a temperature of {weather["temp"]}°F,
        suggest an appropriate outfit.
        Respond in format: 
        "👕 Top: xyz
        👖 Bottoms: xyz\n
        etc"
    """
    response = genai.GenerativeModel("gemini-2.5-flash").generate_content(prompt)
    return response.text