import json
import os
from typing import (
    Protocol,
    TypeVar,
)

from pydantic import (
    BaseModel,
)

from urllib.error import (
    HTTPError,
    URLError,
)
from urllib.request import (
    Request,
    urlopen,
)


T = TypeVar(
    "T",
    bound=BaseModel,
)


class AiProviderError(
    Exception
):
    pass


class AiProviderUnavailableError(
    AiProviderError
):
    pass


class AiModelMissingError(
    AiProviderError
):
    pass


class AiGenerationError(
    AiProviderError
):
    pass


class AiProvider(
    Protocol
):
    model: str

    def check_status(
        self,
    ) -> tuple[
        bool,
        str,
    ]:
        ...


    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model:
            type[T],
    ) -> T:
        ...


class OllamaProvider:
    def __init__(
        self,
    ):
        self.base_url = (
            os.getenv(
                "OLLAMA_BASE_URL",
                (
                    "http://"
                    "127.0.0.1:"
                    "11434"
                ),
            )
            .rstrip(
                "/"
            )
        )

        self.model = (
            os.getenv(
                "OLLAMA_MODEL",
                (
                    "qwen3:"
                    "4b-instruct"
                ),
            )
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


    def _request(
        self,
        path: str,
        *,
        method: str = "GET",
        payload:
            dict
            | None = None,
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
                f"{self.base_url}"
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
                    self
                    .timeout_seconds
                ),
            ) as response:
                raw = (
                    response
                    .read()
                    .decode(
                        "utf-8"
                    )
                )

        except URLError as exc:
            raise (
                AiProviderUnavailableError(
                    (
                        "Ollama is not "
                        "reachable. Make "
                        "sure Ollama is "
                        "running locally."
                    )
                )
            ) from exc

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


    def check_status(
        self,
    ) -> tuple[
        bool,
        str,
    ]:
        try:
            payload = (
                self._request(
                    "/api/tags"
                )
            )

        except AiProviderError as exc:
            return (
                False,
                str(
                    exc
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
                    f"Ollama is running, "
                    f"but {self.model} "
                    f"is not installed."
                ),
            )

        return (
            True,
            (
                f"{self.model} "
                f"is ready."
            ),
        )


    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model:
            type[T],
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

        payload = (
            self._request(
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
        )

        try:
            content = (
                payload[
                    "message"
                ][
                    "content"
                ]
            )

            parsed = (
                json.loads(
                    content
                )
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
                        "returned an "
                        "invalid response."
                    )
                )
            ) from exc