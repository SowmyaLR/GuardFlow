from guardflow.engines.secrets.detect_secrets_engine import (
    DetectSecretsEngine,
)


def test_detects_keyword_based_fake_secret():
    engine = DetectSecretsEngine()

    text = (
        'api_key = '
        '"p7V8Q2mL9xK4nR6sT1wY3zA5bC8dE0fG"'
    )

    detections = engine.detect(text)

    assert detections


def test_does_not_flag_normal_financial_question():
    engine = DetectSecretsEngine()

    text = (
        "What are the best home loan options "
        "for a salaried employee?"
    )

    assert engine.detect(text) == []


def test_does_not_flag_security_education():
    engine = DetectSecretsEngine()

    text = (
        "Developers should never paste passwords or API keys "
        "into public chat applications."
    )

    assert engine.detect(text) == []


def test_does_not_flag_normal_tamil_text():
    engine = DetectSecretsEngine()

    text = (
        "வீட்டு கடன் வட்டி விகிதம் எவ்வளவு?"
    )

    assert engine.detect(text) == []