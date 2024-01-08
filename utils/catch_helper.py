def catch(params: str):
    new_params = []
    for param in params:
        try:
            new_params.append(int(param))
        except:
            pass
    
    return new_params
