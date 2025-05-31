from enum import Enum


class Roles(str, Enum):
    """
    Enum for user roles.
    """
    ADMIN = "admin"
    CLIENT = "client"
