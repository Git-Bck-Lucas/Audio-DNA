FROM python:3.11.5-slim
WORKDIR /app
COPY requirements.txt .
# CPU-only torch zuerst installieren. Sonst zieht torch ueber sentence-transformers den
# kompletten NVIDIA-CUDA-Stack (~3 GB), den der CPU-Server nie nutzt. Das blaeht das Image
# auf und macht den Build so langsam, dass der Deploy in den Timeout laeuft.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ backend/
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]