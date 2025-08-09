FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /text-to-sql

# requirements 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY ./app /text-to-sql/app

# 환경변수 설정
ENV PYTHONPATH=/text-to-sql

# 포트 노출
EXPOSE 8000

# 앱 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]