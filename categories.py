from urllib.parse import urlparse

BLOCKED_SECTIONS = {
    "deporte", "humor", "cultura", "lento", "opinion",
    "le-monde-diplomatique", "gigantes", "cotidiana",
    "tvshow", "ovacion", "bienestar", "vida-actual",
    "el-empresario",
    "rioabierto",
}

def get_url_section(link: str) -> str:
    path = urlparse(link).path.strip("/")
    parts = path.split("/")
    return parts[0] if parts else ""

def url_decision(link: str) -> str:
    section = get_url_section(link)
    if section in BLOCKED_SECTIONS:
        return "block"
    return "unknown"


BLOCKED_CATEGORIES = {
    # ... существующие ...

    # El País — лайфстайл и хроника
    "hogar", "personajes", "vida sana", "el empresario",
    "gastronomía", "moda", "belleza", "automóviles",

    # Лотереи и азартные игры
    "lotería", "mega millions", "quiniela", "5 de oro",

    # Культура / развлечения (если не нужны)
    "cine", "tv", "streaming", "arte", "música", "infantiles",
    "literarias de deporte", "medios", "comer y beber",

    # Мнения и редакционные статьи
    "editorial", "opiniones", "posturas", "ensayo",
    "crónica", "reportaje", "perfil", "ficción",
    "fotorreportaje", "visualizaciones",

    # Le Monde (дайджест, а не новости)
    "le monde › contratapa", "le monde › culturas",
    "le monde › dossier", "le monde › editorial",
    "le monde › mundo", "le monde › región", "le monde › temas",

    # Lento (лонгриды)
    "lento › ediciones", "lento › editorial",

    # Служебное
    "efemérides", "servicios", "artículos para escuchar",
    "apuntes del día", "ediciones gigantes", "en clave país",
    "intercambios", "datos abiertos",
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
    # Международные отношения
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