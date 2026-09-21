USE caso_concierto;

1. El expediente

Cinco tablas: persona, ingreso, mensaje, compra y presentacion. La noche entera está ahí, fila por fila.

2. La giraen curso

SELECT * FROM mensaje,persona,ingreso,mensaje,compra,presentacion

La gira

Ocho personas tenían tarjeta de acceso esa noche: los tres músicos, la productora, el representante, el técnico de sonido, una periodista y el jefe de seguridad.


Resultado

✓ línea 1 · SELECT * FROM persona
id_persona	nombre	apellido	rol	contacto
1	Daniel	Arango Cortés	Vocalista	daniel.arango@nocturnos.co | 3105550101
2	Julián	Mesa Toro	Guitarrista	julian.mesa@nocturnos.co | 3125550202
3	Sofía	Restrepo Ángel	Productora	sofia@restrepoproducciones.com | 3005554471
4	Camilo	Ríos Puerta	Representante	camilo.rios@nocturnos.co | 3155550404
5	Renata	Gil Ospina	Corista	renata.gil@nocturnos.co | 3185550505
6	Bruno	Salazar Peña	Técnico de sonido	bruno.salazar@sonidovivo.co | 3115550606
7	Elena	Cortés Marín	Periodista	elena.cortes@elritmo.co | 3135550707
8	Gabriel	Torres Nieto	Jefe de seguridad	gabriel.torres@estadio.co | 3165550808

8 filas


Hallazgo

La víctima es Daniel Arango Cortés, id 1. Fíjate en la columna contacto: correo y teléfono metidos en la misma celda. Eso va a estorbar más adelante.

Pista 3 de 21
Doce conciertos sin identificar

La productora entregó la tabla presentacion con los doce conciertos de la gira, pero sin llave primaria. Hay dos funciones el mismo día en la misma ciudad y dos con el mismo número de asistentes: el detective necesita poder señalar un concierto sin confundirlo con otro.

Tu tarea

Mira las columnas de presentacion, decide cuál identifica cada concierto sin repetirse nunca, y declárala como llave primaria.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta

ALTER TABLE presentacion ADD PRIMARY KEY(codigo_show);

Pista 4 de 21
Compras de un fantasma

La cafetería del estadio exportó sus ventas en la tabla compra, pero sin llave foránea: id_persona es un número suelto que podría apuntar a alguien que no existe. Para usar esas compras como prueba, cada una tiene que señalar a una persona real.

Tu tarea

Declara en la tabla compra la llave foránea que conecta su columna id_persona con la tabla persona.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.



ALTER TABLE compra ADD FOREIGN KEY(id_persona) REFERENCES persona(id_persona);

Hallazgo

Ahora ninguna compra puede quedar huérfana: las dieciocho apuntan a alguien de la lista. Ya se puede seguir el rastro de lo que compró cada uno.

Pista 5 de 21
Correo y teléfono

El celular de Daniel registró una llamada perdida a las 22:40, pero solo tenemos el número. Para cruzarlo con la tabla persona hace falta una columna de teléfono, y ahí el teléfono va pegado al correo dentro de contacto, separados por una barra: no es atómico.

Tu tarea

Agrega a persona las columnas correo y telefono, y llénalas para las ocho personas: a la izquierda de la barra ' | ' va el correo y a la derecha el teléfono.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.





ALTER TABLE persona ADD correo VARCHAR(50), ADD telefono VARCHAR(50);
UPDATE persona SET correo="daniel.arango@nocturnos.co", telefono="3105550101" WHERE id_persona="1";
UPDATE persona SET correo="julian.mesa@nocturnos.co", telefono="3125550202" WHERE id_persona="2";
UPDATE persona SET correo="sofia@restrepoproducciones.com", telefono="3005554471" WHERE id_persona="3";
UPDATE persona SET correo="camilo.rios@nocturnos.co", telefono="3155550404" WHERE id_persona="4";
UPDATE persona SET correo="renata.gil@nocturnos.co", telefono="3185550505" WHERE id_persona="5";
UPDATE persona SET correo="bruno.salazar@sonidovivo.co", telefono="3115550606" WHERE id_persona="6";
UPDATE persona SET correo="elena.cortes@elritmo.co", telefono="3135550707" WHERE id_persona="7";
UPDATE persona SET correo="gabriel.torres@estadio.co", telefono="3165550808" WHERE id_persona="8";





Pista 5 de 21
Correo y teléfono

El celular de Daniel registró una llamada perdida a las 22:40, pero solo tenemos el número. Para cruzarlo con la tabla persona hace falta una columna de teléfono, y ahí el teléfono va pegado al correo dentro de contacto, separados por una barra: no es atómico.

Tu tarea

Agrega a persona las columnas correo y telefono, y llénalas para las ocho personas: a la izquierda de la barra ' | ' va el correo y a la derecha el teléfono.


Quién entró al camerino

El forense sitúa la muerte entre las 22:35 y las 23:00. Daniel pasó su tarjeta en el camerino a las 22:34. El camerino tiene una sola puerta y cada pasada de tarjeta quedó en la tabla ingreso.

