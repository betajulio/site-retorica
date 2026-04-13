import requests
import re
from firebase_functions import firestore_fn, scheduler_fn
from firebase_admin import initialize_app, firestore
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Inicializa o Admin
initialize_app()

# --- CONFIGURAÇÕES ---
ID_INSTANCE = "7107582324" 
API_TOKEN = ""     
CHAT_ID = "" 
SITE_URL = "https://betajulio.github.io/site-retorica/"
NEWS_URL = "https://betajulio.github.io/site-retorica/noticias.html"

LINKS_FOOTER = f"\n\n🌐 *Site:* {SITE_URL}\n🤘📰 *Notícias do Rock:* {NEWS_URL}"
SP_TZ = ZoneInfo("America/Sao_Paulo")

def now_sp():
    return datetime.now(SP_TZ)

def get_saturday_date(reference=None, include_today=False):
    ref = reference or now_sp()
    days_ahead = (5 - ref.weekday() + 7) % 7
    if days_ahead == 0 and not include_today:
        days_ahead = 7
    return (ref + timedelta(days=days_ahead)).date()

def extract_youtube_id(url):
    regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_next_saturday_str():
    return get_saturday_date(include_today=False).strftime("%d/%m")

def get_next_saturday_iso():
    return get_saturday_date(include_today=False).isoformat()

def get_current_saturday_str():
    return get_saturday_date(include_today=True).strftime("%d/%m")

def get_current_saturday_iso():
    return get_saturday_date(include_today=True).isoformat()

def is_rehearsal_cancelled(db, sat_iso):
    state_doc = db.collection("rehearsal_state").document("current").get()
    return state_doc.exists and state_doc.to_dict().get("cancelled_date") == sat_iso

