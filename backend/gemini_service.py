import google.generativeai as genai, os
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_recommendation(weather):
    prompt = f"""
        Given the current weather conditions: {weather["conditions"]} with a temperature of {weather["temp"]}°F,
        suggest an appropriate outfit.
        Respond in format: 
        "👕 Top: xyz
        👖 Bottoms: xyz\n
        etc"
    """
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
    return response.text