#!/bin/bash

        echo "Setting up Marketplace Mock API..."

        # Create virtual environment
        python3 -m venv venv
        source venv/bin/activate

        # Install dependencies
        pip install --upgrade pip
        pip install -r requirements.txt

        # Create migrations
        python manage.py makemigrations
        python manage.py migrate

        # Create initial data
        python manage.py setup_initial_data

        # Collect static files
        python manage.py collectstatic --noinput

        echo "Setup complete! Run 'python manage.py runserver' to start the server"