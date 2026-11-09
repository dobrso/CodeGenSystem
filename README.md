# CodeGenSystem
Мультиагентная система для генерации кода. Состоит из 4ех агентов:
1. Архитектор - строит план на основе запроса пользователя
2. Роутер - решает, какую модель будет использовать разработчик
3. Разработчик - пишет код на основе плана архитектора
4. Ревьюер - оценивает код разработчика

## Требования
- Docker, Docker Sandbox
- Ollama
- Python 3.13

Важно! Если вы работаете на Windows, то Docker Sandbox будет работать только от 11 версии.

## Быстрый старт
1. Склонируйте репозиторий
```bash
git clone https://github.com/dobrso/CodeGenSystem.git
```

2. Перейдите в директорию
```bash
cd CodeGenSystem
```

3. Запульте модели с Ollama
```bash
ollama pull qwen3.5:2b
ollama pull qwen3.5:4b
ollama pull gemma3:1b
ollama pull laya
ollama pull nomic-embed-text
```

4. Забилдите и сохраните Docker-образ
```bash
docker build -t codegen:latest .
docker save codegen:latest -o codegen.tar
```

5. Загрузите Docker-образ в виде шаблона для Docker Sandbox
```bash
sbx template load codegen.tar
```

6. Создайте Sandbox
```bash
sbx create --name codegen --template codegen:lastest shell .
```

7. Запустите Sandbox
```bash
sbx run --name codegen
```

Важно! Перед этим нужно настроить гипервизора Windows и Docker Sandbox

## Пользование
```bash
/app/.venv/bin/python /app/src/codegensystem/main.py "Напиши функцию"
```
