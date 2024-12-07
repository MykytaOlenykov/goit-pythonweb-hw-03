class MessageForm:
    def __init__(self, data: dict[str, str] | None = None):
        self.data = data or {}
        self.errors = {}

    def is_valid(self):
        self.errors.clear()
        self.validate_fields()
        return not bool(self.errors)

    def validate_fields(self):
        self.validate_required("username")
        self.validate_min_length("username", 3)
        self.validate_min_length("message", 10)

    def validate_required(self, field: str):
        if not self.data.get(field, "").strip():
            self.errors[field] = f"{field} is required"

    def validate_min_length(self, field: str, min_length: int):
        value = self.data.get(field, "").strip()
        if len(value) < min_length:
            self.errors[field] = (
                f"{field} must be at least {min_length} characters long"
            )

    def get_errors(self):
        return self.errors

    def get_clean_data(self):
        return {key: value.strip() for key, value in self.data.items()}
