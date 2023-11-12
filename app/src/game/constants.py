# fijarse de meter las otras cartas.
NADA_DE_BARBACOAS = 17
FALLASTE = 16
NO_GRACIAS = 15
AQUI_ESTOY_BIEN = 14
ATERRADOR = 13
MAS_VALE_QUE_CORRAS = 12
SEDUCCION = 11
VIGILA_TUS_ESPALDAS = 10
CAMBIO_DE_LUGAR = 9
WHISKY = 8
SOSPECHA = 6
ANALISIS = 4
LANZALLAMAS = 3
INFECCION = 2
LA_COSA = 1
CUARENTENA = 18
PUERTA_ATRANCADA = 19
HACHA = 5

DECK = [
    # WITH 4 PLAYERS
    INFECCION,  # ACA ESTARIA LA COSA
    CUARENTENA ,
    CUARENTENA ,
    CUARENTENA ,
    CUARENTENA,
    CUARENTENA,
    CUARENTENA,
    CUARENTENA,
    CUARENTENA,
    CUARENTENA,
    CUARENTENA,
    SOSPECHA,  # ACA ESTARIA HACHA
    HACHA,
    HACHA,
    HACHA,
    SOSPECHA,
    WHISKY,  # ACA ESTARIA DETERMINACION
    WHISKY,  # ACA ESTARIA DETERMINACION
    HACHA,
    HACHA,
    CAMBIO_DE_LUGAR,
    VIGILA_TUS_ESPALDAS,
    HACHA,
    SEDUCCION,
    MAS_VALE_QUE_CORRAS,
    MAS_VALE_QUE_CORRAS,
    AQUI_ESTOY_BIEN,
    NO_GRACIAS,
    NO_GRACIAS,  # ACA ESTARIA FALLASTE
    NADA_DE_BARBACOAS,
    NADA_DE_BARBACOAS,  # ACA ESTARIA PUERTA ENTRANCADA
    ANALISIS,  # ACA ESTARIA OLVIDADIZO
    ANALISIS,  # ACA ESTARIA TRES,CUATRO...
    ANALISIS,  # ACA ESTARIA VUELTA Y VUELTA
    ANALISIS,  # ACA ESTARIA CITA A CIEGAS
    # WITH 5 PLAYERS
    ANALISIS,
    ATERRADOR,
    AQUI_ESTOY_BIEN,  # ACA ESTARIA CUARENTENA
    NO_GRACIAS,  # ACA ESTARIA SAL DE AQUI
    NO_GRACIAS,  # ACA ESTARIA UNO,DOS...
    NADA_DE_BARBACOAS,  # ACA ESTARIA AQUI ESTA LA FIESTA?
    # WITH 6 PLAYERS
    INFECCION,
    INFECCION,
    LANZALLAMAS,
    ANALISIS,
    ANALISIS,  # ACA ESTARIA DETERMINACION
    WHISKY,
    SEDUCCION,
    ATERRADOR,
    AQUI_ESTOY_BIEN,
    NO_GRACIAS,
    NO_GRACIAS,  # ACA ESTARIA FALLASTE
    NADA_DE_BARBACOAS,
    SOSPECHA,  # ACA ESTARIA CUERDAS PODRIDAS
    # WITH 7 PLAYERS
    INFECCION,
    INFECCION,
    SOSPECHA,
    CAMBIO_DE_LUGAR,
    SEDUCCION,
    MAS_VALE_QUE_CORRAS,
    MAS_VALE_QUE_CORRAS,  # ACA ESTARIA PUERTA ENTRANCADA
    MAS_VALE_QUE_CORRAS,  # ACA ESTARIA QUE QUEDE ENTRE NOSOTROS
    SEDUCCION,  # ACA ESTARIA NO PODEMOS SER AMIGOS
    # WITH 8 PLAYERS
    INFECCION,
    SOSPECHA,
    SEDUCCION,
    ATERRADOR,
    NO_GRACIAS,
    NO_GRACIAS,  # ACA ESTARIA REVELACIONES
    # WITH 9 PLAYERS,
    INFECCION,
    INFECCION,
    LANZALLAMAS,
    ANALISIS,
    ANALISIS,  # ACA ESTARIA HACHA
    SOSPECHA,
    ANALISIS,  # ACA ESTARIA DETERMINACION
    CAMBIO_DE_LUGAR,
    VIGILA_TUS_ESPALDAS,
    MAS_VALE_QUE_CORRAS,
    MAS_VALE_QUE_CORRAS,  # ACA ESTARIA CUARENTENA
    MAS_VALE_QUE_CORRAS,  # ACA ESTARIA CUERDAS PODRIDAS
    SEDUCCION,  # ACA ESTARIA UNO,DOS...
    SEDUCCION,  # ACA ESTARIA TRES,CUATRO...
    SEDUCCION,  # ACA ESTARIA DONDE ESTA LA FIESTA?
    SOSPECHA,  # ACA ESTARIA QUE QUEDE ENTRE NOSOTROS
    SOSPECHA,  # ACA ESTARIA VUELTA Y VUELTA
    LANZALLAMAS,  # ACA ESTARIA NO PODEMOS SER AMIGOS
    LANZALLAMAS,  # ACA ESTARIA CITA A CIEGAS
    # WITH 10 PLAYERS
    INFECCION,
    INFECCION,
    SOSPECHA,
    SOSPECHA,  # ACA ESTARIA DETERMINACION
    WHISKY,
    SEDUCCION,
    SEDUCCION,  # ACA ESTARIA UPS
    # WITH 11 PLAYERS AND 12 PLAYERS
    INFECCION,
    INFECCION,
    INFECCION,
    LANZALLAMAS,
    CAMBIO_DE_LUGAR,
    SEDUCCION,
    MAS_VALE_QUE_CORRAS,
    ATERRADOR,
    AQUI_ESTOY_BIEN,
    NO_GRACIAS,
    ATERRADOR,  # ACA ESTARIA FALLASTE
    NADA_DE_BARBACOAS,
    NADA_DE_BARBACOAS,  # ACA ESTARIA PUERTA ENTRANCADA
]


