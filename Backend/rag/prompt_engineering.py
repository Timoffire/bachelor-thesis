from typing import Dict, Any
import textwrap


def build_prompt(ticker: str, metric_data: Dict[str, str], context: str) -> str:
    """
    Erstellt einen hochdetaillierten und robusten Prompt für die Tiefenanalyse einer einzelnen Finanzkennzahl.

    Diese Funktion wurde für maximale Detailtiefe und Präzision optimiert:
    1.  **Fokus auf eine Kennzahl:** Die Funktion ist darauf ausgelegt, eine einzelne Kennzahl intensiv zu beleuchten,
        was eine tiefere Analyse ermöglicht als bei der Verarbeitung mehrerer Kennzahlen gleichzeitig.
    2.  **Strukturierte und ausführliche Anweisungen:** Die Anweisungen für das LLM sind in den Sektionen
        'definition', 'analysis' und 'interpretation' wesentlich detaillierter, um eine umfassende und gut
        strukturierte Ausgabe zu gewährleisten.
    3.  **Strikte Anti-Halluzinations-Regeln:** Die Anweisungen betonen wiederholt, dass jede Aussage direkt
        und ausschließlich auf den bereitgestellten Daten (Kontext und Kennzahl) basieren muss.
    4.  **Verbesserte Lesbarkeit und Wartbarkeit:** Durch die Verwendung von `textwrap.dedent` und eine klare
        Struktur bleibt der Prompt-Code übersichtlich und leicht anpassbar.
    5.  **Logisches Ausgabeformat:** Die Funktion fordert ein einzelnes JSON-Objekt an, was dem Input von einer
        einzelnen Kennzahl entspricht.

    Args:
        ticker (str): Das Aktiensymbol (z.B. "AAPL").
        metric_data (Dict[str, str]): Ein Dictionary, das genau eine zu analysierende Finanzmetrik und ihren Wert
                                     enthält (z.B. `{'PERatio': '31.36'}`).
        context (str): Der Textkontext, der aus Finanzdokumenten (z.B. Quartalsberichten) extrahiert wurde.

    Returns:
        str: Der vollständig formatierte, detailorientierte Prompt für das LLM.

    Raises:
        ValueError: Wenn `metric_data` nicht genau ein Element enthält.
    """
    # 1. Validierung und Datenvorbereitung
    if not isinstance(metric_data, dict) or len(metric_data) != 1:
        raise ValueError("Das 'metric_data'-Argument muss ein Dictionary mit genau einem Schlüssel-Wert-Paar sein.")

    # Extrahiere den Namen und den Wert der einzigen Metrik
    metric_name = list(metric_data.keys())[0]
    metric_value = list(metric_data.values())[0]

    # Stelle sicher, dass der Kontext-String nicht leer ist
    context_str = context.strip() if context and context.strip() else "Kein relevanter Kontext in den Finanzdokumenten gefunden."

    # 2. Detailliertes Prompt-Template
    prompt_template = textwrap.dedent(f"""
        **SYSTEM-ANWEISUNG**
        Rolle: Du bist ein hochpräziser Finanzanalyst-Bot. Deine einzige Aufgabe ist die objektive Analyse der unten stehenden Daten.
        Regeln:
        1.  **Kein externes Wissen:** Du darfst AUSSCHLIESSLICH die Informationen aus den Abschnitten "Kontext aus Finanzdokumenten" und "Aktuelle Kennzahl" verwenden.
        2.  **Keine Halluzination:** Erfinde, schlussfolgere oder interpretiere nichts, was nicht explizit in den bereitgestellten Daten belegt ist. Wenn die Daten keine Aussage zulassen, gib dies explizit an.
        3.  **Nur JSON:** Deine Ausgabe MUSS ausschließlich ein einziges, valides JSON-Objekt sein. Gib KEINEN anderen Text, keine Erklärungen, keine Markdown-Formatierung und keine Code-Blöcke aus. Beginne direkt mit {{ und ende mit }}.

        ---

        **AUFGABENSTELLUNG**
        Führe eine detaillierte Analyse der Aktie mit dem Ticker **{ticker}** für die Finanzkennzahl **{metric_name}** durch.
        Gib das Ergebnis ausschließlich als JSON-Objekt zurück.

        ---

        **EINGABEDATEN**

        **1. Kontext aus Finanzdokumenten (z.B. Geschäftsberichte):**
        <dokumente>
        {context_str}
        </dokumente>

        **2. Aktuelle Kennzahl (API-Daten):**
        <kennzahl>
        - {metric_name}: {metric_value}
        </kennzahl>

        ---

        **AUSGABEFORMAT UND DETAILLIERTE ANWEISUNGEN**

        Generiere ein valides JSON-Objekt. Halte dich exakt an diese Struktur und die folgenden detaillierten Anweisungen für jedes Feld:

        - `metric`: (String) Der exakte Name der Kennzahl: "{metric_name}".

        - `value`: (String oder Number) Der exakte Wert aus `<kennzahl>`: {metric_value if metric_value != "N/A" else '"N/A"'}.

        - `definition`: (String) **Ausführliche Definition:** Erkläre die Kennzahl umfassend, aber verständlich. Beschreibe, was sie misst, wie sie konzeptionell berechnet wird und warum sie für Investoren eine wichtige Messgröße ist.

        - `analysis`: (String) **Ausführliche Analyse:** Führe eine objektive Einordnung des Wertes durch, die den Wert aus `<kennzahl>` mit den Informationen aus `<dokumente>` verknüpft. Deine Analyse muss folgende Schritte beinhalten, sofern die Daten dies zulassen:
        1. Nenne den aktuellen Wert der Kennzahl.
        2. Ordne den Wert in einen branchenüblichen oder theoretischen Kontext ein (z.B. "Ein Wert über X gilt generell als hoch/niedrig").
        3. Stelle eine Verbindung zu konkreten Aussagen im Kontext her (z.B. "Der Wert von {metric_value} steht im Einklang mit der im Quartalsbericht genannten Strategie zur Marktexpansion.").
        4. Wenn der Kontext keine Verbindung oder Einordnung erlaubt, gib exakt an: "Die bereitgestellten Dokumente enthalten keine Informationen für eine weiterführende Einordnung oder Analyse des Wertes."

        - `interpretation`: (String) **Spezifische Interpretation und Implikation:** Leite eine spezifische 
        Interpretation für die Aktie ab. **Diese Interpretation MUSS sich auf eine direkte Aussage oder einen 
        eindeutigen Zusammenhang im `<dokumente>`-Abschnitt stützen.** Erkläre, was die Analyse für das Unternehmen 
        bedeutet (z.B. Anzeichen für solide Finanzlage, Hinweise auf Wachstumspotenzial, mögliche Risiken). **Wenn 
        der Kontext keine fundierte Interpretation zulässt, gib exakt den String "Keine spezifische Interpretation im 
        bereitgestellten Kontext gefunden." zurück.**

        **WICHTIG:** Antworte ausschließlich mit dem JSON-Objekt. Kein anderer Text ist erlaubt. Keine Erklärungen, keine Einleitungen, keine Code-Blöcke.

        **FINALE ANWEISUNG:** Deine Antwort muss mit {{ beginnen und mit }} enden. Keine andere Formatierung oder Text.
    """)

    return prompt_template