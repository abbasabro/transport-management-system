# security/permissions.py

class PermissionManager:
    """
    Centralized RBAC manager.
    Instantiate with the current user's role string (e.g., 'Transport Head' or 'Transport Clerk').
    Then call has_permission(permission_string) to check access.
    """

    # All available permissions (for documentation and future validation)
    ALL_PERMISSIONS = {
        "vehicle.add",
        "vehicle.update",
        "vehicle.delete",
        "vehicle.list_view",
        "vehicle.download_report",
        "driver.add",
        "driver.update",
        "driver.delete",
        "driver.list_view",
        "driver.download_report",
        "log.add",
        "log.view",
        "repair.add",
        "repair.update",
        "repair.delete",
        "repair.list_view",
        "report.generate",
        "settings.access",
        "user.manage",
        "vehicle_type.add",
        "password.change",
    }

    # Role → set of allowed permissions
    ROLE_PERMISSIONS = {
        "Transport Head": ALL_PERMISSIONS,  # complete access
        "Transport Clerk": {
            "vehicle.list_view",
            "driver.list_view",
            "log.add",
            "log.view",
            "repair.add",
            "repair.update",
            "repair.list_view",
            "password.change",
        },
    }

    def __init__(self, user_role: str):
        self.role = user_role
        self.allowed = self.ROLE_PERMISSIONS.get(user_role, set())

    def has_permission(self, permission: str) -> bool:
        """Return True if the user has the given permission."""
        return permission in self.allowed