from dataclasses import dataclass


@dataclass(slots=True)
class AuthenticatedUserDTO:
    access_token: str
