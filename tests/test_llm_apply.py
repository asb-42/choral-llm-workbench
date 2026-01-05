from music21 import stream
from core.score.reharmonize import replace_chord_in_measure, replace_chords_in_measures
from core.score.llm import apply_llm_chords_to_measures

def create_dummy_score():
    """Erstellt einen einfachen Score mit 4 Takten"""
    s = stream.Score()
    p = stream.Part()
    for i in range(4):
        m = stream.Measure(number=i+1)
        p.append(m)
    s.append(p)
    return s

def main():
    # Dummy Score erzeugen
    score = create_dummy_score()
    print("Original Score:")
    for m in score.parts[0].getElementsByClass(stream.Measure):
        print(f"Takt {m.number}: {list(m.notes)}")

    # Test replace_chord_in_measure
    replace_chord_in_measure(score, 1, 'C', 'major')
    replace_chord_in_measure(score, 2, 'A', 'minor')
    print("\nNach replace_chord_in_measure:")
    for m in score.parts[0].getElementsByClass(stream.Measure):
        print(f"Takt {m.number}: {list(m.notes)}")

    # Test replace_chords_in_measures
    chords_data = [
        {'measure': 3, 'root': 'F', 'quality': 'major'},
        {'measure': 4, 'root': 'G', 'quality': 'major'}
    ]
    replace_chords_in_measures(score, chords_data)
    print("\nNach replace_chords_in_measures:")
    for m in score.parts[0].getElementsByClass(stream.Measure):
        print(f"Takt {m.number}: {list(m.notes)}")

    # Test apply_llm_chords_to_measures (Multi-Voice)
    llm_results = {
        'S': {'measure': 1, 'root': 'D', 'quality': 'major'},
        'A': {'measure': 2, 'root': 'E', 'quality': 'minor'}
    }
    apply_llm_chords_to_measures(score, llm_results)
    print("\nNach apply_llm_chords_to_measures:")
    for m in score.parts[0].getElementsByClass(stream.Measure):
        print(f"Takt {m.number}: {list(m.notes)}")

if __name__ == "__main__":
    main()
