def choose_language(func):
    
    def wrapper(*args, **kwargs):
        
        func()
        
    return wrapper