"""
DECK = [
1,2,2,2,2,2,2,2,2,3,3,5,6,6,6,6,7,7,8,9,9,10,11,11,12,12,14,15,16,17,19,23,25,28,30, #cards for 4 player
4,13,18,22,24,26,                                           #cards added to play with 5 players
2,2,3,4,7,8,11,13,14,15,16,17,21,                           #cards added to play with 6 players
2,2,6,9,11,12,19,27,29,                                     #cards added to play with 7 players
2,6,11,13,15,20,                                            #cards added to play with 8 players
2,2,3,4,5,6,7,9,10,12,18,21,24,25,26,27,28,29,30,           #cards added to play with 9 players
2,2,6,7,8,11,31,                                            #cards added to play with 10 players
2,2,2,3,9,11,12,13,14,15,16,17,19]                          #cards added to play with 11 and 12 players

    La Cosa                  = 1
    Infectado                = 2
    Lanzallamas              = 3
    Analisis                 = 4
    Hacha                    = 5
    Sospecha                 = 6
    Determinacion            = 7
    Whisky                   = 8
    Cambio de Lugar          = 9 
    Vigila tu Espalda        = 10
    Seduccion                = 11
    Mas vale que corras      = 12
    Aterrador                = 13
    Aqui estoy Bien          = 14
    No Gracias               = 15
    Fallaste                 = 16
    Nada de Barbacoa         = 17
    Cuarentena               = 18
    Puerta Atrancada         = 19
    Revelacion               = 20
    Cuerdas Podridas         = 21
    Sal de Aqui              = 22
    Olvidadizo               = 23
    uno, dos…                = 24
    tres, cuatro...          = 25
    Aqui es la fiesta?       = 26
    Que quede entre nosotros = 27
    Vuelta y vuelta          = 28 
    No podemos ser amigos    = 29
    Cita a ciegas            = 30
    Ups                      = 31
"""

# Type of cards
TYPE_LA_COSA = "La_Cosa"
TYPE_ACTION = "Accion"
TYPE_DEFENSE = "Defensa"
TYPE_INFECTED = "Infectado"
TYPE_PANIC = "Panico"
TYPE_OBSTACLE = "Obstaculo"

# Player roles
PLAYER_ROLE_HUMAN = "human"
PLAYER_ROLE_THE_THING = "the_thing"
PLAYER_ROLE_DEAD = "dead"
PLAYER_ROLE_INFECTED = "infected"
PLAYER_ROLE_LOBBY = "lobby"

MATCH_CONTINUES = 500