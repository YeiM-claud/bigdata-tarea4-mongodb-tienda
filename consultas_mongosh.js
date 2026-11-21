/*
 * Tarea 4 - Big Data (UNAD, curso 202016911)
 * Consultas en MongoDB (mongosh o consola integrada de MongoDB Compass)
 * Caso de uso: tienda en línea "MercadoVerde" - base mercadoverde_tienda
 *
 * Antes de ejecutar este archivo hay que cargar los datos con cargar_datos.py.
 * Cada bloque se puede copiar y pegar por separado en la consola.
 * Desde mongosh también funciona:  load("consultas_mongosh.js")
 */

use("mercadoverde_tienda");

// =====================================================================
// 0. RECONOCIMIENTO: colecciones y cantidad de documentos de cada una
// =====================================================================
db.getCollectionNames().map(c => ({coleccion: c, documentos: db[c].countDocuments()}))

// =====================================================================
// 1. CONSULTAS BÁSICAS (CRUD)
// =====================================================================

// 1.1 Inserción de un documento (insertOne)
db.productos.insertOne({
  _id: "P061", sku: "MV-TEC-0061", nombre: "Cargador portátil 20000 mAh", marca: "Xiaomi",
  categoria_id: "tecnologia", precio: 135000, stock: 40,
  etiquetas: ["nuevo", "envío gratis"], atributos: {garantia_meses: 12, capacidad_mah: 20000}, activo: true
})

// 1.2 Inserción de varios documentos (insertMany)
db.productos.insertMany([
  {_id: "P062", sku: "MV-HOG-0062", nombre: "Tetera eléctrica", marca: "Oster", categoria_id: "hogar",
   precio: 89000, stock: 25, etiquetas: ["oferta"], atributos: {potencia_w: 1500, color: "negro"}, activo: true},
  {_id: "P063", sku: "MV-LIB-0063", nombre: "MongoDB: la guía definitiva", marca: "Alfaomega", categoria_id: "libros",
   precio: 98000, stock: 15, etiquetas: ["nuevo"], atributos: {paginas: 520, idioma: "español"}, activo: true}
])

// 1.3 Selección básica con proyección, orden y límite
db.productos.find({categoria_id: "tecnologia"}, {_id: 0, nombre: 1, marca: 1, precio: 1}).sort({precio: -1}).limit(4)

// 1.4 Actualización de un documento (updateOne con $set e $inc)
db.productos.updateOne({_id: "P061"}, {$set: {precio: 129000}, $inc: {stock: -5}})
// Se comprueba el cambio leyendo de nuevo el documento
db.productos.findOne({_id: "P061"}, {_id: 1, nombre: 1, precio: 1, stock: 1})

// 1.5 Actualización masiva (updateMany con $mul): 5 % de descuento en la categoría hogar
db.productos.updateMany({categoria_id: "hogar"}, {$mul: {precio: 0.95}})
db.productos.find({categoria_id: "hogar"}, {_id: 0, nombre: 1, precio: 1}).limit(3)

// 1.6 Eliminación (deleteOne y deleteMany): se borran los documentos de prueba insertados
db.productos.deleteOne({_id: "P061"})
db.productos.deleteMany({_id: {$in: ["P062", "P063"]}})
db.productos.countDocuments()   // vuelve a 60

// =====================================================================
// 2. FILTROS Y OPERADORES
// =====================================================================

// 2.1 Comparación y lógicos: $gte, $lte, $and, $or
db.productos.find(
  {$and: [{precio: {$gte: 500000, $lte: 2000000}}, {$or: [{stock: {$gt: 100}}, {etiquetas: "oferta"}]}]},
  {_id: 0, nombre: 1, precio: 1, stock: 1}).limit(5)

// 2.2 Pertenencia a un conjunto ($in) y expresión regular ($regex)
db.pedidos.find({estado: {$in: ["enviado", "pagado"]}, ciudad_envio: {$regex: /^B/}},
                {_id: 1, estado: 1, ciudad_envio: 1, total: 1}).limit(3)

// 2.3 Arreglos: $all exige que el arreglo contenga todos los valores indicados
db.productos.find({etiquetas: {$all: ["oferta", "nuevo"]}}, {_id: 0, nombre: 1, etiquetas: 1}).limit(2)

// 2.4 Contar y valores distintos
db.pedidos.countDocuments({estado: "cancelado"})
db.usuarios.distinct("direcciones.ciudad")

// =====================================================================
// 3. AGREGACIONES: contar, sumar, promediar ($group, $unwind, $project...)
// =====================================================================

// 3.1 Pedidos por estado: cantidad, ingreso total y ticket promedio
db.pedidos.aggregate([
  {$group: {_id: "$estado", pedidos: {$sum: 1}, ingresos: {$sum: "$total"}, ticket_promedio: {$avg: "$total"}}},
  {$project: {_id: 0, estado: "$_id", pedidos: 1, ingresos: 1, ticket_promedio: {$round: ["$ticket_promedio", 0]}}},
  {$sort: {pedidos: -1}}, {$limit: 3}
])

