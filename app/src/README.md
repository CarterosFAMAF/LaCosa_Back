# Estructura del proyecto

game: 
    clases Match Player, Message y Card. Aca va toda la logica del juego

router:  
    schema.py: validaciones de pedantic para inputs y outputs de endpoints
    router_*: endpoints. ¡Aca no hagan logica del juego!

models:
    models.py: modelo de base de datos pony