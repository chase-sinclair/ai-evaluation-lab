FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
RUN pip install --no-cache-dir duckdb==1.4.4 sqlglot==28.10.1
COPY worker.py /opt/worker.py
USER 65534:65534
ENTRYPOINT ["python","-I","-B","/opt/worker.py"]
