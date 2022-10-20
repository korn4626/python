import hashlib
import psycopg2
from functools import wraps


def calc_file_hash(path):
    f = open(path, 'rb')
    data = f.read()
    hash = hashlib.md5(data).hexdigest()
    return hash

def decorator_op_query(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        cmd = """from {0}_op import {1} as new_func 
        """.format(func.__module__, func.__name__)
        try:
            exec(cmd)
            # return new_func(*args, **kwargs)
            result = eval("new_func(*args, **kwargs)")
        except ImportError:
            result = func(*args, **kwargs)
        except ModuleNotFoundError:
            result = func(*args, **kwargs)
        except Exception as e:
            print(e)
            raise e
        return result
    return decorator
