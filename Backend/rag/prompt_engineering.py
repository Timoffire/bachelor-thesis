def build_prompt(ticker: str, metric_data: dict) -> str:
    prompt_lines = [
        f"Du bist ein Finanzanalyst und sollst für die Aktie '{ticker}' verschiedene finanzielle Kennzahlen interpretieren.",
        "Für jede Metrik findest du unten den aktuellen Wert sowie relevante Hintergrundinformationen aus Dokumenten (Kontext).",
        "Bitte beantworte jede Metrik präzise und verwende dabei die gegebenen Informationen.",
        "Wenn Informationen fehlen oder unklar sind, weise höflich darauf hin.",
        "",
        "Antworte bitte ausschließlich im folgenden JSON-Format, ohne weitere Kommentare oder Text:",
        """{
  "metrics": {
    "<metric_name>": {
      "value": <metric_value>,
      "analysis": "<deine Interpretation der Metrik>"
    },
    ...
  }
}""",
        "",
        "Beginnen wir mit den Metriken:"
    ]

    for metric_name, data in metric_data.items():
        value = data.get("value", "Keine Daten")
        context = data.get("context", [])
        sources = data.get("sources", [])

        prompt_lines.append(f"\nMetrik: {metric_name}")
        prompt_lines.append(f"Wert: {value}")
        prompt_lines.append("Kontext:")
        if context:
            for i, paragraph in enumerate(context, 1):
                prompt_lines.append(f"  {i}. {paragraph}")
        else:
            prompt_lines.append("  Keine Kontextinformationen verfügbar.")

        prompt_lines.append("Quellen:")
        if sources:
            for src in sources:
                prompt_lines.append(f"  - {src}")
        else:
            prompt_lines.append("  Keine Quellen verfügbar.")

    prompt_lines.append("\nBitte gib für jede Metrik eine Interpretation im angegebenen JSON-Format zurück.")

    return "\n".join(prompt_lines)
