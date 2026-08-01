"""
One-off helper: hash an admin password for storage in .env as ADMIN_PASSWORD_HASH.
Usage:
    python generate_password_hash.py
"""
import getpass
import bcrypt

if __name__ == "__main__":
    password = getpass.getpass("Choose an admin password: ")
    confirm = getpass.getpass("Confirm: ")

    if password != confirm:
        print("Passwords did not match. Try again.")
        raise SystemExit(1)

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    print("\nAdd this line to backend/.env:\n")
    print(f"ADMIN_PASSWORD_HASH={hashed}")
