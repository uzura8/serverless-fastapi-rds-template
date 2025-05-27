# import pkgutil
# import importlib
from fastapi import FastAPI
from mangum import Mangum

from app.routes import items

app = FastAPI()

# @app.get('/')
# def read_root():
#    return {'Hello': 'World'}
#
#
# @app.get('/items/{item_id}')
# def read_item(item_id: int, q: str = None):
#    return {'item_id': item_id, 'q': q}

# routes ディレクトリ内のモジュールを全て読み込んで router を登録する
# import app.routes as routes_pkg
#
# for _, module_name, _ in pkgutil.iter_modules(routes_pkg.__path__):
#    module = importlib.import_module(f'app.routes.{module_name}')
#    # 各モジュールで `router: APIRouter` を定義しておくこと
#    app.include_router(module.router)

app.include_router(items.router)
# app.include_router(root.router)

handler = Mangum(app)
