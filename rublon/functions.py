import six
import hashlib


def hash_data(data, hash_alg):
    data = data.lower()
    if six.PY3:
        data = data.encode('utf-8')
    return getattr(hashlib, hash_alg)(data).hexdigest()


def htmlspecialchars(text):
    """Python equivalent for PHP htmlspecialchars"""
    return text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def empty(var):
    if not var:
        return True
    else:
        return False