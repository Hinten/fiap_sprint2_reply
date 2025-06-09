from fastapi import FastAPI

from src.settings import DEBUG
from src.wokwi_api.init_sensor import init_router
from src.wokwi_api.receber_leitura import receber_router
import uvicorn
import threading

app = FastAPI()
app.include_router(init_router, prefix='/init')
app.include_router(receber_router, prefix='/leitura')

def _print_routes(app):
    for route in app.routes:
        if hasattr(route, "methods"):
            print(f"{list(route.methods)} {route.path}")

def iniciar_api():
    """
    Inicia a API
    """
    if DEBUG:
        _print_routes(app)
    uvicorn.run(app, host="0.0.0.0", port=8180)


def inciar_api_thread_paralelo():
    """
    Inicia a API em uma thread separada.
    Isso permite que a API seja executada em segundo plano enquanto outras tarefas podem ser executadas
    """
    api_thread = threading.Thread(target=iniciar_api, daemon=True)
    api_thread.start()

if __name__ == "__main__":
    from src.database.tipos_base.database import Database
    Database.init_sqlite('../../database.db')

    uvicorn.run(app, host="0.0.0.0", port=8180)