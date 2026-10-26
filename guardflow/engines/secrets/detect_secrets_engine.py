from detect_secrets.core.scan import scan_line
from detect_secrets.settings import transient_settings

from guardflow.engines.secrets.base import (
    SecretDetection,
    SecretsEngine,
)


DEFAULT_PLUGIN_CONFIGURATION = {
    "plugins_used": [
        {"name": "AWSKeyDetector"},
        {"name": "ArtifactoryDetector"},
        {"name": "AzureStorageKeyDetector"},
        {"name": "BasicAuthDetector"},
        {"name": "CloudantDetector"},
        {"name": "DiscordBotTokenDetector"},
        {"name": "GitHubTokenDetector"},
        {"name": "GitLabTokenDetector"},
        {"name": "IbmCloudIamDetector"},
        {"name": "IbmCosHmacDetector"},
        {"name": "IPPublicDetector"},
        {"name": "JwtTokenDetector"},
        {"name": "KeywordDetector"},
        {"name": "MailchimpDetector"},
        {"name": "NpmDetector"},
        {"name": "OpenAIDetector"},
        {"name": "PrivateKeyDetector"},
        {"name": "PypiTokenDetector"},
        {"name": "SendGridDetector"},
        {"name": "SlackDetector"},
        {"name": "SoftlayerDetector"},
        {"name": "SquareOAuthDetector"},
        {"name": "StripeDetector"},
        {"name": "TelegramBotTokenDetector"},
        {"name": "TwilioKeyDetector"},
    ]
}


class DetectSecretsEngine(SecretsEngine):
    """
    GuardFlow adapter for detect-secrets.

    The configuration is intentionally optimized for natural-language
    LLM input instead of source-code repository scanning.

    High-entropy Base64 and Hex detectors are disabled by default because
    they create excessive false positives on ordinary prose.
    """

    def __init__(
        self,
        plugin_configuration: dict | None = None,
    ) -> None:
        self._plugin_configuration = (
            plugin_configuration
            or DEFAULT_PLUGIN_CONFIGURATION
        )

    def detect(
        self,
        text: str,
    ) -> list[SecretDetection]:
        detections: list[SecretDetection] = []

        offset = 0

        with transient_settings(
            self._plugin_configuration
        ):
            for line in text.splitlines(
                keepends=True
            ):
                content = line.rstrip("\r\n")

                detections.extend(
                    self._scan_line(
                        line=content,
                        base_offset=offset,
                    )
                )

                offset += len(line)

        return self._deduplicate(
            detections
        )

    @staticmethod
    def _scan_line(
        line: str,
        base_offset: int,
    ) -> list[SecretDetection]:
        detections: list[
            SecretDetection
        ] = []

        for secret in scan_line(line):
            secret_value = (
                secret.secret_value
            )

            if not secret_value:
                continue

            search_from = 0

            while True:
                position = line.find(
                    secret_value,
                    search_from,
                )

                if position == -1:
                    break

                detections.append(
                    SecretDetection(
                        secret_type=(
                            secret.type
                        ),
                        start=(
                            base_offset
                            + position
                        ),
                        end=(
                            base_offset
                            + position
                            + len(
                                secret_value
                            )
                        ),
                    )
                )

                search_from = (
                    position
                    + len(
                        secret_value
                    )
                )

        return detections

    @staticmethod
    def _deduplicate(
        detections: list[
            SecretDetection
        ],
    ) -> list[SecretDetection]:
        unique = {
            (
                detection.secret_type,
                detection.start,
                detection.end,
            ): detection
            for detection in detections
        }

        return sorted(
            unique.values(),
            key=lambda detection: (
                detection.start,
                detection.end,
                detection.secret_type,
            ),
        )