import subprocess
import time

def run_fastapi():
    """Runs the FastAPI server on port 8000."""
    return subprocess.Popen(["uvicorn", "scraper_bot.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

def run_streamlit():
    """Runs the Streamlit app on default port 8501."""
    return subprocess.Popen(["streamlit", "run", "scraper_bot/ui.py"])

if __name__ == "__main__":
    fastapi_process = run_fastapi()
    time.sleep(2)

    streamlit_process = run_streamlit()

    try:
        fastapi_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("Stopping applications...")
        fastapi_process.terminate()
        streamlit_process.terminate()