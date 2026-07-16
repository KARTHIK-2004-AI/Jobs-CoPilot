"""Base exception for the ULTRON Jobs application."""


class UltronJobsError(Exception):
    """Base exception for all ULTRON Jobs errors.

    Attributes:
        message: Human-readable description.
        error_code: Short stable machine-readable code, e.g. "CONFIG_MISSING".
                    Defaults to the class name in SCREAMING_SNAKE_CASE if not given.
        context: Optional dict of structured debugging context (never put
                 secrets/API keys in here — see Constraints).
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        context: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.message: str = message
        self.context: dict[str, object] = context or {}

        self.error_code: str
        if error_code:
            self.error_code = error_code
        else:
            # Deterministically convert CamelCase / PascalCase to SCREAMING_SNAKE_CASE
            # e.g., MissingConfigError -> MISSING_CONFIG_ERROR
            name = self.__class__.__name__
            parts: list[str] = []
            for i, char in enumerate(name):
                if i > 0 and char.isupper():
                    parts.append("_")
                parts.append(char.upper())
            self.error_code = "".join(parts)

    def __str__(self) -> str:
        """Return exception representation in the format '[ERROR_CODE] message'."""
        return f"[{self.error_code}] {self.message}"

    def to_dict(self) -> dict[str, object]:
        """Return structured dictionary of the error for serialization/logging."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
        }
