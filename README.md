# Tarea 4 - Big Data (UNAD, curso 202016911): tienda en línea sobre MongoDB

Caso de uso: **MercadoVerde**, una tienda en línea (e-commerce) con una base de datos documental en MongoDB 7.0.
Base de datos `mercadoverde_tienda` con **seis colecciones** y **365 documentos** de prueba (sintéticos, con semilla fija).

| Colección   | Documentos | Contenido |
|-------------|-----------:|-----------|
| categorias  | 10  | clasificación del catálogo |
| productos   | 60  | catálogo con atributos variables por categoría (`atributos`) |
| usuarios    | 50  | clientes con direcciones embebidas |
| pedidos     | 120 | compras con las líneas (`articulos`) embebidas |
| resenas     | 100 | opiniones de clientes sobre productos |
| carritos    | 25  | carritos abiertos (aún sin pagar) |

## Archivos

- `cargar_datos.py`: crea la base, genera y carga los datos con `pymongo` y crea los índices base.
- `consultas_mongosh.js`: consultas comentadas para `mongosh` o la consola de MongoDB Compass:
  CRUD, filtros y operadores, agregaciones (`$group`, `$unwind`, `$bucket`, `$month`), uniones con `$lookup`,
  índices con `explain` y validación con `$jsonSchema`.

## Cómo ejecutarlo

1. Tener MongoDB en `mongodb://127.0.0.1:27017` (o pasar otra URI como argumento).
2. Instalar el controlador: `pip install pymongo`
3. Cargar los datos: `python cargar_datos.py`
4. Abrir la consola de Compass o `mongosh` y pegar los bloques de `consultas_mongosh.js` (cada bloque es independiente;
   la sección de `explain` se ejecuta sentencia por sentencia).

> Los datos son de prueba generados para practicar las consultas; no representan ventas reales.