// 3.2 Los productos más vendidos ($unwind abre el arreglo de artículos)
db.pedidos.aggregate([
  {$match: {estado: {$ne: "cancelado"}}},
  {$unwind: "$articulos"},
  {$group: {_id: "$articulos.nombre", unidades: {$sum: "$articulos.cantidad"},
            ventas: {$sum: {$multiply: ["$articulos.cantidad", "$articulos.precio_unitario"]}}}},
  {$sort: {unidades: -1}}, {$limit: 3}
])

// 3.3 Ventas por mes (operador de fecha $month)
db.pedidos.aggregate([
  {$match: {estado: {$in: ["entregado", "enviado", "pagado"]}}},
  {$group: {_id: {$month: "$fecha"}, pedidos: {$sum: 1}, ventas: {$sum: "$total"}}},
  {$project: {_id: 0, mes: "$_id", pedidos: 1, ventas: 1}},
  {$sort: {mes: 1}}, {$limit: 3}
])

// 3.4 Agrupación por rangos con $bucket: pedidos según su valor
db.pedidos.aggregate([
  {$bucket: {groupBy: "$total", boundaries: [0, 200000, 500000, 1000000, 100000000], default: "otros",
             output: {pedidos: {$sum: 1}, promedio: {$avg: "$total"}}}},
  {$set: {promedio: {$round: ["$promedio", 0]}}}
])

// =====================================================================
// 4. UNIONES CON $lookup (equivalente a JOIN)
// =====================================================================

// 4.1 Pedido + datos del cliente (pedidos -> usuarios)
db.pedidos.aggregate([
  {$match: {_id: "PED-0001"}},
  {$lookup: {from: "usuarios", localField: "usuario_id", foreignField: "_id", as: "cliente"}},
  {$unwind: "$cliente"},
  {$project: {_id: 1, estado: 1, total: 1, cliente: {$concat: ["$cliente.nombre", " ", "$cliente.apellido"]},
              plan: "$cliente.plan"}}
])

// 4.2 Promedio de estrellas por categoría (reseñas -> productos -> categorías, dos uniones)
db.resenas.aggregate([
  {$lookup: {from: "productos", localField: "producto_id", foreignField: "_id", as: "p"}}, {$unwind: "$p"},
  {$lookup: {from: "categorias", localField: "p.categoria_id", foreignField: "_id", as: "c"}}, {$unwind: "$c"},
  {$group: {_id: "$c.nombre", resenas: {$sum: 1}, estrellas_prom: {$avg: "$estrellas"}}},
  {$project: {_id: 0, categoria: "$_id", resenas: 1, estrellas_prom: {$round: ["$estrellas_prom", 2]}}},
  {$sort: {estrellas_prom: -1}}, {$limit: 3}
])

// 4.3 Valor de los carritos abiertos: se unen los ítems con el precio actual del producto
db.carritos.aggregate([
  {$unwind: "$items"},
  {$lookup: {from: "productos", localField: "items.producto_id", foreignField: "_id", as: "prod"}}, {$unwind: "$prod"},
  {$group: {_id: "$_id", articulos: {$sum: "$items.cantidad"},
            valor: {$sum: {$multiply: ["$items.cantidad", "$prod.precio"]}}}},
  {$sort: {valor: -1}}, {$limit: 4}
])

// =====================================================================
// 5. ÍNDICES Y PLAN DE EJECUCIÓN (explain)
// =====================================================================
db.getCollectionNames().map(c => ({coleccion: c, indices: db[c].getIndexes().map(i => i.name)}))

// Consulta frecuente: pedidos de un cliente, con el índice idx_usuario_fecha y sin él (hint $natural).
// En la consola de Compass se ejecuta una sentencia por vez (las tres primeras líneas por separado).
var u = db.pedidos.findOne({}, {usuario_id: 1}).usuario_id
var a = db.pedidos.find({usuario_id: u}).explain("executionStats")
var b = db.pedidos.find({usuario_id: u}).hint({$natural: 1}).explain("executionStats")
({con_indice: {etapa: a.queryPlanner.winningPlan.inputStage.stage, indice: a.queryPlanner.winningPlan.inputStage.indexName,
               docs_examinados: a.executionStats.totalDocsExamined, devueltos: a.executionStats.nReturned},
  sin_indice: {etapa: b.queryPlanner.winningPlan.stage, docs_examinados: b.executionStats.totalDocsExamined,
               devueltos: b.executionStats.nReturned}})

// =====================================================================
// 6. VALIDACIÓN DE ESQUEMA ($jsonSchema)
// =====================================================================
db.runCommand({
  collMod: "productos",
  validator: {$jsonSchema: {
    bsonType: "object", required: ["sku", "nombre", "categoria_id", "precio", "stock"],
    properties: {
      sku: {bsonType: "string"},
      precio: {bsonType: ["int", "long", "double"], minimum: 0},
      stock: {bsonType: ["int", "long"], minimum: 0}
    }}},
  validationLevel: "moderate", validationAction: "error"
})
// Este documento viola el esquema (precio negativo, falta categoria_id y sku): debe ser rechazado
db.productos.insertOne({_id: "P999", nombre: "Producto inválido", precio: -10, stock: 3})
