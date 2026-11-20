BLOCKED_CATEGORIES = {
    # Спорт
    "fútbol", "fútbol femenino", "básquetbol", "tenis", "rugby",
    "atletismo", "otros deportes",
    # Развлечения / светская хроника
    "teatro y carnaval", "tv y radio", "virales", "música",
    "videojuegos", "humor", "ficción", "fitness",
    # Служебное / не новости
    "efemérides", "en clave país", "servicios", "artículos para escuchar",
    "apuntes del día", "ediciones gigantes", "lento › ediciones",
    "lento › editorial", "le monde › contratapa", "le monde › culturas",
    "le monde › dossier", "le monde › editorial", "le monde › mundo",
    "le monde › región", "le monde › temas",
    # Мнения (если не нужны)
    "opiniones", "posturas", "ensayo", "perfil", "miradas",
    "fuera de agenda", "intercambios", "crónica", "reportaje",
    "fotografía", "fotorreportaje", "visualizaciones",
    # агроновости
    "valor agregado",
    "mente",
    "calidad de vida",
    "bienestar",
}

ALLOWED_CATEGORIES = {
    # Политика
    "política", "política nacional", "política internacional",
    "parlamento", "gobierno nacional", "sector público",
    # Экономика
    "mercados", "precios", "actividad económica", "empresas",
    "comercio y sector externo", "empleo y producción",
    # Общество
    "sociedad", "noticias", "locales", "nacional", "policiales",
    "derechos humanos", "desigualdad y pobreza", "violencias",
    "niñez y adolescencia", "políticas de género", "feminismos › desigualdades",
    "movimientos feministas", "lgbti+", "víctimas",
    # Здоровье / образование / наука
    "políticas de salud", "investigación en salud", "sistema educativo",
    "educación media", "educación primaria", "educación terciaria",
    "prácticas educativas", "ciencia", "ciencia y cultura",
    "conocimiento", "investigación científica", "comunidad científica",
    # Суды / безопасность
    "procesos judiciales", "sistema judicial", "cárceles",
    "fuerzas de seguridad", "crimen organizado",
    # Международка
    "internacionales", "américa", "asia", "españa", "gobernanza global",
    "trabajo › mundo",
    # Экология / вода (если интересно)
    "agua", "ambiente y producción", "crisis climática", "ecosistemas",
    "cuencas y acuíferos", "debates ambientales", "economía y ambiente",
    "educación y ambiente", "género y agua", "información y gestión del agua",
    "ley de riego", "pesca y playas", "calidad de vida",
    # Регионы (если нужны)
    "colonia › educación", "colonia › sociedad",
    "maldonado › ambiente", "maldonado › educación",
    "maldonado › justicia", "maldonado › sociedad",
    "paysandú › educación",
    "rivera › ambiente", "rivera › educación", "rivera › sociedad",
    "salto › cultura", "salto › educación", "salto › política",
    "salto › producción", "salto › sociedad",
}

def normalize(cat: str) -> str:
    """Приводит категорию к нижнему регистру и убирает лишние пробелы."""
    return " ".join(cat.strip().lower().split())

_BLOCKED = {normalize(c) for c in BLOCKED_CATEGORIES}
_ALLOWED = {normalize(c) for c in ALLOWED_CATEGORIES}

def category_decision(entry) -> str:
    """
    Возвращает:
      'block' — есть запрещённая категория
      'allow' — есть разрешённая категория
      'unknown' — категорий нет или они не в списках
    """
    tags = entry.get("tags", [])
    if not tags:
        return "unknown"

    cats = {normalize(t.get("term", "")) for t in tags if t.get("term")}

    if cats & _BLOCKED:
        return "block"
    if cats & _ALLOWED:
        return "allow"
    return "unknown"