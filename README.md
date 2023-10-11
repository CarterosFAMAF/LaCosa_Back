# La Cosa Backend

## Para empezar a trabajar:
~~~
python3 -m venv lacosa_venv
source ./lacosa_venv/bin/activate
pip install -r requirements.txt
~~~

## Para levantar el server
~~~
uvicorn app.main:app --reload
~~~

## Para ejecutar los tests
~~~
pytest
~~~
