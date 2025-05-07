#!/usr/bin/env python3
"""
Interactive CLI for Gemini LLM.
Hava durumu yalnızca açıkça sorulduğunda eklenecek şekilde güncellenmiştir.
"""

import os, sys, argparse, requests, json, re
from typing import List

# ---------------------------------------------------------------------------
# Ortam değişkenleri
# ---------------------------------------------------------------------------
token       = os.environ.get("GEMINI_API_KEY", "")
weather_key = os.environ.get("WEATHER_API_KEY", "")

if not token:
    sys.exit("Error: GEMINI_API_KEY env var not set.")
if not weather_key:
    print("Warning: WEATHER_API_KEY not set – weather queries will fail.\n")

# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTION = (
    "You are a helpful assistant. "
    "If—and only if—the user explicitly asks about current or future weather, "
    "respond with exactly CALL_WEATHER(location) and nothing else. "
    "Otherwise, answer normally."
)

# Kullanıcı sorusunun hava durumuyla ilgili olup olmadığını kaba bir anahtar‑kelime listesiyle test et
_WEATHER_WORDS: List[str] = [
    "weather", "hava", "sıcaklık", "temperature", "forecast",
    "hava durumu", "yağmur", "rain", "kar", "snow", "wind", "rüzgâr",
    "humidity", "nem", "hava nasıl"
]

def is_weather_query(text: str) -> bool:
    t = text.lower()
    return any(word in t for word in _WEATHER_WORDS)

def get_weather(location: str) -> str:
    url = "https://api.weatherapi.com/v1/current.json"
    params = {"key": weather_key, "q": location, "aqi": "no"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        d = r.json()
        loc  = d["location"]["name"]
        ctry = d["location"]["country"]
        temp = d["current"]["temp_c"]
        cond = d["current"]["condition"]["text"]
        return f"{loc}, {ctry}: {temp}°C, {cond}"
    except Exception as e:
        return f"Failed to fetch weather: {e}"

def generate_content(prompt: str, model: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={token}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        resp = requests.post(url, headers={"Content-Type": "application/json"},
                             json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except requests.exceptions.RequestException as e:
        sys.exit(f"Gemini request failed: {e}")
    except (KeyError, IndexError):
        sys.exit("Unexpected Gemini response:\n" + json.dumps(resp.json(), indent=2))

# ---------------------------------------------------------------------------
# CLI döngüsü
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gemini CLI with weather function‑call simulation."
    )
    parser.add_argument("--model", default="gemini-2.0-flash", help="Gemini model ID")
    args = parser.parse_args()

    print("Gemini CLI – type 'exit' to quit.")
    while True:
        try:
            user_input = input("Prompt> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye."); break
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye."); break
        if not user_input:
            continue

        # 1) İlk istek – fonksiyon çağrısı lazım mı?
        first_prompt = f"{SYSTEM_INSTRUCTION}\nUser: {user_input}"
        first_reply  = generate_content(first_prompt, model=args.model)

        call_match = re.fullmatch(r"CALL_WEATHER\((.+?)\)", first_reply.strip(),
                                  flags=re.DOTALL)

        # --------------------------------------------------------------
        # Senaryo A – KULLANICI GERÇEKTEN HAVA SORUYOR
        # --------------------------------------------------------------
        if call_match and is_weather_query(user_input):
            location = call_match.group(1).strip()
            weather_info = get_weather(location)

            second_prompt = (
                "You are a helpful assistant. "
                "The user asked a question and the current weather data is provided. "
                "Use the weather data ONLY IF it is relevant to the user's query. "
                "Otherwise ignore it.\n\n"
                f"USER_QUERY: {user_input}\n"
                f"WEATHER_DATA: {weather_info}"
            )
            final_reply = generate_content(second_prompt, model=args.model)
            print(f"\nAssistant> {final_reply}\n")
            continue

        # --------------------------------------------------------------
        # Senaryo B – Gemini yanlışlıkla CALL_WEATHER dedi
        # --------------------------------------------------------------
        if call_match and not is_weather_query(user_input):
            # CALL_WEATHER çıktısını yok say, normal yanıt iste
            fallback_prompt = (
                "The assistant mistakenly entered a weather function call. "
                "Please answer the user's question normally, without mentioning weather.\n\n"
                f"USER_QUERY: {user_input}"
            )
            final_reply = generate_content(fallback_prompt, model=args.model)
            print(f"\nAssistant> {final_reply}\n")
            continue

        # --------------------------------------------------------------
        # Senaryo C – Fonksiyon çağrısı yok, normal cevap
        # --------------------------------------------------------------
        print(f"\nAssistant> {first_reply}\n")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
