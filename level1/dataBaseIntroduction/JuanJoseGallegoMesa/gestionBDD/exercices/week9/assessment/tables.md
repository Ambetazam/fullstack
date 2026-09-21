🗄️caso_concierto5 tablas

Para trabajar en ella: USE caso_concierto;

        id_personaINTPKauto
        nombreVARCHAR(40)obligatorio
        apellidoVARCHAR(40)obligatorio
        rolVARCHAR(40)obligatorio
        contactoVARCHAR(90)obligatorio
    id_persona	nombre	apellido	rol	contacto
    1	Daniel	Arango Cortés	Vocalista	daniel.arango@nocturnos.co | 3105550101
    2	Julián	Mesa Toro	Guitarrista	julian.mesa@nocturnos.co | 3125550202
    3	Sofía	Restrepo Ángel	Productora	sofia@restrepoproducciones.com | 3005554471
    4	Camilo	Ríos Puerta	Representante	camilo.rios@nocturnos.co | 3155550404
    5	Renata	Gil Ospina	Corista	renata.gil@nocturnos.co | 3185550505
    6	Bruno	Salazar Peña	Técnico de sonido	bruno.salazar@sonidovivo.co | 3115550606

    … y 2 fila(s) más. Míralas con SELECT * FROM persona;
        id_ingresoINTPKauto
        id_personaINTFK → personaobligatorio
        puertaVARCHAR(40)obligatorio
        horaVARCHAR(5)obligatorio
    id_ingreso	id_persona	puerta	hora
    1	8	Entrada de artistas	19:00
    2	6	Entrada de artistas	19:05
    3	6	Cabina de sonido	19:10
    4	3	Entrada de artistas	19:20
    5	4	Entrada de artistas	19:25
    6	1	Entrada de artistas	19:30

    … y 30 fila(s) más. Míralas con SELECT * FROM ingreso;
        id_mensajeINTPKauto
        id_emisorINTFK → personaobligatorio
        id_receptorINTFK → personaobligatorio
        horaVARCHAR(5)obligatorio
        textoVARCHAR(120)obligatorio
    id_mensaje	id_emisor	id_receptor	hora	texto
    1	4	1	19:45	Después del show firmamos la renovación, ya está todo listo.
    2	1	4	19:50	No voy a firmar nada, Camilo. Ya lo decidí.
    3	3	4	19:55	Daniel no puede irse ahora, la gira se hunde sin él.
    4	6	1	21:50	Te dejé la botella de agua de siempre en el camerino.
    5	1	6	21:52	Gracias, Bruno. Como siempre.
    6	3	6	22:20	¿Ya dejaste la botella en el camerino? Necesito hablar con Daniel a solas.

    … y 16 fila(s) más. Míralas con SELECT * FROM mensaje;
        id_compraINTPKauto
        id_personaINTobligatorio
        productoVARCHAR(30)obligatorio
        cantidadINTobligatorio
        totalDECIMAL(10,2)obligatorio
        horaVARCHAR(5)obligatorio
    id_compra	id_persona	producto	cantidad	total	hora
    1	8	Café	1	4500	19:02
    2	6	Gaseosa	1	5000	19:12
    3	5	Agua	1	3000	19:38
    4	4	Café	1	4500	20:12
    5	7	Sándwich	1	12000	20:16
    6	7	Café	2	9000	20:17

    … y 12 fila(s) más. Míralas con SELECT * FROM compra;
        codigo_showVARCHAR(8)obligatorio
        ciudadVARCHAR(40)obligatorio
        fechaDATEobligatorio
        asistentesINTobligatorio
        recaudoDECIMAL(14,2)obligatorio
    codigo_show	ciudad	fecha	asistentes	recaudo
    NOC-01	Bogotá	2026-06-05	12000	960000000
    NOC-02	Bogotá	2026-06-05	8500	680000000
    NOC-03	Medellín	2026-06-12	11000	880000000
    NOC-04	Cali	2026-06-19	9000	720000000
    NOC-05	Barranquilla	2026-06-26	7800	624000000
    NOC-06	Bucaramanga	2026-07-03	6500	520000000

    … y 6 fila(s) más. Míralas con SELECT * FROM presentacion;
