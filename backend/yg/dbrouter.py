class Router(object):
    def __init__(self):
        self.model_list = ["default", "mongo"]
    
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "default":
            return "default"
        elif model._meta.app_label == "mongo":
            return "mongo"
        return None
    
    def db_for_write(self, model, **hints):
        if model._meta.app_label == "default":
            return "default"
        elif model._meta.app_label == "mongo":
            return "mongo"
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == "default" or \
            obj2._meta.app_label == "default":
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "default":
            return db == "default"
        if app_label == "mongo":
            return db == "mongo"
        return True