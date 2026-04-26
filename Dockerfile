# Używamy lekkiego obrazu Pythona
FROM python:3.11-slim

# Ustawiamy zmienne środowiskowe, aby Python nie tworzył plików .pyc i wypisywał logi od razu
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalujemy zależności systemowe niezbędne dla biblioteki mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Ustawiamy folder roboczy wewnątrz kontenera
WORKDIR /app

# Kopiujemy plik z bibliotekami i instalujemy je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy całą resztę kodu Twojej pracy dyplomowej
COPY . .

# Cloud Run domyślnie używa portu 8080, dlatego Django powinno na nim startować
EXPOSE 8080

# Komenda startowa (zakładając, że Twój projekt nazywa się 'myproject')
# Zmień 'myproject' na nazwę folderu, w którym masz plik wsgi.py
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]