up:
	poetry run uvicorn app:app --reload --port 8000

.PHONY: migrate-rev
migrate-rev:
	poetry run alembic revision --autogenerate -m $(name)

.PHONY: migrate-up
migrate-up:
	poetry run alembic upgrade $(rev)

.PHONY: local
local:
	docker compose -f docker-compose.local.yml up

.PHONY: test
test:
	poetry run pytest

load-models:
	mkdir -p ml/preloaded_models/toxic-classifier
	wget https://huggingface.co/IlyaGusev/rubertconv_toxic_clf/resolve/main/pytorch_model.bin -O ml/preloaded_models/toxic-classifier/pytorch_model.bin
	wget https://huggingface.co/IlyaGusev/rubertconv_toxic_clf/resolve/main/config.json -O ml/preloaded_models/toxic-classifier/config.json
	wget https://huggingface.co/IlyaGusev/rubertconv_toxic_clf/resolve/main/special_tokens_map.json -O ml/preloaded_models/toxic-classifier/special_tokens_map.json
	wget https://huggingface.co/IlyaGusev/rubertconv_toxic_clf/resolve/main/tokenizer.json -O ml/preloaded_models/toxic-classifier/tokenizer.json
	wget https://huggingface.co/IlyaGusev/rubertconv_toxic_clf/resolve/main/tokenizer_config.json -O ml/preloaded_models/toxic-classifier/tokenizer_config.json
	wget https://huggingface.co/IlyaGusev/rubertconv_toxic_clf/resolve/main/vocab.txt -O ml/preloaded_models/toxic-classifier/vocab.txt