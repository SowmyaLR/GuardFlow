from guardflow.engines.secrets.detect_secrets_engine import (
    DetectSecretsEngine,
)


def test_detects_keyword_based_secret():
    engine = DetectSecretsEngine()

    text = (
        'api_key = '
        '"p7V8Q2mL9xK4nR6sT1wY3zA5bC8dE0fG"'
    )

    detections = engine.detect(text)

    assert len(detections) >= 1


def test_does_not_flag_normal_sentence():
    engine = DetectSecretsEngine()

    text = (
        "What are the best home loan options "
        "for a salaried employee?"
    )

    detections = engine.detect(text)

    assert detections == []


def test_secret_value_is_not_part_of_detection_object():
    engine = DetectSecretsEngine()

    secret_value = (
        "p7V8Q2mL9xK4nR6sT1wY3zA5bC8dE0fG"
    )

    detections = engine.detect(
        f'password = "{secret_value}"'
    )

    assert detections

    for detection in detections:
        assert not hasattr(
            detection,
            "secret_value",
        )
def test_does_not_flag_normal_email_discussion():
    engine = DetectSecretsEngine()

    text = (
        "Please explain how API keys "
        "should be stored securely."
    )

    assert engine.detect(text) == []


def test_does_not_flag_security_education():
    engine = DetectSecretsEngine()

    text = (
        "Never paste passwords or access "
        "tokens into public chat systems."
    )

    assert engine.detect(text) == []


def test_does_not_flag_normal_tamil_text():
    engine = DetectSecretsEngine()

    text = (
        "வீட்டு கடன் வட்டி விகிதம் "
        "எவ்வளவு?"
    )

    assert engine.detect(text) == []