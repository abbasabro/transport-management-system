import bcrypt
import uuid,sqlite3
from datetime import datetime
from database.database_manager import DatabaseManager


class UserRepository:
    """Handles user authentication and management against the SQLite users table."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def authenticate(self, username: str, password: str) -> dict:
        """
        Verify username and password.
        Returns user dict if credentials are valid and user is Active.
        Raises ValueError('USER_INACTIVE') if the user is inactive.
        Raises ValueError('Invalid credentials') if username/password is wrong.
        """
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT id, uuid, username, password_hash, full_name, role, status "
            "FROM users WHERE username = ? AND is_deleted = 0",
            (username,),
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError("Invalid credentials")

        # Check if user is active
        if row["status"] != "Active":
            raise ValueError("USER_INACTIVE")

        stored_hash = row["password_hash"]
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            return {
                "id": row["id"],
                "uuid": row["uuid"],
                "username": row["username"],
                "full_name": row["full_name"],
                "role": row["role"],
                "status": row["status"],
            }
        raise ValueError("Invalid credentials")

    def get_all_users(self) -> list[dict]:
        """Return all non‑deleted users."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT id, uuid, username, full_name, role, status "
            "FROM users WHERE is_deleted = 0 ORDER BY username"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, user_id: int) :
        """Return a single user by id."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT id, uuid, username, full_name, role, status "
            "FROM users WHERE id = ? AND is_deleted = 0",
            (user_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def add_user(self, username: str, password: str, full_name: str, role: str) -> bool:
        """Insert a new user with bcrypt hashed password. Raises ValueError on duplicate username."""
        if not username or not password:
            raise ValueError("Username and password are required.")
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        new_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO users (uuid, username, password_hash, full_name, role, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'Active', ?)
                """,
                (new_uuid, username, hashed, full_name, role, now),
            )
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: users.username" in str(e):
                raise ValueError(f"Username '{username}' already exists.")
            raise e

    def update_user(self, user_id: int, username: str, full_name: str, role: str, status: str) -> bool:
        """Update user details (except password). Raises ValueError on duplicate username."""
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE users
                SET username = ?, full_name = ?, role = ?, status = ?, updated_at = ?
                WHERE id = ? AND is_deleted = 0
                """,
                (username, full_name, role, status, now, user_id),
            )
            if cursor.rowcount == 0:
                raise ValueError("User not found.")
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: users.username" in str(e):
                raise ValueError(f"Username '{username}' already exists.")
            raise e

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Verify old password and update to new password (bcrypt)."""
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id = ? AND is_deleted = 0", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("User not found.")
        if not bcrypt.checkpw(old_password.encode("utf-8"), row["password_hash"].encode("utf-8")):
            raise ValueError("Current password is incorrect.")
        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        now = datetime.now().isoformat()
        cursor.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
            (new_hash, now, user_id),
        )
        self.db.conn.commit()
        return True

    def set_password(self, user_id: int, new_password: str) -> bool:
        """Set a new password for a user (admin override, no old password required)."""
        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ? AND is_deleted = 0",
            (new_hash, now, user_id),
        )
        if cursor.rowcount == 0:
            raise ValueError("User not found.")
        self.db.conn.commit()
        return True

    def set_user_status(self, user_id: int, status: str) -> bool:
        """Activate or Deactivate a user. Raises ValueError if user not found."""
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        cursor.execute(
            "UPDATE users SET status = ?, updated_at = ? WHERE id = ? AND is_deleted = 0",
            (status, now, user_id),
        )
        if cursor.rowcount == 0:
            raise ValueError("User not found.")
        self.db.conn.commit()
        return True