FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY bridge_crd_controller.py bridge_crd_controller.py

CMD ["python", "bridge_crd_controller.py"]
