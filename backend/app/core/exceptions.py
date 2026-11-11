from fastapi import HTTPException, status


class PerturixException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code

class ConfigurationError(PerturixException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail, error_code="CONFIG_ERROR")

class FileValidationError(PerturixException):
    def __init__(self, detail: str, error_code: str = "FILE_INVALID"):
        super().__init__(status_code=400, detail=detail, error_code=error_code)

class AttackNotFoundException(PerturixException):
    def __init__(self, attack_name: str):
        super().__init__(status_code=404, detail=f"Attack '{attack_name}' not found in registry.", error_code="ATTACK_NOT_FOUND")

class AttackValidationException(PerturixException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail, error_code="ATTACK_VALIDATION_FAILED")

class AttackExecutionException(PerturixException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail, error_code="ATTACK_EXECUTION_FAILED")

class ResourceNotFoundError(PerturixException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, error_code="NOT_FOUND")
