#!/usr/bin/env python3
"""chat_weather.py
Terminal tabanlı bir sohbet asistanı.

* Kullanıcı hava durumu sorduğunda OpenAI **function-calling** (v1 `tools` arayüzü)
  ile gerçek `get_weather` fonksiyonunu çağırır.
* openai-python >= 1.0.0 uyumludur — eski `openai.ChatCompletion.create` artık
  kullanılmıyor.

Kurulum
=======
```bash
python -m venv .venv && source .venv/bin/activate   # opsiyonel sanal ortam
pip install --upgrade openai requests python-dotenv  # openai>=1.0.0
```

Ortam değişkenleri veya `.env` dosyası:
```
OPENAI_API_KEY="sk-..."
WEATHER_API_KEY="..."
```

Çalıştırma
==========
```bash
python chat_weather.py       # veya chmod +x && ./chat_weather.py
```
Çıkmak için **exit** / **quit** / **Ctrl-D** / **Ctrl-C** yeterli.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------------------------
# Ortam değişkenleri
# ---------------------------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY tanımlı değil.")
if not WEATHER_API_KEY:
    raise RuntimeError("WEATHER_API_KEY tanımlı değil.")

# OpenAI istemcisi (>=1.0.0 arayüzü)
client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------------------------------------------------------------------
# Gerçek işlev: Hava durumu
# ---------------------------------------------------------------------------

def get_weather(location: str) -> str:
    """WeatherAPI.com üzerinden mevcut hava durumunu getirir."""
    url = "https://api.weatherapi.com/v1/current.json"
    params = {"key": WEATHER_API_KEY, "q": location, "aqi": "no"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        d = r.json()
        loc = d["location"]["name"]
        ctry = d["location"]["country"]
        temp = d["current"]["temp_c"]
        cond = d["current"]["condition"]["text"]
        return f"{loc}, {ctry}: {temp}°C, {cond}"
    except Exception as e:
        return f"Failed to fetch weather: {e}"

# ---------------------------------------------------------------------------
# Function schema (v1: tools)
# ---------------------------------------------------------------------------

tools: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Belirli bir konum için mevcut hava durumu özetini döndürür.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Şehir veya coğrafi konum (örn. 'Istanbul')."
                    }
                },
                "required": ["location"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

SYSTEM_PROMPT = (
    "You are a helpful assistant. If the user requests current weather, "
    "call get_weather via the provided tool and use the result in your reply."
)

# ---------------------------------------------------------------------------
# Yardımcı: Model ile etkileşim
# ---------------------------------------------------------------------------

def chat_with_tools(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Modeli çağırır ve yanıt mesajını döndürür."""
    return client.chat.completions.create(
        model="gpt-4.1",  # dilediğiniz modeli seçin
        messages=messages,
        tools=tools,
        tool_choice="auto",  # model gerekirse çağıracak
    )

# ---------------------------------------------------------------------------
# Ana döngü
# ---------------------------------------------------------------------------

def main() -> None:
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    print("Assistant hazır. Çıkmak için 'exit' yazın.\n")

    while True:
        try:
            user_inp = input("you: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nassistant: Görüşmek üzere!")
            break

        if user_inp.lower() in {"exit", "quit"}:
            print("assistant: Görüşmek üzere!")
            break

        # Kullanıcı isteğini ekle
        messages.append({"role": "user", "content": user_inp})

        # Modeli çağır
        response = chat_with_tools(messages)
        first_msg = response.choices[0].message

        # API v1: tool_calls alanı var mı?
        if first_msg.tool_calls:  # type: ignore[attr-defined]
            # Assistant mesajını geçmişe ekle (tool çağrısı içeren)
            messages.append(first_msg.to_dict())

            # Her çağrı için fonksiyonu çalıştır ve sonucu modele ilet
            for call in first_msg.tool_calls:  # type: ignore[attr-defined]
                name = call.function.name
                args = json.loads(call.function.arguments)

                if name == "get_weather":
                    result = get_weather(**args)
                else:
                    result = f"Unknown function: {name}"

                # Sonucu rolü 'tool' olan mesaj olarak ekle
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result,
                    }
                )

            # Sonuçları içeren mesajlarla modeli tekrar çağır, nihai cevap al
            follow_up = client.chat.completions.create(
                model="gpt-4.1",
                messages=messages,
            )
            final_reply = follow_up.choices[0].message.content
            messages.append({"role": "assistant", "content": final_reply})
            print(f"assistant: {final_reply}")
        else:
            # Fonksiyon gerekmedi, doğrudan yanıt
            reply = first_msg.content
            messages.append({"role": "assistant", "content": reply})
            print(f"assistant: {reply}")


if __name__ == "__main__":
    main()
