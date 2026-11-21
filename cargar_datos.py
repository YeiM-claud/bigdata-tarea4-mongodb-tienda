"""Tarea 4 - Big Data (UNAD, curso 202016911) - Carga de datos de prueba en MongoDB.

Caso de uso: tienda en linea (e-commerce) "MercadoVerde".
Base de datos: mercadoverde_tienda, con EXACTAMENTE seis colecciones:

    categorias  (10 documentos)  -> clasificacion del catalogo
    productos   (60 documentos)  -> catalogo con atributos variables por categoria
    usuarios    (50 documentos)  -> clientes, con direcciones embebidas
    pedidos     (120 documentos) -> compras, con los articulos embebidos
    resenas     (100 documentos) -> opiniones de clientes sobre productos
    carritos    (25 documentos)  -> carritos de compra abiertos (aun sin pagar)

Total: 365 documentos. Los datos son sinteticos y reproducibles (semilla fija).

Requisitos:  pip install pymongo
Uso:         python cargar_datos.py [uri_mongodb]
             (por defecto mongodb://127.0.0.1:27017)
"""
import random
import sys
from datetime import datetime, timedelta

from pymongo import ASCENDING, DESCENDING, MongoClient

URI = sys.argv[1] if len(sys.argv) > 1 else "mongodb://127.0.0.1:27017"
NOMBRE_BD = "mercadoverde_tienda"

random.seed(161)                      # misma informacion en cada ejecucion
cliente = MongoClient(URI)
cliente.drop_database(NOMBRE_BD)      # parte siempre de cero
db = cliente[NOMBRE_BD]

# ------------------------------------------------------------ 1. categorias
# Se usa un _id legible (cadena corta) para poder referenciarlo desde productos.
CATEGORIAS = [
    ("tecnologia", "Tecnología", "Computadores, celulares y accesorios"),
    ("hogar", "Hogar y cocina", "Electrodomésticos y utensilios"),
    ("moda", "Moda", "Ropa, calzado y accesorios"),
    ("deportes", "Deportes", "Equipos y ropa deportiva"),
    ("libros", "Libros", "Literatura, técnicos y académicos"),
    ("belleza", "Belleza y cuidado personal", "Cosméticos y aseo"),
    ("juguetes", "Juguetes", "Juegos y entretenimiento infantil"),
    ("mascotas", "Mascotas", "Alimento y accesorios"),
    ("oficina", "Oficina y papelería", "Útiles y mobiliario"),
    ("jardin", "Jardín y ferretería", "Herramientas y plantas"),
]
db.categorias.insert_many([
    {"_id": cid, "nombre": nom, "descripcion": desc, "activa": True,
     "comision_pct": random.choice([5, 8, 10, 12])}
    for cid, nom, desc in CATEGORIAS
])

