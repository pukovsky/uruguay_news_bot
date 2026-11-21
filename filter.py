# Стоп-слова: если заголовок содержит любое из них — пропускаем
STOP_WORDS = [
    # Спорт
    "fútbol", "futbol", "gol", "partido", "selección", "peñarol", "nacional",
    "tenis", "básquetbol", "basquetbol", "rugby", "olímpic", "olimpic",
    "campeón", "campeonato", "torneo", "liga", "copa", "clásico", "clasico",
    "deportivo", "atleta", "mundial",
    # Светская хроника / развлечения
    "farándula", "farandula", "espectáculos", "espectaculos", "celebridad",
    "boda", "romance", "reality", "concierto", "música", "musica",
    "cine", "serie", "actor", "actriz", "cantante", "famoso",
    # Прочее (по желанию — можно закомментировать)
    "horóscopo", "horoscopo", "lotería", "loteria", "quiniela", "clima",
    "cómo usar", "cómo hacer", "cómo limpiar", "cómo barrer",
    "trucos", "consejos", "tips", "paso a paso",
    "bolsa en la escoba", "barrer mejor",
    "ee uu", "estados unidos",
    # Светская хроника / знаменитости / отношения
    "romance", "novio", "novia", "pareja", "boda", "casamiento",
    "separación", "divorcio", "infidelidad", "cuernos",
    "reveló", "confesó", "contó", "habló de", "opinó sobre",
    "polémica", "escándalo", "pelea", "enfrentamiento",
    "famoso", "famosa", "celebridad", "figura pública",
    "hincha", "fan", "se burló", "ironizó", "respondió a",
"cómo encontrar", "cómo saber", "cómo consultar", "dónde consultar",
"lote 21", "remate", "ganado", "precios del ganado",

]


STOP_WORDS += [
    # Лайфстайл / инструкции
    "pasos para", "cómo dejar", "cómo cuidar", "qué tener en cuenta",
    "trucos", "consejos", "tips", "impecable", "antiage",
    # Лотереи / азартные игры
    "lotería", "boleto ganador", "sorteo", "quiniela", "5 de oro",
    # Светская хроника / культура / реклама
    "corona", "se consagró", "premio", "galardón", "festival",
    "documental", "entretenido", "muestra", "exposición",
    # Локальные события
    "expo", "este sábado", "dique",
    # Здоровье/лайфстайл (если не нужно)
    "semillas", "chia", "fibra", "microbioma", "longevidad",
]

def is_relevant(title: str) -> bool:
    """Возвращает True, если заголовок стоит оставить."""
    if not title:
        return False
    title_lower = title.lower()
    return not any(word in title_lower for word in STOP_WORDS)