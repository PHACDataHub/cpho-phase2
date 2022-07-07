# CPHO Phase 2

## How to run locally

1. Create a virtual environment:

```bash
virtualenv --python=python3.9.13 venv
```

2. Activate it:

```bash
source venv/bin/activate
```

3. Install all dependencies:

```bash
pip install -r requirements.txt
```

4. Run the script:

```bash
python manage.py runserver
```

Then open `http://127.0.0.1:8000` on your browser of choice and you should be able to see the application.

When you are done with the virtual environment, deactivate it by using:

```bash
deactivate
```

phac@cpho2
