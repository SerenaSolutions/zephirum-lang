# ZEPHIRUM Core — imagem unica, com QPU opcional.
# Núcleo (ZCA, QASM3, verificador) não precisa de nenhuma dependência externa.
FROM python:3.12-slim AS base

ARG WITH_QPU=0
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY zephirum_core ./zephirum_core
COPY requirements.txt requirements-qpu.txt ./

# Camada QPU só quando pedida: imagem base fica pequena e sem qiskit.
RUN if [ "$WITH_QPU" = "1" ]; then \
      pip install --no-cache-dir -r requirements-qpu.txt; \
    fi

RUN useradd --create-home --uid 10001 zephirum && chown -R zephirum:zephirum /app
USER zephirum

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=4).status==200 else 1)"

CMD ["python", "-m", "zephirum_core.server"]