def send_wa_message(text):
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    payload = {"chatId": CHAT_ID, "message": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except: pass

def send_wa_image(file_url, caption):
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
    payload = {"chatId": CHAT_ID, "urlFile": file_url, "fileName": "foto.jpg", "caption": caption}
    try:
        requests.post(url, json=payload, timeout=15)
    except: pass

# 1. GATILHO: NOVA ENQUETE
@firestore_fn.on_document_created(document="polls/{pollId}")
def on_poll_created(event: firestore_fn.Event[firestore_fn.DocumentSnapshot | None]) -> None:
    poll = event.data.to_dict()
    if poll:
        q = poll.get('question', 'Nova Enquete')
        d = poll.get('description', '')
        opts = poll.get('options', [])
        opts_txt = "\n" + "\n".join([f"🔹 {o.get('label')}" for o in opts]) if opts else ""
        desc_txt = f"\n📝 _{d}_" if d else ""
        send_wa_message(f"🗳️ *NOVA ENQUETE NO AR!*\n\n❓ *{q}*{desc_txt}\n{opts_txt}{LINKS_FOOTER}")

# 2. GATILHO: NOVAS FOTOS
@firestore_fn.on_document_created(document="gallery/{photoId}")
def on_photo_added(event: firestore_fn.Event[firestore_fn.DocumentSnapshot | None]) -> None:
    p = event.data.to_dict()
    if p:
        caption_db = p.get('caption', '')
        tag_db = p.get('tag', 'Bastidores')
        user_name = p.get('addedBy', 'Membro')
        desc_txt = f"📝 _{caption_db}_\n\n" if caption_db else ""
        msg = f"{desc_txt}📸 *Nova foto na galeria!* [#{tag_db}]\n👤 Enviado por: *{user_name}*{LINKS_FOOTER}"
        if p.get('url'):
            send_wa_image(p['url'], msg)
        else:
            send_wa_message(msg)

# 3. GATILHO: NOVA SUGESTÃO
@firestore_fn.on_document_created(document="suggestions/{suggestionId}")
def on_suggestion_created(event: firestore_fn.Event[firestore_fn.DocumentSnapshot | None]) -> None:
    s = event.data.to_dict()
    if s:
        song = s.get('song', 'Desconhecida')
        artist = s.get('artist', 'Desconhecido')
        user = s.get('by', 'Alguém')
        yt_link = s.get('youtube', '')
        yt_txt = f"\n🎥 *Vídeo:* {yt_link}" if yt_link else ""
        msg = f"🎸 *Nova Sugestão de Música!*\n\n🎵 *Música:* {song}\n👤 *Artista:* {artist}\n✍️ *Sugerido por:* {user}{yt_txt}{LINKS_FOOTER}"
        
        # Se tiver link do YouTube, tenta pegar o thumbnail
        if yt_link:
            yt_id = extract_youtube_id(yt_link)
            if yt_id:
                thumb_url = f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"
                send_wa_image(thumb_url, msg)
                return
        
        send_wa_message(msg)

# 4. GATILHO: LOGS (REMOÇÃO OU DISPARO MANUAL)
@firestore_fn.on_document_created(document="logs/{logId}")
def on_log_created(event: firestore_fn.Event[firestore_fn.DocumentSnapshot | None]) -> None:
    log = event.data.to_dict()
    if not log: return

    action = log.get('action')

    # A. Remoção de Sugestão
    if action == "Sugestão Removida":
        song = log.get('song', 'Música')
        artist = log.get('artist', 'Artista')
        suggested_by = log.get('by', 'Membro')
        likes = log.get('likes', 0)
        dislikes = log.get('dislikes', 0)
        reason = log.get('reason', 'Não informado')
        removed_by = log.get('removedBy', 'Sistema')
        
        msg = (
            f"🗑️ *SUGESTÃO REMOVIDA*\n\n"
            f"🎵 *Música:* {song} - {artist}\n"
            f"👤 *Sugerida por:* {suggested_by}\n"
            f"📊 *Votos:* 👍 {likes} | 👎 {dislikes}\n"
            f"📝 *Motivo:* {reason}\n"
            f"👤 *Removido por:* {removed_by}\n\n"
            f"✨ *Não desanime, {suggested_by}!* O rock é feito de persistência. Se sua música não entrou agora, "
            f"tente sugerir novamente em um momento mais oportuno. Continuem participando!"
            f"{LINKS_FOOTER}"
        )
        send_wa_message(msg)

    # B. Disparo Manual da Lista de Ensaio
    elif action == "Disparar Zap Ensaio":
        db = firestore.client()
        doc = db.collection("setlists").document("data").get()
        if doc.exists:
            tab0 = doc.to_dict().get("tab0", [])
            if tab0:
                sat_date = get_next_saturday_str()
                txt = "\n".join([f"{i+1}. {m.get('song')} ({m.get('artist')})" for i, m in enumerate(tab0)])
                send_wa_message(f"🎸 *LISTA DO ENSAIO — SÁBADO ({sat_date})*\n\n{txt}\n\nEstudem, pessoal! 🤘{LINKS_FOOTER}")
            else:
                send_wa_message(f"⚠️ *Atenção:* A lista do Ensaio Atual está vazia no momento.{LINKS_FOOTER}")
        else:
            send_wa_message(f"⚠️ *Erro:* Documento de setlist não encontrado.{LINKS_FOOTER}")

    # C. Cancelamento de Ensaio
    elif action == "Cancelar Ensaio":
        db = firestore.client()
        sat_date = get_next_saturday_str()
        sat_iso = get_next_saturday_iso()
        reason = (log.get('reason') or log.get('detail') or 'Motivo não informado').strip()
        
        # Salva estado de cancelamento no Firestore
        db.collection("rehearsal_state").document("current").set({
            "cancelled_date": sat_iso,
            "reason": reason,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        
        msg = (
            f"🚫 *AVISO IMPORTANTE: ENSAIO CANCELADO*\n\n"
            f"Informamos que *não teremos ensaio* neste próximo sábado ({sat_date}).\n\n"
            f"📝 *Motivo:* {reason}\n\n"
            f"Aproveitem o descanso e continuem praticando em casa! 🎸🤘"
            f"{LINKS_FOOTER}"
        )
        send_wa_message(msg)

# 5. AGENDAMENTO: LEMBRETE DIÁRIO (14:10)
@scheduler_fn.on_schedule(schedule="10 14 * * *", timezone="America/Sao_Paulo")
def daily_reminder(event: scheduler_fn.ScheduledEvent) -> None:
    send_wa_message(f"📢 *Lembrete:* Não esqueça de votar nas enquetes de hoje!{LINKS_FOOTER}")

# 6. AGENDAMENTO: REPERTÓRIO (TERÇA ÀS 14:00)
@scheduler_fn.on_schedule(schedule="0 14 * * 2", timezone="America/Sao_Paulo")
def tuesday_repertoire(event: scheduler_fn.ScheduledEvent) -> None:
    db = firestore.client()
    
    # Verifica se o ensaio desta semana está cancelado
    sat_iso = get_next_saturday_iso()
    if is_rehearsal_cancelled(db, sat_iso):
        print(f"Cancelando disparo automático: ensaio de {sat_iso} está marcado como cancelado.")
        return

    doc = db.collection("setlists").document("data").get()
    if doc.exists:
        tab0 = doc.to_dict().get("tab0", [])
        if tab0:
            sat_date = get_next_saturday_str()
            txt = "\n".join([f"{i+1}. {m.get('song')} ({m.get('artist')})" for i, m in enumerate(tab0)])
            send_wa_message(f"🎸 *REPERTÓRIO DO ENSAIO — SÁBADO ({sat_date})*\n\n{txt}\n\nEstudem! 🤘{LINKS_FOOTER}")

# 7. AGENDAMENTO: ABRIR FÓRUM DO ENSAIO (SÁBADO 00:01)
@scheduler_fn.on_schedule(schedule="1 0 * * 6", timezone="America/Sao_Paulo")
def open_rehearsal_forum(event: scheduler_fn.ScheduledEvent) -> None:
    db = firestore.client()
    sat_iso = get_current_saturday_iso()
    sat_str = get_current_saturday_str()

    if is_rehearsal_cancelled(db, sat_iso):
        print(f"Fórum automático não criado: ensaio de {sat_iso} está cancelado.")
        return

    existing = list(db.collection("forum").where("rehearsalDate", "==", sat_iso).limit(1).stream())
    if existing:
        print(f"Fórum de {sat_iso} já existe.")
        return

    db.collection("forum").add({
        "title": f"Ensaio {sat_str} — Fórum automático",
        "date": sat_str,
        "open": True,
        "closed": False,
        "closedAt": None,
        "autoGenerated": True,
        "rehearsalDate": sat_iso,
        "posts": [],
        "createdAt": firestore.SERVER_TIMESTAMP
    })
    print(f"Fórum automático criado para o ensaio de {sat_iso}.")

# 8. AGENDAMENTO: ENCERRAR FÓRUM DO ENSAIO (SÁBADO 23:59)
@scheduler_fn.on_schedule(schedule="59 23 * * 6", timezone="America/Sao_Paulo")
def close_rehearsal_forum(event: scheduler_fn.ScheduledEvent) -> None:
    db = firestore.client()
    sat_iso = get_current_saturday_iso()

    forum_docs = list(db.collection("forum").where("rehearsalDate", "==", sat_iso).stream())
    if not forum_docs:
        print(f"Nenhum fórum encontrado para encerrar em {sat_iso}.")
        return

    batch = db.batch()
    close_count = 0
    for forum_doc in forum_docs:
        data = forum_doc.to_dict() or {}
        if data.get("closed") is True:
            continue
        batch.update(forum_doc.reference, {
            "closed": True,
            "open": False,
            "closedAt": firestore.SERVER_TIMESTAMP
        })
        close_count += 1

    if close_count:
        batch.commit()
    print(f"{close_count} fórum(ns) encerrado(s) para o ensaio de {sat_iso}.")

# 9. AGENDAMENTO: MONITOR DE ENQUETES (CADA 1 HORA)
@scheduler_fn.on_schedule(schedule="0 * * * *", timezone="America/Sao_Paulo")
def poll_monitor(event: scheduler_fn.ScheduledEvent) -> None:
    db = firestore.client()
    from datetime import timezone
    now = datetime.now(timezone.utc)
    
    # A. Notificar Encerramento (Enquetes que acabaram de expirar)
    expired = db.collection("polls").where("deadline", ">", (now - timedelta(minutes=60)).isoformat()).where("deadline", "<=", now.isoformat()).stream()
    for doc in expired:
        p = doc.to_dict()
        opts = p.get("options", [])
        if not opts: continue
        res = sorted(opts, key=lambda x: x.get('votes', 0), reverse=True)
        winner = res[0].get('label')
        t = p.get("type", "")
        if t in ["repertoire", "repertory"]:
            send_wa_message(f"🏁 *ENQUETE ENCERRADA!*\n\n🎸 Venceu: *{winner}*\nSerá inserida no repertório!{LINKS_FOOTER}")
        elif t in ["promotion", "tiebreaker"]:
            losers = "\n".join([f"{o.get('label')} ({o.get('votes', 0)} votos)" for o in res[1:]])
            send_wa_message(f"🏆 *RESULTADO DO DESEMPATE*\n\n✅ VENCEU: *{winner}*\n\n❌ Perderam:\n{losers}{LINKS_FOOTER}")

    # B. Notificar Faltando 24 Horas
    expiring_24h = db.collection("polls").where("deadline", ">", (now + timedelta(hours=23)).isoformat()).where("deadline", "<=", (now + timedelta(hours=24)).isoformat()).stream()
    for doc in expiring_24h:
        p = doc.to_dict()
        q = p.get("question", "Enquete")
        send_wa_message(f"⏳ *FALTAM 24 HORAS!*\n\nA enquete *\"{q}\"* encerra amanhã. Já deixou seu voto?{LINKS_FOOTER}")

    # C. Notificar Faltando 1 Hora
    expiring_1h = db.collection("polls").where("deadline", ">", now.isoformat()).where("deadline", "<=", (now + timedelta(hours=1)).isoformat()).stream()
    for doc in expiring_1h:
        p = doc.to_dict()
        q = p.get("question", "Enquete")
        send_wa_message(f"⚠️ *ÚLTIMA CHAMADA (1 HORA)!*\n\nA enquete *\"{q}\"* encerra em breve. Corre lá para votar!{LINKS_FOOTER}")
