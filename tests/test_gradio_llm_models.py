# File: tests/test_gradio_llm_models.py

from cli.gradio_app_llm_models import select_model, harmonize_voices

def test_select_model():
    # Dummy-LLM auswählen
    result = select_model("Dummy")
    print(result)
    assert "DummyModel" in result
    return harmonize_voices

def test_harmonize():
    harmonize_fn = test_select_model()

    # Testprompts für SATB
    prompts = {
        "S": "Make soprano line more lyrical",
        "A": "Make alto line smoother",
        "T": "Add warmth to tenor",
        "B": "Strengthen bass foundation"
    }

    results, status = harmonize_fn(prompts)
    print("Harmonization status:", status)
    print("Results:", results)

    # Überprüfen, dass alle Stimmen Ergebnisse haben
    for voice in ["S", "A", "T", "B"]:
        assert voice in results
        assert isinstance(results[voice], dict)

if __name__ == "__main__":
    test_harmonize()
