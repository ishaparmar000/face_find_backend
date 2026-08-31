face_search_backend/
│
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
│
├── config/
│   ├── __init__.py
│   │
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   │
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   │
│   ├── photos/
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── services.py
│   │
│   └── face_recognition/
│       ├── __init__.py
│       ├── apps.py
│       ├── detector.py
│       ├── embeddings.py
│       └── services.py
│
├── media/
│   └── photos/
│
└── scripts/


1) python -m venv venv
2) .\venv\Scripts\Activate.ps1
3) pip install django djangorestframework python-decouple django-cors-headers
4) django-admin startproject config .
5) python manage.py check
6) mkdir config\settings
    New-Item config\settings\__init__.py
    New-Item config\settings\development.py
    New-Item config\settings\production.py
    Move-Item config\settings.py config\settings\base.py

7) base.py
    ENVIRONMENT = "development"

8) Tell Django which settings to use -> .development

manage.py : os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
asgi.py : os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
wsgi.py : os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

9) mkdir apps
10) New-Item apps\__init__.py
11) mkdir apps\face_recognition
    New-Item apps\face_recognition\__init__.py
    New-Item apps\face_recognition\detector.py
    New-Item apps\face_recognition\embeddings.py
    New-Item apps\face_recognition\services.py
12) python manage.py startapp photos apps/photos
13) API files for photos
    New-Item apps\photos\serializers.py
    New-Item apps\photos\urls.py
    New-Item apps\photos\services.py

14) in config/settings/base.py
    inside INSTALLED_APPS = [
        "rest_framework",   -->   Django REST Framework (DRF) used to build REST APIs in Django
        "corsheaders",   -->   CORS is needed when your frontend and backend are running on different origins
        "apps.photos",

    inside MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',

Database setup --------------------------------------------------------------------------------------------------

15) install successfully Postgess & manage with vector.. 
16) psql -U postgres -c "SELECT name, default_version FROM pg_available_extensions WHERE name = 'vector';"
    name   | default_version
    --------+-----------------
    vector | 0.8.6

    psql -U postgres -c "CREATE DATABASE face_recognition;"
    psql -U postgres -d face_recognition -c "CREATE EXTENSION vector;"
    psql -U postgres -d face_recognition -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"

17) create .env file & put all database credentials there
18) database connectivity with django
    in config/settings/base.py

    Add
    from decouple import config

    Replace old with below content 
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST"),
            "PORT": config("DB_PORT"),
        }
    }

19) New-Item .gitignore
    venv/
    .env
    __pycache__/
    *.pyc
    db.sqlite3
    media/
    .vscode/
    .idea/

20) python manage.py migrate 
21) python manage.py showmigrations

---------------------------------------------------------------------------------------------------------------------------------------------------

22) pip install pgvector
23) python manage.py makemigrations photos
24) in 0001_initial.py 
    
    Add 

    from pgvector.django import VectorExtension

    inside the Migration    
    operations = [
        VectorExtension(),
        # existing operations...
    ]

25) python manage.py migrate

26) psql -U postgres -d face_recognition --> check database tables
    face_recognition=# \dt --> list all tables.. 

27) pip install opencv-python pillow numpy   (face-processing package)

28) mkdir models (place for face model)


Before installing the recognition model, veirfy OpenCv works

29) python -c "import cv2; print(cv2.__version__)"
30) python -c "from PIL import Image; import numpy; print('Pillow, NumPy and OpenCV are ready')"

31) Install InsightFace
    pip install insightface onnxruntime
    python -c "import insightface; print('InsightFace:', insightface.__version__)"
    python -c "import onnxruntime; print('ONNX Runtime:', onnxruntime.__version__)"

32) Testing image at face_recognition/test_model.py     
    it was working fine.. and can recognize the faces 

Work on API's ----------------------------------------------------------------------------------------------------------------------------------

33) Configure media files
    config/settings/base.py

    at bottom : 
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"