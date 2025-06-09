from src.dashboard.main import main as dashboard_main
from dotenv import load_dotenv


import os

def main():
    """
    Função principal do aplicativo Streamlit.
    para rodar o aplicativo, execute o seguinte comando:
    streamlit run main_dash.py
    """
    load_dotenv()

    dashboard_main()

if __name__ == "__main__":
    main()
