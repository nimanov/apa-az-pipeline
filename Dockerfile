FROM python:3.8
ADD apa_az.py .
ADD utils.py .
ADD requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "./apa_az.py"]