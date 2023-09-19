# La Cosa Backend

## Para empezar a trabajar:
~~~
python3 -m venv lacosa_venv
source lacosa_venv
~~~

## Para levantar
~~~
cd src
uvicorn main:app --reload
~~~

## Extension de vscode para probar requests y no andar haciendo curls feos
https://marketplace.visualstudio.com/items?itemName=humao.rest-client

Para instalar desde la terminal:
~~~
ext install humao.rest-client
~~~

La instalan, se dirigen a ./requests, y en un archivo escriben como seria la request. Esta la de crear_partida de ejemplo.

## Formato standard del codigo
Black, está la extension. 