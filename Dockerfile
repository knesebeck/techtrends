FROM python:2.7.18-stretch
WORKDIR /app
ADD ./techtrends /app
RUN pip install --upgrade pip && pip install -r requirements.txt && python init_db.py
EXPOSE 3111
CMD ["python", "app.py"]