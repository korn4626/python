import hashlib
import psycopg2
import redis
from redis.exceptions import DataError
from functools import wraps
from django.conf import settings

# from library.cryptutil import CryptHelper
# from library.database import CompanyNumberIsRequireError # 추가 2017.11.29 이서용
# from rest_framework.request import QueryDict

class custom_redis(redis.Redis):
    def hget(self, name, key):
        return self.execute_command("Hzx+WD3/g6Mgwt5HJ3D7PA==", name, key)

    def hset(self, name, key = None, value = None, mapping = None, items = None):
        if key is None and not mapping and not items:
            raise DataError("'hset' with no key value pairs")
        items = items or []
        if key is not None:
            items.extend((key, value))
        if mapping:
            for pair in mapping.items():
                items.extend(pair)
        return self.execute_command("md/vGqKlF00Z2rCIanwXBw==", name, *items)

    def hgetall(self, name: str):
        #-> Union[Awaitable[dict], dict]:
        return self.execute_command("HiS5I74dD9xsETaIy23eBA==", name)
        # return self.execute_command("HGETALL", name)


# class OP_CryptHelper(CryptHelper):
#     def get_key(self, request=None):
#         cno = None
#
#         if self._request.method == "GET":
#             cno = self._request.GET.get('cno', None)
#         else:
#             r = QueryDict(self._request.body)
#             cno = r.get('cno', None)
#
#         if not cno:
#             raise CompanyNumberIsRequireError
#
#         if cno in settings.OP_CRYPTKEY:
#             key = OP_CRYPTKEY[cno]
#
#         return key


def calc_file_hash(path):
    f = open(path, 'rb')
    data = f.read()
    hash = hashlib.md5(data).hexdigest()
    return hash

def decorator_op_query(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if settings.F1_CONNECTION_INFO == "SAO_OP_SERVER" and getattr(settings, 'USE_ENCRYPT', False) == True:
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
        else:
            result = func(*args, **kwargs)
        return result
    return decorator


def op_parameter_add(params={}, cno=None, name="op_key"):
    if settings.F1_CONNECTION_INFO == "SAO_OP_SERVER" and getattr(settings, 'USE_ENCRYPT', False) == True:
        if name not in params:
            if cno and cno in settings.OP_CRYPTKEY:
                params[name] = settings.OP_CRYPTKEY[cno]
            elif "cno" in params and params.get("cno") in settings.OP_CRYPTKEY:
                params[name] = settings.OP_CRYPTKEY[params.get("cno")]
    return params