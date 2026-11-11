FROM meridian-worker:checkpoint1
RUN python -I -B -c "import duckdb, sqlglot; assert (duckdb.__version__, sqlglot.__version__) == ('1.4.4', '28.10.1')"
COPY worker.py /usr/local/lib/python3.12/site-packages/experiments/finops_sql/worker.py
COPY v3/worker.py /usr/local/lib/python3.12/site-packages/experiments/finops_sql/v3/worker.py
USER 65534:65534
ENTRYPOINT ["python","-I","-B","-m","experiments.finops_sql.v3.worker"]