# ------------------------------------------------------------ 2. productos
# Cada categoria aporta nombres y atributos propios: es la ventaja del modelo
# documental (los documentos de una misma coleccion no tienen los mismos campos).
CATALOGO = {
    "tecnologia": (["Portátil 14 pulgadas", "Teléfono inteligente", "Audífonos inalámbricos", "Tablet 10 pulgadas",
                    "Teclado mecánico", "Monitor 24 pulgadas"], ["Samsung", "Lenovo", "Xiaomi", "Logitech"],
                   lambda: {"garantia_meses": random.choice([6, 12, 24]), "ram_gb": random.choice([4, 8, 16])}),
    "hogar": (["Licuadora", "Freidora de aire", "Juego de ollas", "Aspiradora", "Cafetera", "Plancha de vapor"],
              ["Oster", "Imusa", "Black+Decker", "Hamilton Beach"],
              lambda: {"potencia_w": random.choice([600, 900, 1200, 1500]), "color": random.choice(["negro", "blanco", "gris"])}),
    "moda": (["Camiseta de algodón", "Jean clásico", "Tenis urbanos", "Chaqueta impermeable", "Gorra deportiva",
              "Reloj análogo"], ["Arturo Calle", "Totto", "Adidas", "Americanino"],
             lambda: {"tallas": random.sample(["S", "M", "L", "XL"], k=random.randint(2, 4)),
                      "material": random.choice(["algodón", "poliéster", "cuero sintético"])}),
    "deportes": (["Balón de fútbol", "Bicicleta de montaña", "Pesas ajustables", "Colchoneta de yoga",
                  "Guantes de boxeo", "Tula deportiva"], ["Nike", "Puma", "GW", "Decathlon"],
                 lambda: {"deporte": random.choice(["fútbol", "ciclismo", "gimnasio", "yoga"]),
                          "peso_kg": round(random.uniform(0.3, 15), 1)}),
    "libros": (["Bases de datos NoSQL", "Cien años de soledad", "Python para ciencia de datos", "El principito",
                "Introducción a Big Data", "Cálculo diferencial"], ["Alfaomega", "Planeta", "UOC", "Ecoe Ediciones"],
               lambda: {"paginas": random.randint(120, 780), "idioma": random.choice(["español", "inglés"])}),
    "belleza": (["Crema hidratante", "Perfume 100 ml", "Shampoo reparador", "Protector solar", "Set de brochas",
                 "Jabón facial"], ["Nivea", "Natura", "L'Oréal", "Eucerin"],
                lambda: {"contenido_ml": random.choice([50, 100, 250, 400]), "vegano": random.choice([True, False])}),
    "juguetes": (["Bloques de construcción", "Muñeca articulada", "Carro a control remoto", "Rompecabezas 500 piezas",
                  "Juego de mesa", "Peluche gigante"], ["Lego", "Hasbro", "Mattel", "Ravensburger"],
                 lambda: {"edad_minima": random.choice([3, 5, 8, 12]), "requiere_pilas": random.choice([True, False])}),
    "mascotas": (["Alimento para perro 10 kg", "Arenero para gato", "Correa retráctil", "Cama acolchada",
                  "Snacks dentales", "Rascador"], ["Pro Plan", "Dog Chow", "Whiskas", "Kong"],
                 lambda: {"especie": random.choice(["perro", "gato"]), "peso_kg": round(random.uniform(0.5, 10), 1)}),
    "oficina": (["Silla ergonómica", "Escritorio plegable", "Resma de papel", "Calculadora científica",
                 "Lámpara de escritorio", "Archivador metálico"], ["Norma", "Faber-Castell", "Casio", "Officemax"],
                lambda: {"material": random.choice(["madera", "metal", "plástico"]), "garantia_meses": random.choice([3, 12])}),
    "jardin": (["Taladro inalámbrico", "Manguera 20 m", "Juego de herramientas", "Podadora eléctrica",
                "Matera decorativa", "Fertilizante orgánico"], ["Dewalt", "Truper", "Stanley", "Bosch"],
               lambda: {"voltaje": random.choice([12, 18, 110]), "uso": random.choice(["hogar", "profesional"])}),
}
# Rango de precios (en miles de pesos) por categoria, para que el catalogo sea realista
RANGO_PRECIO = {"tecnologia": (80, 3200), "hogar": (40, 650), "moda": (25, 420), "deportes": (30, 1800),
                "libros": (25, 160), "belleza": (15, 280), "juguetes": (20, 380), "mascotas": (15, 260),
                "oficina": (10, 700), "jardin": (20, 900)}
productos = []
n = 0
for cid, (nombres, marcas, extra) in CATALOGO.items():
    for nombre in nombres:                       # 10 categorias x 6 productos = 60
        n += 1
        productos.append({
            "_id": f"P{n:03d}", "sku": f"MV-{cid[:3].upper()}-{n:04d}", "nombre": nombre,
            "marca": random.choice(marcas), "categoria_id": cid,
            "precio": random.randrange(*RANGO_PRECIO[cid], 5) * 1000,     # pesos colombianos
            "stock": random.randint(0, 120),
            "etiquetas": random.sample(["oferta", "nuevo", "envío gratis", "más vendido", "ecológico", "importado"],
                                       k=random.randint(1, 3)),
            "atributos": extra(),                                       # campos distintos por categoria
            "activo": True,
        })
db.productos.insert_many(productos)

# ------------------------------------------------------------ 3. usuarios
NOMBRES = ["Camila", "Santiago", "Valentina", "Mateo", "Daniela", "Sebastián", "Laura", "Andrés", "Sofía", "Julián",
           "Paula", "Felipe", "Manuela", "David", "Isabella", "Nicolás", "Mariana", "Esteban", "Carolina", "Tomás"]
APELLIDOS = ["Gómez", "Rodríguez", "Martínez", "López", "Hernández", "Ramírez", "Castro", "Torres", "Vargas", "Moreno",
             "Jiménez", "Rojas", "Cárdenas", "Pardo", "Suárez"]
CIUDADES = [("Bogotá", "Cundinamarca"), ("Medellín", "Antioquia"), ("Cali", "Valle del Cauca"),
            ("Bucaramanga", "Santander"), ("Barranquilla", "Atlántico"), ("Cartagena", "Bolívar"),
            ("Pereira", "Risaralda"), ("Cúcuta", "Norte de Santander")]
