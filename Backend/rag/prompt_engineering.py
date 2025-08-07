def build_metric_analysis_prompt(metric_data, metric_context, metric_name):
    """
    Erstellt einen detaillierten Prompt für die Einzelanalyse einer Finanzmetrik.

    Args:
        metric_data (dict): Dictionary mit allen Metriken und deren Werten
        metric_context (dict): Dictionary mit historischen Daten, Peer-Metriken,
                              Makro-Info und Unternehmensinfo
        metric_name (str): Name der zu analysierenden Metrik (z.B. 'revenue', 'pe_ratio')

    Returns:
        str: Vollständig formatierter Prompt für die LLM-Analyse
    """

    # Extrahiere die spezifische Metrik aus den Daten
    if metric_name not in metric_data:
        raise ValueError(f"Metrik '{metric_name}' nicht in metric_data gefunden")

    specific_metric = metric_data[metric_name]

    # Formatiere die Metrikdaten
    metric_info = f"""
Metrikname: {metric_name}
Aktueller Wert: {specific_metric.get('value', specific_metric.get(metric_name, 'N/A'))}
Kontext: {specific_metric.get('context', 'N/A')}
Quellen: {', '.join(specific_metric.get('sources', []))}
"""

    # Formatiere historische Daten
    historical_section = "## Historische Daten\n"
    if 'historical_metrics' in metric_context:
        historical_section += "Jahresvergleich:\n"
        for year, data in metric_context['historical_metrics'].items():
            if metric_name in data and data[metric_name] is not None and str(data[metric_name]) != 'nan':
                historical_section += f"- {year}: {data[metric_name]:,.0f}\n"

    # Formatiere Peer-Informationen
    peer_section = "## Branchenkontext (Peer-Daten)\n"
    if 'peer_metrics' in metric_context:
        peer_data = metric_context['peer_metrics']
        peer_section += f"""
Sektor: {peer_data.get('Sector', 'N/A')}
Branchen-ETF: {peer_data.get('ETF Name', 'N/A')} ({peer_data.get('ETF Symbol', 'N/A')})
ETF YTD Return: {peer_data.get('YTD Return', 'N/A')}%
ETF 1-Jahres-Return: {peer_data.get('1Y Return', 'N/A')}%
ETF Dividendenrendite: {peer_data.get('Dividend Yield', 'N/A')}%
ETF Beta: {peer_data.get('Beta', 'N/A')}
"""

    # Formatiere Makro-Informationen
    macro_section = "## Makroökonomisches Umfeld\n"
    if 'macro_info' in metric_context:
        macro_data = metric_context['macro_info']
        macro_section += f"""
Land: {macro_data.get('country', 'N/A')}
BIP-Wachstum: {macro_data.get('gdp_growth', 'N/A')}%
Inflationsrate: {macro_data.get('inflation_rate', 'N/A')}%
Importe (% des BIP): {macro_data.get('imports', 'N/A')}%
Exporte (% des BIP): {macro_data.get('exports', 'N/A')}%
"""

    # Formatiere Unternehmensinformationen
    company_section = "## Unternehmensinformationen\n"
    if 'company_info' in metric_context and 'company_info' in metric_context['company_info']:
        company_data = metric_context['company_info']['company_info']
        company_section += f"""
Unternehmen: {company_data.get('name', 'N/A')}
Sektor: {company_data.get('sector', 'N/A')}
Branche: {company_data.get('industry', 'N/A')}
Mitarbeiter: {company_data.get('employees', 'N/A'):,}
Marktkapitalisierung: ${company_data.get('market_cap', 'N/A'):,.0f}
Hauptsitz: {company_data.get('headquarters', 'N/A')}
Website: {company_data.get('website', 'N/A')}
Beschreibung: {company_data.get('description', 'N/A')[:500]}...
"""

    # Vollständiger Prompt
    full_prompt = f"""# Prompt für umfassende Einzelmetrik-Analyse

## Anweisung
Du bist ein erfahrener Finanzanalyst. Analysiere die angegebene Metrik vollständig und detailliert unter Verwendung des bereitgestellten Kontexts. Konzentriere dich ausschließlich auf diese eine Metrik.

## Zu analysierende Metrik
{metric_info}

## Kontextinformationen
{historical_section}
{peer_section}
{macro_section}
{company_section}

## Analyseanforderungen

### 1. Metrik-Definition und Bedeutung
- Erkläre präzise, was diese Metrik misst und wie sie berechnet wird
- Definiere die Kennzahl im finanzwirtschaftlichen Kontext
- Erläutere die Relevanz für Investoren und Stakeholder

### 2. Aktueller Wert-Interpretation
- Analysiere den vorliegenden Wert der Metrik
- Erkläre, was dieser spezifische Wert über das Unternehmen aussagt
- Bewerte, ob der Wert als positiv, neutral oder negativ einzustufen ist

### 3. Historische Einordnung
- Vergleiche den aktuellen Wert mit historischen Daten aus dem Kontext
- Identifiziere Trends, Verbesserungen oder Verschlechterungen
- Erkläre mögliche Ursachen für Veränderungen

### 4. Branchenvergleich (Peer-Analyse)
- Setze den Wert in Relation zu Branchendurchschnitt und Wettbewerbern
- Bewerte die Wettbewerbsposition des Unternehmens bei dieser Metrik
- Erkläre Über- oder Unterperformance gegenüber Peers

### 5. Makroökonomische Einflüsse
- Analysiere, wie makroökonomische Faktoren diese Metrik beeinflussen können
- Berücksichtige Zinsumfeld, Konjunkturlage, Branchenzyklen
- Erkläre externe Einflussfaktoren auf die Kennzahl

### 6. Unternehmenskontext
- Integriere unternehmensspezifische Informationen in die Analyse
- Berücksichtige Geschäftsmodell, Strategie und besondere Umstände
- Erkläre, wie diese Metrik zur Gesamtbeurteilung des Unternehmens beiträgt

### 7. Implikationen und Ausblick
- Erläutere, was dieser Metrikwert für die Zukunft des Unternehmens bedeutet
- Identifiziere potenzielle Risiken und Chancen
- Gib Hinweise auf wichtige Entwicklungen, die zu beobachten sind

### 8. Finanzliteratur-Fundierung
- Untermauere deine Analyse mit etablierten finanzwirtschaftlichen Prinzipien
- Referenziere relevante Bewertungstheorien und -methoden
- Erkläre theoretische Grundlagen, wo angebracht

## Ausgabeformat
Strukturiere deine Antwort klar und logisch. Verwende Absätze und Zwischenüberschriften für bessere Lesbarkeit. Begründe alle Aussagen und Bewertungen nachvollziehbar.

## Fokus
Konzentriere dich ausschließlich auf die Metrik '{metric_name}'. Erwähne andere Kennzahlen nur, wenn sie direkt zur Interpretation der analysierten Metrik beitragen.
"""

    return full_prompt


# Beispiel-Nutzung mit den bereitgestellten Daten
def example_usage():
    """Beispiel für die Nutzung der Prompt-Builder-Funktion"""

    # Beispieldaten aus dem bereitgestellten JSON
    metric_data = {
        "revenue": {
            "revenue": 408624988160,
            "context": "test",
            "sources": ["68bcb9f8_chunk_0201", "68bcb9f8_chunk_0013"]
        },
        "pe_ratio": {
            "pe_ratio": 32.359634,
            "context": "test",
            "sources": ["68bcb9f8_chunk_0236", "68bcb9f8_chunk_0013"]
        }
    }

    metric_context = {
        "historical_metrics": {
            "2024": {"revenue": 391035000000.0},
            "2023": {"revenue": 383285000000.0}
        },
        "peer_metrics": {
            "Sector": "Technology",
            "ETF Symbol": "XLK"
        },
        "macro_info": {
            "country": "USA",
            "gdp_growth": 2.79619035621393
        },
        "company_info": {
            "company_info": {
                "name": "Apple Inc.",
                "sector": "Technology"
            }
        }
    }

    # Erstelle Prompt für Revenue-Analyse
    prompt = build_metric_analysis_prompt(metric_data, metric_context, "revenue")
    print(prompt)

    return prompt