from typing import List, Dict, Any
import json
import textwrap


def build_prompt(ticker: str, metrics: List[str], context: str, metric_values: Dict[str, Any]) -> str:
    """
    Erstellt einen hochstrukturierten und robusten Prompt für eine detaillierte Finanzanalyse.

    Diese Funktion wurde optimiert für:
    1.  **Code-Lesbarkeit**: Durch `textwrap.dedent` wird der Prompt-Text im Code sauber ausgerichtet.
    2.  **Präzisere Anweisungen**: Die Anweisungen an das LLM sind noch direkter und unmissverständlicher formuliert.
    3.  **Wartbarkeit**: Das Template ist klar strukturiert und lässt sich leicht anpassen.
    4.  **Robustheit**: Zusätzliche Guardrails, wie die Anweisung, nur JSON auszugeben, minimieren Fehler.

    Args:
        ticker (str): Das Aktiensymbol (z.B. "AAPL").
        metrics (List[str]): Eine Liste der zu analysierenden Finanzmetriken (z.B. ["P/E Ratio"]).
        context (str): Der Textkontext, der aus der Vektordatenbank abgerufen wurde.
        metric_values (Dict[str, Any]): Ein Dictionary mit den über eine API abgerufenen Kennzahlen.

    Returns:
        str: Der vollständig formatierte, optimierte Prompt für das LLM.
    """
    # 1. Datenvorbereitung: Logik für die dynamischen Teile des Prompts bündeln
    metrics_str = ", ".join(metrics) or "Keine spezifischen Metriken angefordert."

    # Sicherstellen, dass der Kontext-String nicht leer ist
    context_str = context.strip() if context and context.strip() else "Kein relevanter Kontext in den Finanzdokumenten gefunden."

    # Kennzahlen für eine saubere Darstellung formatieren.
    # Es wird für jede angeforderte Metrik ein Eintrag erzeugt, auch wenn kein Wert vorliegt.
    metric_values_str = "\n".join(
        [f"- {metric}: {metric_values.get(metric, 'N/A')}" for metric in metrics]
    ) if metric_values and metrics else "Keine aktuellen Kennzahlen verfügbar."

    # 2. Prompt-Template: textwrap.dedent entfernt führende Leerzeichen aus mehrzeiligen
    #    Strings, was die Lesbarkeit im Code erheblich verbessert.
    #    Die Anweisungen wurden für maximale Klarheit und zur Vermeidung von Halluzinationen geschärft.
    prompt_template = textwrap.dedent(f"""
        **SYSTEM-ANWEISUNG**
        Rolle: Du bist ein präziser Finanzanalyse-Bot. Deine Aufgabe ist es, die unten stehenden Eingabedaten objektiv zu analysieren.
        Regeln:
        1.  Halte dich strikt an die bereitgestellten Daten. Verwende kein externes Wissen.
        2.  Erfinde oder schlussfolgere keine Informationen, die nicht explizit in den Daten enthalten sind.
        3.  Deine Ausgabe MUSS ein einziges, valides JSON-Array sein, ohne einleitenden oder nachfolgenden Text.

        ---

        **AUFGABENSTELLUNG**
        Analysiere die Aktie mit dem Ticker **{ticker}** für die folgenden Finanzkennzahlen: **{metrics_str}**.
        Gib das Ergebnis als JSON-Array zurück, wobei jedes Objekt eine Kennzahl analysiert.

        ---

        **EINGABEDATEN**

        **1. Kontext aus Finanzdokumenten:**
        <dokumente>
        {context_str}
        </dokumente>

        **2. Aktuelle Kennzahlen (API-Daten):**
        <kennzahlen>
        {metric_values_str}
        </kennzahlen>

        ---

        **AUSGABEFORMAT UND ANWEISUNGEN**
        Generiere ein valides JSON-Array von Objekten. Halte dich exakt an diese Struktur und Feldanweisungen:

        - `metric`: (String) Der Name der Kennzahl.
        - `value`: (String, Number oder "N/A") Der exakte Wert aus `<kennzahlen>`.
        - `definition`: (String) Eine kurze, allgemeine Definition der Kennzahl (1-2 Sätze).
        - `analysis`: (String) Eine objektive Analyse, die den Wert aus `<kennzahlen>` mit Informationen aus `<dokumente>` vergleicht oder in Beziehung setzt.
        - `interpretation`: (String) Eine spezifische Interpretation für die Aktie. Diese MUSS sich direkt auf eine Aussage in `<dokumente>` stützen. **Wenn der Kontext keine Interpretation zulässt, gib exakt den String "Keine spezifische Interpretation im bereitgestellten Kontext gefunden." zurück.**

        **BEISPIEL FÜR DAS GEWÜNSCHTE JSON-FORMAT:**
        ```json
        [
          {{
            "metric": "P/E Ratio",
            "value": 15.7,
            "definition": "Das Kurs-Gewinn-Verhältnis (KGV) setzt den Aktienkurs eines Unternehmens ins Verhältnis zu seinem Gewinn pro Aktie.",
            "analysis": "Das aktuelle KGV von 15.7 liegt unter dem Branchendurchschnitt von 20, wie im Quartalsbericht Q4 erwähnt.",
            "interpretation": "Laut dem Management-Kommentar im Dokument deutet das niedrigere KGV auf eine mögliche Unterbewertung oder geringere Wachstumserwartungen im Vergleich zu Wettbewerbern hin."
          }},
          {{
            "metric": "Dividend Yield",
            "value": "N/A",
            "definition": "Die Dividendenrendite gibt das Verhältnis der Dividende zum Aktienkurs an.",
            "analysis": "Für die Dividendenrendite wurde kein Wert bereitgestellt.",
            "interpretation": "Keine spezifische Interpretation im bereitgestellten Kontext gefunden."
          }}
        ]
        ```

        **FINALE ANWEISUNG:** Beginne deine Antwort direkt mit `[` und beende sie mit `]`.
    """)

    return prompt_template
