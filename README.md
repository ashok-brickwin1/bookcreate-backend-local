# bookcreate-backend-local


## Database Alembic Initiliaze and changes:


Step-by-step guide for a new user to initialize Alembic, create a migration.
-----

#  Database Migration Guide (Alembic)

This project uses **Alembic** to manage database schema changes, ensuring your local database schema matches the SQLAlchemy models in the application code.

## 1\. Initial Setup & Initialization

Follow these steps only if the `alembic/` directory and `alembic.ini` file **do not already exist** in the root of the project.

1.  **Register Tables** :
    Register your new tables inside /models/__init__.py file.

2.  **Create the Initial Migration**:
    This generates the first script to create all tables based on your current models.

    ```bash
    alembic revision --autogenerate -m "Initial schema setup"
    ```
3. **Verify Migration**:
    Verify the migation file generated inside alembic/versions folder. Check the changes written.

5.  **Apply the Migration**:
    Run the initial migration on your local database.

    ```bash
    alembic upgrade head
    ```

## 2\. Creating New Migrations

Whenever you **add, change, or remove a model/column**, you must generate and apply a new migration script.

1.  **Generate Script**:

    ```bash
    alembic revision --autogenerate -m "Added the new 'status' column to the User model"
    ```

    *Alembic compares your models to the database and writes a new `.py` file in `alembic/versions/`.*

2.  **Review the Script**:
    **Always open the generated `.py` file** and check the `upgrade()` and `downgrade()` functions to ensure Alembic detected your changes correctly.

3.  **Apply to Local DB**:

    ```bash
    alembic upgrade head
    ```