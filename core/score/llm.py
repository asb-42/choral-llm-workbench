from .reharmonize import replace_chords_in_measures

def apply_llm_chords_to_measures(score, llm_results):
    """
    Wendet LLM-Ergebnisse auf einen Score an.
    llm_results: dict, z.B.
        {'S': {'measure': 1, 'root': 'C', 'quality': 'major'}, ...}
    """
    for voice, data in llm_results.items():
        measure = data.get("measure")
        root = data.get("root")
        quality = data.get("quality", "major")
        if measure is not None and root is not None:
            replace_chords_in_measures(score, {measure: (root, quality)})
    return score
