#base image
FROM python:3.13-slim 

#Install uv
RUN pip install uv

#Set working directory
WORKDIR /app

#Copy dependency files
COPY pyproject.toml uv.lock* ./

#Install deps
RUN uv sync --frozen --no-dev

#Copy rest of the apps 
COPY . .

#Export port for FastAPI
EXPOSE 8000

#Run FastAPI apps 
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
