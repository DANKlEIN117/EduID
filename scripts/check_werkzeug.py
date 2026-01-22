import sys
import importlib
print('Python', sys.version)
try:
    import werkzeug
    print('werkzeug', werkzeug.__version__)
    m = importlib.import_module('werkzeug.sansio.http')
    print('imported', m)
except Exception as e:
    print('ERROR:', type(e).__name__, e)
