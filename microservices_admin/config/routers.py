class AppDBRouter:
    """
    A router to control all database operations on models in the
    assigned application databases.
    """
    app_db_mapping = {
        'auth_micro': 'kinoplus_auth_db',  # Use kinoplus_auth_db for auth_micro app
    }

    def db_for_read(self, model, **hints):
        """Direct read operations to the appropriate database."""
        if model._meta.app_label in self.app_db_mapping:
            return self.app_db_mapping[model._meta.app_label]
        return 'default'

    def db_for_write(self, model, **hints):
        """Direct write operations to the appropriate database."""
        if model._meta.app_label in self.app_db_mapping:
            return self.app_db_mapping[model._meta.app_label]
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations within the same app or between apps in the same database."""
        db_set = {self.db_for_read(obj1), self.db_for_read(obj2)}
        if len(db_set) == 1:  # Both objects are in the same database
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure that migrations are directed to the correct database.
        auth_micro models should only migrate to kinoplus_auth_db.
        All other apps should only migrate to the default database.
        """
        if app_label == 'auth_micro':
            return db == 'kinoplus_auth_db'
        return db == 'default'