Tu tarea

Muestra el id de la persona y la hora de cada pasada por la puerta 'Camerino' entre las '22:35' y las '23:00'.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.






SELECT id_persona, hora FROM ingreso WHERE puerta="Camerino" AND hora BETWEEN '22:35' AND '23:00';

Pista 7 de 21
La botella

El veneno estaba en la botella de agua. Daniel solo tomaba de la que el técnico de sonido le dejaba en el camerino antes de cada show. Alguien tuvo que saber eso. El chat de la gira está en la tabla mensaje.

Tu tarea

Muestra id_emisor, id_receptor y texto de los mensajes en cuyo texto aparezca la palabra botella.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.

SELECT id_emisor,id_receptor, texto FROM mensaje WHERE texto like '%botella%';

Pista 8 de 21
Lo que le escribieron a Daniel

Tres personas entraron al camerino en la hora de la muerte: la 2, la 3 y la 5. El detective quiere leer exactamente lo que cada una le escribió a Daniel esa noche.

Tu tarea

Muestra id_emisor, hora y texto de los mensajes enviados por las personas 2, 3 o 5 cuyo receptor sea la persona 1.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.

SELECT id_emisor, hora, texto FROM mensajes WHERE id_receptor = 1 AND id_emisor IN (2, 3, 5);



Resultado

✓ línea 1 · SELECT id_emisor,id_receptor, texto FROM mensaje WHERE texto like '%bo…
id_emisor	id_receptor	texto
6	1	Te dejé la botella de agua de siempre en el camerino.
3	6	¿Ya dejaste la botella en el camerino? Necesito hablar con Daniel a solas.
3	6	Borra el mensaje de la botella.


SELECT id_emisor, hora, texto FROM mensaje WHERE id_receptor = 1 AND id_emisor IN (2, 3, 5);

Resultado

✓ línea 1 · SELECT id_emisor, hora, texto FROM mensaje WHERE id_receptor = 1 AND i…
id_emisor	hora	texto
5	22:31	Estuviste increíble esta noche.
3	22:38	Sube a firmar antes de que te arrepientas. Voy al camerino.
2	22:45	Daniel, ¿estás en el camerino? Necesito la guitarra que dejaste.





SELECT nombre, apellido, rol
FROM personas
WHERE rol = 'Productora' 
   OR rol = 'Representante';

SELECT nombre, apellido, rol FROM persona WHERE rol = 'Productora' OR rol = 'Representante';


Pista 10 de 21
Cafetería y camerino

La botella del camerino era de la cafetería. Quien la cambió tuvo que pasar por la cafetería y después por el camerino, ya entrada la noche. Ojo: una condición es «esto o aquello» y la otra es obligatoria; piensa en qué orden se evalúan.

Tu tarea

Muestra id_persona, puerta y hora de las pasadas por la puerta 'Camerino' o por la puerta 'Cafetería' ocurridas a partir de las '22:00' (incluida).

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.


SELECT id_persona, puerta, hora FROM ingreso WHERE (puerta = 'Camerino' OR puerta = 'Cafetería') AND hora >= '22:00';


Resultado

