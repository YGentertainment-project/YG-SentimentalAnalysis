class Router(object):
    def __init__(self):
        self.mongo_list = ["crawler"]
    
    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.mongo_list:
            return "mongo"
        else:
            return "default"
    
    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.mongo_list:
            return "mongo"
        else:
            return "default"
    
    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label not in self.mongo_list or \
            obj2._meta.app_label not in self.mongo_list:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.mongo_list:
            if db == "mongo":
                print("mongo_list [" + db + "] : " + app_label)
                return True
            else:
                return False
        else:
            if db == "default":
                print("else_list [" + db + "] : " + app_label)
                return True
            else:
                return False