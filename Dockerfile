FROM python:3.11-slim

# Munkakönyvtár beállítása a konténeren belül
WORKDIR /code

# Függőségek másolása és telepítése
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# A teljes app mappa bemásolása
COPY ./app /code/app

# A szerver indítási parancsa
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]