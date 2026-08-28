import json
import os
import subprocess
from typing import Protocol, TypeVar

from pydantic import BaseModel
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


T = TypeVar(
    "T",
    bound=BaseModel,
)


class AiProviderError(Exception):
    pass


class AiProviderUnavailableError(AiProviderError):
    pass


class AiModelMissingError(AiProviderError):
    pass


class AiGenerationError(AiProviderError):
    pass


class AiProvider(Protocol):
    model: str

    def check_status(
        self,
    ) -> tuple[bool, str]:
        ...

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        ...


def _get_wsl_windows_host() -> str | None:
    """
    Return the Windows host IP when MyGarage is running inside WSL.
    """
    try:
        result = subprocess.run(
            [
                "ip",
                "route",
                "show",
                "default",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=2,
        )

        parts = result.stdout.strip().split()

        if "via" not in parts:
            return None

        via_index = parts.index("via")

        if (
            via_index + 1
            >= len(parts)
        ):
            return None

        return parts[
            via_index + 1
        ]

    except (
        FileNotFoundError,
        subprocess.SubprocessError,
        ValueError,
    ):
        return None


class OllamaProvider:
    def __init__(
        self,
    ) -> None:
        configured_url = (
            os.getenv(
                "OLLAMA_BASE_URL"
            )
        )

        self.model = os.getenv(
            "OLLAMA_MODEL",
            "qwen3:4b-instruct",
        )

        self.timeout_seconds = float(
            os.getenv(
                "OLLAMA_TIMEOUT_SECONDS",
                "120",
            )
        )

        self.num_ctx = int(
            os.getenv(
                "OLLAMA_NUM_CTX",
                "8192",
            )
        )

        self.base_urls: list[str] = []

        if configured_url:
            self.base_urls.append(
                configured_url.rstrip(
                    "/"
                )
            )

        self.base_urls.extend(
            [
                "http://127.0.0.1:11434",
                "http://localhost:11434",
            ]
        )

        windows_host = (
            _get_wsl_windows_host()
        )

        if windows_host:
            self.base_urls.append(
                (
                    f"http://"
                    f"{windows_host}"
                    f":11434"
                )
            )

        self.base_urls = list(
            dict.fromkeys(
                self.base_urls
            )
        )

        self.active_base_url: (
            str | None
        ) = None

    def _request_url(
        self,
        base_url: str,
        path: str,
        *,
        method: str = "GET",
        payload: dict | None = None,
        timeout: float | None = None,
    ) -> dict:
        body = None

        headers = {
            "Content-Type":
                "application/json",
        }

        if payload is not None:
            body = json.dumps(
                payload
            ).encode(
                "utf-8"
            )

        request = Request(
            (
                f"{base_url}"
                f"{path}"
            ),
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(
                request,
                timeout=(
                    timeout
                    or self.timeout_seconds
                ),
            ) as response:
                raw = (
                    response
                    .read()
                    .decode(
                        "utf-8"
                    )
                )

        except HTTPError as exc:
            try:
                message = (
                    exc.read()
                    .decode(
                        "utf-8"
                    )
                )

            except Exception:
                message = str(
                    exc
                )

            raise AiProviderError(
                message
            ) from exc

        except URLError as exc:
            raise (
                AiProviderUnavailableError(
                    (
                        f"Ollama is not "
                        f"reachable at "
                        f"{base_url}."
                    )
                )
            ) from exc

        try:
            return json.loads(
                raw
            )

        except json.JSONDecodeError as exc:
            raise AiProviderError(
                (
                    "Ollama returned "
                    "invalid JSON."
                )
            ) from exc

    def _find_ollama(
        self,
    ) -> tuple[
        str | None,
        dict | None,
    ]:
        if self.active_base_url:
            try:
                payload = (
                    self._request_url(
                        self.active_base_url,
                        "/api/tags",
                        timeout=3,
                    )
                )

                return (
                    self.active_base_url,
                    payload,
                )

            except AiProviderError:
                self.active_base_url = (
                    None
                )

        for base_url in self.base_urls:
            try:
                payload = (
                    self._request_url(
                        base_url,
                        "/api/tags",
                        timeout=3,
                    )
                )

                self.active_base_url = (
                    base_url
                )

                return (
                    base_url,
                    payload,
                )

            except AiProviderError:
                continue

        return (
            None,
            None,
        )

    def _request(
        self,
        path: str,
        *,
        method: str = "GET",
        payload: dict | None = None,
    ) -> dict:
        if not self.active_base_url:
            base_url, _ = (
                self._find_ollama()
            )

            if not base_url:
                raise (
                    AiProviderUnavailableError(
                        (
                            "Ollama is not "
                            "reachable from "
                            "MyGarage. Make "
                            "sure Ollama is "
                            "running on Windows."
                        )
                    )
                )

        assert (
            self.active_base_url
            is not None
        )

        return self._request_url(
            self.active_base_url,
            path,
            method=method,
            payload=payload,
        )

    def check_status(
        self,
    ) -> tuple[
        bool,
        str,
    ]:
        base_url, payload = (
            self._find_ollama()
        )

        if (
            base_url is None
            or payload is None
        ):
            return (
                False,
                (
                    "Ollama is not reachable. "
                    "Make sure Ollama is "
                    "running on Windows and "
                    "port 11434 is accessible "
                    "from WSL."
                ),
            )

        installed_models = {
            item.get(
                "name",
                "",
            )
            for item
            in payload.get(
                "models",
                [],
            )
        }

        if (
            self.model
            not in installed_models
        ):
            return (
                False,
                (
                    f"Ollama is reachable at "
                    f"{base_url}, but "
                    f"{self.model} is not "
                    f"installed."
                ),
            )

        return (
            True,
            (
                f"{self.model} is ready "
                f"through local Ollama."
            ),
        )

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        available, message = (
            self.check_status()
        )

        if not available:
            if (
                "not installed"
                in message
            ):
                raise (
                    AiModelMissingError(
                        message
                    )
                )

            raise (
                AiProviderUnavailableError(
                    message
                )
            )

        payload = self._request(
            "/api/chat",
            method="POST",
            payload={
                "model":
                    self.model,

                "messages": [
                    {
                        "role":
                            "system",
                        "content":
                            system_prompt,
                    },
                    {
                        "role":
                            "user",
                        "content":
                            user_prompt,
                    },
                ],

                "stream":
                    False,

                "format":
                    response_model
                    .model_json_schema(),

                "keep_alive":
                    "10m",

                "options": {
                    "temperature":
                        0.1,

                    "num_ctx":
                        self.num_ctx,

                    "num_predict":
                        900,
                },
            },
        )

        try:
            content = (
                payload[
                    "message"
                ][
                    "content"
                ]
            )

            parsed = json.loads(
                content
            )

            return (
                response_model
                .model_validate(
                    parsed
                )
            )

        except (
            KeyError,
            TypeError,
            json.JSONDecodeError,
            ValueError,
        ) as exc:
            raise (
                AiGenerationError(
                    (
                        "The local AI "
                        "returned an invalid "
                        "structured response."
                    )
                )
            ) from exc