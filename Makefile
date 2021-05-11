VENV := . .venv/bin/activate &&

create_venv:
	python3 -m venv .venv

create_db:
	${VENV} python manage.py migrate
	${VENV} echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell
	if [ -f transactions.sql ]; then cat transactions.sql | sqlite3 db.sqlite3; fi
	if [ -f exchangerates.sql ]; then cat exchangerates.sql | sqlite3 db.sqlite3; fi

clean:
	rm db.sqlite3

run:
	${VENV} python manage.py runserver 0.0.0.0:8000
