import bcrypt
from database.database_manager import DatabaseManager

class UserRepository:
    """Handles user authentication against SQLite."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def authenticate(self, username: str, password: str):
        """Return user dict if credentials are valid, else None."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT id, uuid, username, password_hash, full_name, role, status "
            "FROM users WHERE username = ? AND is_deleted = 0",
            (username,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        stored_hash = row["password_hash"]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return {
                "id": row["id"],
                "uuid": row["uuid"],
                "username": row["username"],
                "full_name": row["full_name"],
                "role": row["role"],
                "status": row["status"]
            }
        return None