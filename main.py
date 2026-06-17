"""Content Command Center — FastAPI Backend
Puerto 8097 — Gestiona copies, frases, estrategia de contenido para @henryzarak
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from datetime import date, datetime
import json
import os
from pathlib import Path

app = FastAPI(title="Content Command Center")

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ── Models ─────────────────────────────────────────
class Copy(BaseModel):
    id: str
    date: str
    week_day: str
    texto_pantalla: str
    caption: str
    hashtags: list[str]
    tipo: str  # "viral" | "puente" | "tech"
    status: str = "draft"  # draft | approved | published
    hook_visual: str = ""
    audio_sugerido: str = ""

class Frase(BaseModel):
    id: str
    texto: str
    categoria: str  # "motivacional" | "antisocial" | "resiliencia" | "tech"
    veces_usada: int = 0
    rendimiento: str = ""  # "viral" | "medio" | "bajo" | ""

class Estrategia(BaseModel):
    month: str
    meta_seguidores: int
    meta_vistas: int
    pilares: dict  # {"viral": 60, "puente": 30, "tech": 10}
    frecuencia_diaria: int = 1
    horario: str = "10:00-12:00"

# ── Persistence helpers ────────────────────────────
def load_json(filename: str, default=None):
    path = DATA_DIR / filename
    if path.exists():
        return json.loads(path.read_text())
    return default if default is not None else []

def save_json(filename: str, data):
    (DATA_DIR / filename).write_text(json.dumps(data, indent=2, ensure_ascii=False))

# ── Seed data ──────────────────────────────────────
def seed_data():
    if not (DATA_DIR / "copies.json").exists():
        save_json("copies.json", [
            {
                "id": "2026-06-12",
                "date": "2026-06-12",
                "week_day": "Jueves",
                "texto_pantalla": "La gente cree que estoy todo el día en el teléfono.\nNo saben que un agente de IA publica por mí\nmientras yo construyo 8 negocios.",
                "caption": "Automatizar no es flojera. Es inteligencia. 🧠\n\nMientras duermo, trabajo, o entreno — mis agentes publican, monitorean, ejecutan.\n\nEl futuro no es trabajar más. Es delegar mejor.\n\n¿Ya automatizaste algo hoy?",
                "hashtags": ["ia", "automatización", "agentesia", "networking"],
                "tipo": "puente",
                "status": "draft",
                "hook_visual": "Cara seria → corte rápido a dashboard/setup",
                "audio_sugerido": "Beat oscuro tendencia"
            },
            {
                "id": "2026-06-13",
                "date": "2026-06-13",
                "week_day": "Viernes",
                "texto_pantalla": "No es que sea antisocial.\nEs que aprendí a estar solo\ny me gustó demasiado.",
                "caption": "Hay paz en la soledad que la gente no entiende.\n\nNo es tristeza. No es depresión. Es tranquilidad.\n\nY cuando aprendes a disfrutarla, dejas de buscar validación afuera.",
                "hashtags": ["soledad", "crecimientopersonal", "mentalidad"],
                "tipo": "viral",
                "status": "draft",
                "hook_visual": "Tú caminando solo, plano serio",
                "audio_sugerido": "Trending sad/reflective"
            },
            {
                "id": "2026-06-14",
                "date": "2026-06-14",
                "week_day": "Sábado",
                "texto_pantalla": "Mi yo de hace un año no reconocería\n al que soy hoy.\nY mi yo de mañana ya está siendo\nprogramado por un agente esta noche.",
                "caption": "El glow up más pesado no se ve. Se siente.\n\nHace un año no tenía agentes. No tenía sistemas. No tenía dashboards.\n\nHoy miro mi Home Lab y no puedo creer lo que construí.\n\nY apenas voy empezando.",
                "hashtags": ["glowup", "ia", "automatización", "buildinpublic"],
                "tipo": "puente",
                "status": "draft",
                "hook_visual": "Split screen: tú antes vs ahora + dashboards",
                "audio_sugerido": "Beat de superación/motivación"
            },
            {
                "id": "2026-06-15",
                "date": "2026-06-15",
                "week_day": "Domingo",
                "texto_pantalla": "Todos publican frases motivacionales.\nYo las programé para que un agente\nlas publique por mí.",
                "caption": "Mientras lees esto, un agente de IA ya publicó por mí hoy.\n\nAsí tengo tiempo para construir 8 negocios, entrenar, y vivir.\n\nLa automatización no es el futuro. Es el presente.\n\nLink en bio si quieres aprender cómo.",
                "hashtags": ["ia", "agentes", "automatizacion", "productividad"],
                "tipo": "tech",
                "status": "draft",
                "hook_visual": "Dashboard de agente publicando + tú haciendo otra cosa",
                "audio_sugerido": "Tech/futuristic beat"
            }
        ])

    if not (DATA_DIR / "frases.json").exists():
        save_json("frases.json", [
            {"id": "f1", "texto": "Qué tan insoportable tengo que ser para que cuando esté callado me pregunten si me pasa algo", "categoria": "antisocial", "veces_usada": 1, "rendimiento": "viral"},
            {"id": "f2", "texto": "Me encantan cuando me dicen... ¿no puedes? Bro, acabas de decir las palabras mágicas", "categoria": "resiliencia", "veces_usada": 1, "rendimiento": "viral"},
            {"id": "f3", "texto": "Solo tengo 4 versiones: Hablo mucho, No hablo, Hablo solo, Me trabo al hablar", "categoria": "antisocial", "veces_usada": 1, "rendimiento": "viral"},
            {"id": "f4", "texto": "No existe una sola versión de mi en la que no vea un futuro exitoso y extraordinario frente a mí. Ni una.", "categoria": "motivacional", "veces_usada": 1, "rendimiento": "viral"},
            {"id": "f5", "texto": "Soy una mezcla rara de alguien que sobrepiensa todo y alguien que le vale vrga todo", "categoria": "antisocial", "veces_usada": 1, "rendimiento": "viral"},
            {"id": "f6", "texto": "Nunca estuve listo para nada, simplemente soy una maldita máquina de resiliencia y aún con miedo siempre lo hice", "categoria": "resiliencia", "veces_usada": 1, "rendimiento": "alto"},
            {"id": "f7", "texto": "No olvides que la brújula fue inventada antes que el reloj mecánico, porque es más importante saber hacia donde vas, que cuanto tardas en llegar", "categoria": "motivacional", "veces_usada": 1, "rendimiento": "medio"},
            {"id": "f8", "texto": "Es de kbrones aceptar que primero debes organizar tu vida, cuidar tu mente, mejorar tu físico, ser más inteligente en la vida y lograr tus metas profesionales y personales para así merecer", "categoria": "motivacional", "veces_usada": 1, "rendimiento": "alto"},
            {"id": "f9", "texto": "La gente cree que estoy todo el día en el teléfono. No saben que un agente de IA publica por mí mientras yo construyo 8 negocios.", "categoria": "tech", "veces_usada": 0, "rendimiento": ""},
            {"id": "f10", "texto": "Mi yo de mañana ya está siendo programado por un agente esta noche.", "categoria": "tech", "veces_usada": 0, "rendimiento": ""},
            {"id": "f11", "texto": "Todos publican frases motivacionales. Yo las programé para que un agente las publique por mí.", "categoria": "tech", "veces_usada": 0, "rendimiento": ""},
            {"id": "f12", "texto": "El futuro no es trabajar más. Es delegar mejor.", "categoria": "tech", "veces_usada": 0, "rendimiento": ""}
        ])

    if not (DATA_DIR / "estrategia.json").exists():
        save_json("estrategia.json", {
            "month": "Junio 2026",
            "meta_seguidores": 7200,
            "meta_vistas": 1500000,
            "pilares": {"viral": 60, "puente": 30, "tech": 10},
            "frecuencia_diaria": 1,
            "horario": "10:00-12:00",
            "metricas_actuales": {
                "seguidores": 6700,
                "vistas_30d": 1209663,
                "vistas_90d": 10475978,
                "crecimiento_90d_pct": 81246,
                "nuevos_segs_30d": 519,
                "alcance_no_segs_pct": 93.5
            }
        })

seed_data()

# ── API Endpoints ──────────────────────────────────
@app.get("/api/copies")
def get_copies():
    return load_json("copies.json")

@app.get("/api/copies/{copy_id}")
def get_copy(copy_id: str):
    copies = load_json("copies.json")
    for c in copies:
        if c["id"] == copy_id:
            return c
    raise HTTPException(404, "Copy not found")

@app.post("/api/copies")
def save_copy(copy: Copy):
    copies = load_json("copies.json")
    existing = [c for c in copies if c["id"] == copy.id]
    if existing:
        copies = [c if c["id"] != copy.id else copy.model_dump() for c in copies]
    else:
        copies.append(copy.model_dump())
    save_json("copies.json", copies)
    return {"status": "ok"}

@app.put("/api/copies/{copy_id}/status")
def update_status(copy_id: str, status: str = Query(...)):
    copies = load_json("copies.json")
    for c in copies:
        if c["id"] == copy_id:
            c["status"] = status
            save_json("copies.json", copies)
            return {"status": "ok"}
    raise HTTPException(404)

@app.get("/api/frases")
def get_frases(categoria: str = None):
    frases = load_json("frases.json")
    if categoria:
        frases = [f for f in frases if f["categoria"] == categoria]
    return frases

@app.post("/api/frases")
def save_frase(frase: Frase):
    frases = load_json("frases.json")
    existing = [f for f in frases if f["id"] == frase.id]
    if existing:
        frases = [f if f["id"] != frase.id else frase.model_dump() for f in frases]
    else:
        frases.append(frase.model_dump())
    save_json("frases.json", frases)
    return {"status": "ok"}

@app.get("/api/estrategia")
def get_estrategia():
    return load_json("estrategia.json")

@app.put("/api/estrategia")
def update_estrategia(data: dict):
    current = load_json("estrategia.json")
    current.update(data)
    save_json("estrategia.json", current)
    return {"status": "ok"}

@app.get("/api/metrics")
def get_metrics():
    copies = load_json("copies.json")
    frases = load_json("frases.json")
    estrategia = load_json("estrategia.json")

    # Count by type for this week
    today = date.today()
    week_copies = [c for c in copies if c["date"] >= str(today)]
    viral = sum(1 for c in week_copies if c["tipo"] == "viral")
    puente = sum(1 for c in week_copies if c["tipo"] == "puente")
    tech = sum(1 for c in week_copies if c["tipo"] == "tech")
    total = len(week_copies)

    return {
        "copies_drafts": sum(1 for c in copies if c["status"] == "draft"),
        "copies_approved": sum(1 for c in copies if c["status"] == "approved"),
        "copies_published": sum(1 for c in copies if c["status"] == "published"),
        "frases_total": len(frases),
        "frases_virales": sum(1 for f in frases if f["rendimiento"] == "viral"),
        "estrategia": estrategia,
        "semana_actual": {
            "total": total,
            "viral": viral,
            "puente": puente,
            "tech": tech,
            "viral_pct": round(viral/total*100) if total else 0,
            "puente_pct": round(puente/total*100) if total else 0,
            "tech_pct": round(tech/total*100) if total else 0
        }
    }

# ── Static frontend ────────────────────────────────
@app.get("/")
def index():
    return FileResponse("templates/index.html")

# ── Vault file access ──────────────────────────────
VAULT_MARKETING = Path("/opt/agents/data/hzlabs/02_HOLDING/Henry_Zarak/04_Marketing.md")

@app.get("/api/vault/marketing")
def get_vault_marketing():
    if VAULT_MARKETING.exists():
        return {"content": VAULT_MARKETING.read_text(), "path": str(VAULT_MARKETING)}
    raise HTTPException(404, "Marketing file not found")

@app.put("/api/vault/marketing")
def update_vault_marketing(data: dict):
    content = data.get("content", "")
    VAULT_MARKETING.write_text(content)
    return {"status": "ok", "path": str(VAULT_MARKETING)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8099)
