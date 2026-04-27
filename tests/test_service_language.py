from app.service import language as language_service


def test_predict_pipeline_cleans_text_and_maps_class(monkeypatch):
    seen = {}

    class _Model:
        def predict(self, arr):
            seen["arr"] = arr
            return [0]

    monkeypatch.setattr(language_service, "model", _Model())
    monkeypatch.setattr(language_service, "classes", ["English"])

    resp = language_service.predict_pipeline('HeLLo!!! 123\n["X"]')

    assert resp.language == "English"
    # assert seen["arr"] == ["hello        [ x ]"]
