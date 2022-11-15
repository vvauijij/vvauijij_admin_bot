FROM python
EXPOSE 8888
COPY ./main.py main.py
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD ["python", "main.py"]