usuarios = []
for i in range(1, 51):
    nom, ape = random.choice(NOMBRES), random.choice(APELLIDOS)
    dirs = []
    for k in range(random.randint(1, 2)):                       # direcciones embebidas (1 o 2)
        ciudad, depto = random.choice(CIUDADES)
        dirs.append({"alias": ["casa", "trabajo"][k], "ciudad": ciudad, "departamento": depto,
                     "direccion": f"Calle {random.randint(1, 120)} # {random.randint(1, 90)}-{random.randint(1, 99)}"})
    usuarios.append({
        "_id": f"U{i:03d}", "nombre": nom, "apellido": ape,
        "correo": f"{nom.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i')}.{i}@correo-ejemplo.co",
        "registro": datetime(2024, 1, 1) + timedelta(days=random.randint(0, 800)),
        "plan": random.choices(["básico", "premium"], [80, 20])[0],
        "direcciones": dirs, "activo": True,
    })
db.usuarios.insert_many(usuarios)

# ------------------------------------------------------------ 4. pedidos
ESTADOS = [("entregado", 55), ("enviado", 15), ("pagado", 12), ("pendiente", 10), ("cancelado", 8)]
METODOS = ["tarjeta", "PSE", "contraentrega", "billetera digital"]
pedidos = []
for i in range(1, 121):
    u = random.choice(usuarios)
    lineas = []
    for p in random.sample(productos, k=random.randint(1, 4)):
        cant = random.randint(1, 3)
        lineas.append({"producto_id": p["_id"], "nombre": p["nombre"], "cantidad": cant,
                       "precio_unitario": p["precio"]})            # se copia el precio del momento
    subtotal = sum(l["cantidad"] * l["precio_unitario"] for l in lineas)
    envio = 0 if subtotal >= 150000 else 12000
    estado = random.choices([e for e, _ in ESTADOS], [w for _, w in ESTADOS])[0]
    pedidos.append({
        "_id": f"PED-{i:04d}", "usuario_id": u["_id"],
        "fecha": datetime(2026, 1, 1) + timedelta(days=random.randint(0, 300), hours=random.randint(0, 23),
                                                  minutes=random.randint(0, 59)),
        "estado": estado, "metodo_pago": random.choice(METODOS),
        "ciudad_envio": u["direcciones"][0]["ciudad"],
        "articulos": lineas, "subtotal": subtotal, "envio": envio, "total": subtotal + envio,
    })
db.pedidos.insert_many(pedidos)

# ------------------------------------------------------------ 5. resenas
COMENTARIOS = {5: ["Excelente calidad, lo recomiendo", "Llegó rápido y funciona perfecto", "Superó mis expectativas"],
               4: ["Muy bueno por el precio", "Cumple lo prometido", "Buen producto, empaque mejorable"],
               3: ["Normal, nada especial", "Cumple pero esperaba más"],
               2: ["La calidad no es la esperada", "Tardó en llegar y vino con detalles"],
               1: ["No lo recomiendo", "Llegó dañado"]}
resenas = []
for i in range(1, 101):
    p, u = random.choice(productos), random.choice(usuarios)
    est = random.choices([5, 4, 3, 2, 1], [35, 33, 17, 10, 5])[0]
    resenas.append({
        "_id": f"R{i:04d}", "producto_id": p["_id"], "usuario_id": u["_id"], "estrellas": est,
        "comentario": random.choice(COMENTARIOS[est]),
        "fecha": datetime(2026, 2, 1) + timedelta(days=random.randint(0, 280)),
        "compra_verificada": random.random() < 0.8, "votos_utiles": random.randint(0, 40),
    })
db.resenas.insert_many(resenas)

# ------------------------------------------------------------ 6. carritos
carritos = []
for i, u in enumerate(random.sample(usuarios, 25), start=1):
    items = [{"producto_id": p["_id"], "cantidad": random.randint(1, 2)}
             for p in random.sample(productos, k=random.randint(1, 4))]
    carritos.append({"_id": f"CAR-{i:03d}", "usuario_id": u["_id"], "items": items,
                     "actualizado": datetime(2026, 10, 1) + timedelta(days=random.randint(0, 45)),
                     "cupon": random.choice([None, "BIENVENIDA10", "NOVIEMBRE15"])})
db.carritos.insert_many(carritos)

# ------------------------------------------------------------ indices base
db.productos.create_index([("categoria_id", ASCENDING), ("precio", DESCENDING)], name="idx_categoria_precio")
db.pedidos.create_index([("usuario_id", ASCENDING), ("fecha", DESCENDING)], name="idx_usuario_fecha")
db.resenas.create_index([("producto_id", ASCENDING)], name="idx_resena_producto")
db.usuarios.create_index([("correo", ASCENDING)], unique=True, name="idx_correo_unico")

print(f"Base '{NOMBRE_BD}' creada:")
for c in db.list_collection_names():
    print(f"  {c:<11} {db[c].count_documents({}):>4} documentos")
