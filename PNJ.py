import google.generativeai as genai
import os

def get_pnj_story(village):
    google_api_key = os.getenv("google_api_key")
    prompt = f"Tu est un PNJ de l'île de {village} dans One Piece, tu me raconte une petite annecdote en lien avec l'île en UTF 8. Ne genre pas le texte quand tu parle au joeuur, ca peut-être un homme comme une femme. 2 petite ligne devrais être suffisant"


    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text