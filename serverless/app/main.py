# import pkgutil
# import importlib
from app.api import router
from app.core.config import settings
from app.exceptions import init_exception_handler
from app.log import init_log
from app.middlewares import init_middlewares
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(title="FastAPI Sample")
# app = FastAPI(
#     title='MyWallets API', lifespan=lifespan
# )

init_log()
init_exception_handler(app)
init_middlewares(app)

# routes ディレクトリ内のモジュールを全て読み込んで router を登録する
# import app.routes as routes_pkg
#
# for _, module_name, _ in pkgutil.iter_modules(routes_pkg.__path__):
#    module = importlib.import_module(f'app.routes.{module_name}')
#    # 各モジュールで `router: APIRouter` を定義しておくこと
#    app.include_router(module.router)
app.include_router(router, prefix=settings.API_V1_STR)

handler = Mangum(app)
