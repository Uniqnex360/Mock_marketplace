@echo off

        echo Setting up Marketplace Mock API...

        REM Create virtual environment
        python -m venv venv
        call venv\Scripts\activate

        REM Install dependencies
        pip install --upgrade pip
        pip install -r requirements.txt

        REM Create migrations
        python manage.py makemigrations
        python manage.py migrate

        REM Create initial data
        python manage.py setup_initial_data

        REM Collect static files
        python manage.py collectstatic --noinput

        echo Setup complete! Run 'python manage.py runserver' to start the server