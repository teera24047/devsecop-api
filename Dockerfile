FROM python:3.9-slim

# ติดตั้ง Microsoft ODBC Driver เพื่อให้ Python คุยกับ Azure SQL ได้
RUN apt-get update && apt-get install -y gnupg2 curl
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 80
CMD ["python", "app.py"]