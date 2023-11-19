def request_method_table(method_name: str) -> str:
    hash_table = {
        "GET": "view"
        , "PATCH": "change"
        , "PUT": "change"
        , "DELETE": "delete"
        , "POST": "add"
    }
    
    return hash_table[method_name]