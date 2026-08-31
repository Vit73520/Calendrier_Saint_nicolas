import requests
from bs4 import BeautifulSoup
from google import genai
import os
import json
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import re

# Configuration
URL_ANNOUNCES = "https://www.saintnicolasduchardonnet.org/category/annonces/"
TZ = pytz.timezone('Europe/Paris')

def setup_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    return genai.Client(api_key=api_key)

def get_latest_articles():
    """Fetches the latest announcements articles links."""
    response = requests.get(URL_ANNOUNCES)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = {}
    for article in soup.find_all('article'):
        title_tag = article.find('h2', class_='entry-title')
        if not title_tag:
            continue
        title = title_tag.get_text().strip().lower()
        link = title_tag.find('a')['href']
        
        if "permanence" in title and "permanence" not in articles:
            articles["permanence"] = link
        elif "complémentaires" in title and "complementaires" not in articles:
            articles["complementaires"] = link
        elif "semaine" in title and "semaine" not in articles:
            articles["semaine"] = link
            
    return articles

def fetch_article_text(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    content_div = soup.find('div', class_='entry-content')
    if content_div:
        return content_div.get_text(separator='\n')
    return ""

def extract_events_with_gemini(client, text, category_type):
    """
    category_type can be 'semaine', 'complementaires', 'permanence'.
    Returns a list of dicts: [{"title": "...", "start_time": "YYYY-MM-DDTHH:MM", "end_time": "YYYY-MM-DDTHH:MM", "description": "..."}, ...]
    """
    
    prompt = f"""
    Tu es un assistant spécialisé dans l'extraction de données structurées.
    Voici le texte d'une annonce de la paroisse Saint-Nicolas-du-Chardonnet.
    Le type d'annonce est '{category_type}'.
    
    Analyse le texte et extrais tous les événements avec leur date et leur heure.
    - Pour les "Messes/offices" (semaine), essaie de déduire la date exacte à partir du jour et du mois donnés.
    - Pour les "Permanences", la durée est souvent explicite (ex: de 11h30 à 12h45).
    - Pour les "Conférences/Cours" (complémentaires), si l'heure de fin n'est pas précisée, fixe une durée de 1 heure.
    - Format de date de sortie : YYYY-MM-DDTHH:MM:SS
    
    Retourne UNIQUEMENT un tableau JSON structuré comme suit, sans aucun formatage Markdown ni texte avant ou après :
    [
      {{
        "title": "Nom de l'événement (ex: Messe chantée, Permanence Abbé X)",
        "start_time": "2026-08-30T09:00:00",
        "end_time": "2026-08-30T10:00:00",
        "description": "Détails optionnels"
      }}
    ]
    
    Texte de l'annonce :
    {text}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    raw_text = response.text.strip()
    
    # Clean up possible markdown code blocks around json
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    raw_text = raw_text.strip()
    
    try:
        events = json.loads(raw_text)
        return events
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from Gemini: {e}")
        print("Raw text:")
        print(raw_text)
        return []

def create_ics(events, filename, cal_name):
    cal = Calendar()
    cal.add('prodid', f'-//Saint-Nicolas-du-Chardonnet//{cal_name}//FR')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', cal_name)
    cal.add('x-wr-timezone', 'Europe/Paris')
    
    for ev in events:
        try:
            event = Event()
            event.add('summary', ev.get('title', 'Événement'))
            
            start_dt = datetime.fromisoformat(ev['start_time'])
            start_dt = TZ.localize(start_dt)
            event.add('dtstart', start_dt)
            
            if 'end_time' in ev and ev['end_time']:
                end_dt = datetime.fromisoformat(ev['end_time'])
                end_dt = TZ.localize(end_dt)
                event.add('dtend', end_dt)
            else:
                # Default 1 hour duration
                event.add('dtend', start_dt + timedelta(hours=1))
                
            if 'description' in ev and ev['description']:
                event.add('description', ev['description'])
                
            event.add('dtstamp', datetime.now(TZ))
            cal.add_component(event)
        except Exception as e:
            print(f"Could not parse event {ev}: {e}")
            
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())
    print(f"Generated {filename} with {len(events)} events.")

def main():
    client = setup_gemini()
    print("Fetching latest articles...")
    articles = get_latest_articles()
    
    mapping = {
        "semaine": {"filename": "messes.ics", "cal_name": "SNC - Messes et Offices"},
        "complementaires": {"filename": "conferences.ics", "cal_name": "SNC - Conférences et Cours"},
        "permanence": {"filename": "permanence.ics", "cal_name": "SNC - Permanence des Prêtres"}
    }
    
    for cat_key, url in articles.items():
        if cat_key in mapping:
            print(f"Processing category: {cat_key} from {url}")
            text = fetch_article_text(url)
            if not text:
                print(f"No text found for {url}")
                continue
                
            events = extract_events_with_gemini(client, text, cat_key)
            
            if events:
                create_ics(events, mapping[cat_key]["filename"], mapping[cat_key]["cal_name"])
            else:
                print(f"No events extracted for {cat_key}")

if __name__ == "__main__":
    main()