✓ línea 1 · SELECT id_persona, puerta, hora FROM ingreso WHERE (puerta = 'Camerino…
id_persona	puerta	hora
3	Cafetería	22:05
1	Camerino	22:34
2	Cafetería	22:36
3	Camerino	22:41
5	Camerino	22:47
2	Camerino	22:52
4	Cafetería	22:56
8	Camerino	23:05
6	Camerino	23:08
4	Camerino	23:10


SELECT nombre, apellido FROM persona WHERE telefono LIKE '%4471'; 




SELECT ciudad, fecha, recaudo FROM presentacion ORDER BY recaudo DESC;


Hallazgo

Los primeros conciertos recaudaron casi mil millones; los últimos, poco más de trescientos. La gira se venía abajo, y la productora había asegurado la vida del vocalista por dos mil millones.

Pista 13 de 21
Los dos conciertos más vacíos

Para el informe, el detective no quiere los doce conciertos: solo los dos con menos público, que son los que hundieron la gira.

Tu tarea

Muestra ciudad, fecha y asistentes de los dos conciertos con menos asistentes, del más vacío al menos vacío.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.


SELECT ciudad, fecha, asistentes
FROM presentacion
ORDER BY asistentes ASC
LIMIT 2;


Quién compró agua

La botella del camerino no era la de Bruno: era una de la cafetería, de la misma marca. Alguien compró agua esa noche para cambiarla. Las ventas están en la tabla compra.

Tu tarea

Cuenta cuántas compras del producto 'Agua' hizo cada persona: muestra id_persona y el total de compras de esa persona.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.

SELECT id_persona, COUNT(*) AS total
FROM compra
WHERE producto = 'Agua'
GROUP BY id_persona;


Pista 15 de 21
Cuánto gastó cada uno

El detective quiere ver el gasto completo de la noche por persona, no solo el agua. La columna total ya trae el valor de cada compra; falta sumarlo por persona.

Tu tarea

Muestra id_persona y la suma de total de todas las compras de esa persona.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.


SELECT id_persona, SUM(total) AS gasto_total
FROM compra
GROUP BY id_persona;

SELECT id_persona, SUM(total) AS total
FROM compra
GROUP BY id_persona;


Pista 16 de 21
Quién escribió más

Veintidós mensajes en una noche. El detective quiere saber quién no soltó el celular, pero solo le interesa quien pasó de tres mensajes. Ojo: el total de mensajes no existe hasta que se agrupa, así que el filtro de siempre no lo ve.

Tu tarea

Muestra id_emisor y el total de mensajes únicamente de las personas que enviaron más de 3 mensajes.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.


SELECT id_emisor, COUNT(*) AS total_mensajes
FROM mensaje
GROUP BY id_emisor
HAVING COUNT(*) > 3;


Pista 17 de 21
El total de la gira

Falta un número para cerrar el motivo. Si la gira recaudó menos de lo que costó, la póliza de dos mil millones era la única salida de la productora.

Tu tarea

Muestra la suma del recaudo de todas las presentaciones y el número de asistentes más bajo que tuvo un concierto.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.


Resultado

✓ línea 1 · SELECT id_emisor, COUNT(*) AS total_mensajes
id_emisor	total_mensajes
3	5

1 grupo


SELECT SUM(recaudo) AS recaudo_total, MIN(asistentes) AS asistencia_minima
FROM presentacion;


Resultado

✓ línea 1 · SELECT SUM(recaudo) AS recaudo_total, MIN(asistentes) AS asistencia_mi…
recaudo_total	asistencia_minima
6775000000	3900



El camerino, con nombres

«Deje de hablarme de números», dice el detective. Quiere la lista completa de pasadas por el camerino, pero con el nombre y el apellido de cada persona junto a la hora. El nombre no está en la tabla ingreso.

Tu tarea

Muestra nombre, apellido y hora de cada pasada por la puerta 'Camerino', en orden de hora.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.



SELECT p.nombre, p.apellido, i.hora
FROM ingreso i
JOIN persona p ON i.id_persona = p.id_persona
WHERE i.puerta = 'Camerino'
ORDER BY i.hora;



Resultado

✓ línea 1 · SELECT p.nombre, p.apellido, i.hora
p.nombre	p.apellido	i.hora
Daniel	Arango Cortés	19:40
Sofía	Restrepo Ángel	20:00
Camilo	Ríos Puerta	21:15
Bruno	Salazar Peña	21:50
Daniel	Arango Cortés	22:34
Sofía	Restrepo Ángel	22:41
Renata	Gil Ospina	22:47
Julián	Mesa Toro	22:52
Gabriel	Torres Nieto	23:05
Bruno	Salazar Peña	23:08
Camilo	Ríos Puerta	23:10

11 filas

Pista 19 de 21
Cuántas ciudades

Doce conciertos no son doce ciudades: Bogotá tuvo tres y Medellín y Cali dos cada una. Para el informe hace falta cuántas ciudades diferentes recorrió la gira, sin contar dos veces ninguna.

Tu tarea

Cuenta cuántas ciudades distintas aparecen en la tabla presentacion.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.


SELECT COUNT(DISTINCT ciudad) AS ciudades_distintas
FROM presentacion;

Resultado

✓ línea 1 · SELECT COUNT(DISTINCT ciudad) AS ciudades_distintas
ciudades_distintas
8

1 fila


Pista 20 de 21
Lo que recibió Daniel, con nombre

Última lectura antes de acusar. El detective quiere todos los mensajes que recibió Daniel esa noche, pero con el nombre de quien los envió, no con su número.

Tu tarea

Muestra el nombre del emisor, la hora y el texto de los mensajes cuyo receptor sea la persona 1.

¿Qué palabras reservadas de SQL necesitas para esto? Decídelo antes de escribir: cada ejecución que no resuelve la pista cuenta.

SELECT p.nombre, m.hora, m.texto
FROM mensajes m
JOIN personas p ON m.id_emisor = p.id_persona
WHERE m.id_receptor = 1;


SELECT p.nombre, m.hora, m.texto
FROM mensaje m
JOIN persona p ON m.id_emisor = p.id_persona
WHERE m.id_receptor = 1;



Resultado

✓ línea 1 · SELECT p.nombre, m.hora, m.texto
p.nombre	m.hora	m.texto
Camilo	19:45	Después del show firmamos la renovación, ya está todo listo.
Bruno	21:50	Te dejé la botella de agua de siempre en el camerino.
Elena	22:00	Prima, ¿la entrevista de mañana sigue en pie?
Renata	22:31	Estuviste increíble esta noche.
Sofía	22:38	Sube a firmar antes de que te arrepientas. Voy al camerino.
Julián	22:45	Daniel, ¿estás en el camerino? Necesito la guitarra que dejaste.
