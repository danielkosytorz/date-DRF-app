### Variables ###

containers-tool = docker-compose
dev-dockerfile = -f docker-compose.yml

### Development ###

.PHONY: build
build:
	$(containers-tool) $(dev-dockerfile) build

.PHONY: up
up:
	$(containers-tool) $(dev-dockerfile) up --remove-orphans

### OPTIONS ###

.PHONY: makemigrations
makemigrations:
	$(containers-tool) run --rm backend bash -c 'python manage.py makemigrations && python manage.py migrate'

.PHONY: django-shell
django-shell:
	$(containers-tool) exec backend bash -c "./manage.py shell"

.PHONY: format
format:
	docker-compose exec backend bash -c "python -m black . && python -m isort ."

.PHONY: test-backend
test-backend:
	$(containers-tool) run backend bash -c "python manage.py test"