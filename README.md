# CPHO Phase 2

## How to run locally

Assumes you have Python installed in system.

### Backend

1. Create a virtual environment:

```bash
python -m venv venv
```

1. Activate it:

Windows
```
.\venv\Scripts\activate
```

Mac/Linux
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

When you are done with the virtual environment, deactivate it by using:

```bash
deactivate
```

### Frontend

While starting just the Django app does let you interact with the app, it uses the latest *build* project in the frontend.
To develop frontend without having to rebuild the project every time, open another terminal and use the following commands:

Enter frontend folder
```bash
cd frontend
```

Install dependencies
```bash
npm install
```

Start development app
```bash
npm start
```

Access `` to see the app in the browser.

phac@cpho2
