#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════╗
# ║            NEXUS TRADING AI  ·  v3.1.0 PROFESSIONAL         ║
# ║         AI-Powered Quantitative Intelligence Engine          ║
# ║              Sistema de Predicción con Red Neuronal          ║
# ╚══════════════════════════════════════════════════════════════╝

import asyncio
import random
from datetime import datetime, timedelta
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)
from telegram.constants import ParseMode

# ──────────────────────────────────────────────────────────────
#  CONFIGURACIÓN PRINCIPAL
# ──────────────────────────────────────────────────────────────
BOT_TOKEN = "TU_TOKEN_AQUI"   # Obtén tu token en @BotFather
ADMIN_IDS = [123456789]        # Tu Telegram user_id numérico

# Credenciales de acceso (estéticas — solo demo)
VALID_USERS = {
    "admin":  "nexus2024",
    "trader": "trading123",
    "demo":   "demo1234",
}

# Estados del ConversationHandler (login)
ASK_USER, ASK_PASS = range(2)


# ══════════════════════════════════════════════════════════════
#  MOTOR DE MERCADO (precios simulados en tiempo real)
# ══════════════════════════════════════════════════════════════

ASSETS: dict[str, dict] = {
    # ── CRIPTO ───────────────────────────────────────────────
    "BTC":    {"name": "Bitcoin",    "price": 67_842.50, "vol": 0.018, "emoji": "₿",  "type": "crypto"},
    "ETH":    {"name": "Ethereum",   "price":  3_521.80, "vol": 0.022, "emoji": "Ξ",  "type": "crypto"},
    "SOL":    {"name": "Solana",     "price":    178.40, "vol": 0.035, "emoji": "◎",  "type": "crypto"},
    "BNB":    {"name": "BNB",        "price":    594.20, "vol": 0.020, "emoji": "⬡",  "type": "crypto"},
    "AVAX":   {"name": "Avalanche",  "price":     38.60, "vol": 0.040, "emoji": "🔺", "type": "crypto"},
    "DOGE":   {"name": "Dogecoin",   "price":      0.163,"vol": 0.055, "emoji": "🐕", "type": "crypto"},
    "ARB":    {"name": "Arbitrum",   "price":      1.08, "vol": 0.048, "emoji": "🔵", "type": "crypto"},
    # ── FOREX ────────────────────────────────────────────────
    "EURUSD": {"name": "EUR/USD",    "price":   1.0847,  "vol": 0.003, "emoji": "🇪🇺", "type": "forex"},
    "GBPUSD": {"name": "GBP/USD",    "price":   1.2694,  "vol": 0.004, "emoji": "🇬🇧", "type": "forex"},
    "USDJPY": {"name": "USD/JPY",    "price":  155.30,   "vol": 0.003, "emoji": "🇯🇵", "type": "forex"},
    "USDCHF": {"name": "USD/CHF",    "price":    0.9041, "vol": 0.003, "emoji": "🇨🇭", "type": "forex"},
    # ── ACCIONES ─────────────────────────────────────────────
    "AAPL":   {"name": "Apple",      "price":   213.70,  "vol": 0.012, "emoji": "🍎", "type": "stock"},
    "NVDA":   {"name": "NVIDIA",     "price":   876.40,  "vol": 0.025, "emoji": "🖥",  "type": "stock"},
    "TSLA":   {"name": "Tesla",      "price":   176.90,  "vol": 0.030, "emoji": "⚡", "type": "stock"},
    "MSFT":   {"name": "Microsoft",  "price":   415.20,  "vol": 0.010, "emoji": "🪟", "type": "stock"},
    "AMZN":   {"name": "Amazon",     "price":   187.40,  "vol": 0.014, "emoji": "📦", "type": "stock"},
    "META":   {"name": "Meta",       "price":   486.30,  "vol": 0.018, "emoji": "🌐", "type": "stock"},
    # ── COMMODITIES ──────────────────────────────────────────
    "XAUUSD": {"name": "Gold",       "price": 2_347.80,  "vol": 0.008, "emoji": "🥇", "type": "commodity"},
    "XAGUSD": {"name": "Silver",     "price":    30.42,  "vol": 0.012, "emoji": "🥈", "type": "commodity"},
    "OIL":    {"name": "Crude Oil",  "price":    82.30,  "vol": 0.015, "emoji": "🛢",  "type": "commodity"},
}

_prices: dict[str, float] = {k: v["price"] for k, v in ASSETS.items()}
_prev:   dict[str, float] = dict(_prices)


def _tick() -> None:
    global _prices, _prev
    _prev = dict(_prices)
    for sym, info in ASSETS.items():
        shock = random.gauss(0, info["vol"] * _prices[sym])
        _prices[sym] = max(0.0001, _prices[sym] + shock)


def get_price(sym: str) -> tuple[float, float, float]:
    p, p0 = _prices[sym], _prev[sym]
    return p, p - p0, (p - p0) / p0 * 100


def fmt_price(sym: str, price: float) -> str:
    info = ASSETS[sym]
    if info["type"] == "forex" or price < 10:
        return f"{price:,.4f}"
    return f"{price:,.2f}"


def trend_bar(value: float, width: int = 10) -> str:
    filled = min(width, max(1, int(abs(value) / 4 * width)))
    return "█" * filled + "░" * (width - filled)


def spark(rising: bool = True) -> str:
    seq = sorted([random.choice("▁▂▃▄▅▆▇█") for _ in range(8)],
                 reverse=not rising)
    return "".join(seq)


def ai_signal(sym: str) -> dict:
    p = _prices[sym]
    rsi        = random.randint(30, 75)
    macd_h     = round(random.uniform(-1.5, 2.5), 3)
    confidence = random.randint(71, 97)
    stoch_k    = random.randint(20, 80)
    atr        = round(p * random.uniform(0.005, 0.02), 4)
    adx        = random.randint(22, 68)
    signals    = ["COMPRAR 🟢", "VENDER 🔴", "MANTENER 🟡", "COMPRA FUERTE 💚", "VENTA FUERTE ❤️"]
    weights    = [0.35, 0.18, 0.22, 0.15, 0.10]
    signal     = random.choices(signals, weights=weights)[0]
    sentiments = ["Alcista", "Bajista", "Neutral", "Muy Alcista", "Cautelosamente Alcista"]
    pnl_pred   = round(random.uniform(8, 450), 2)   # siempre positivo
    return {
        "signal":     signal,
        "confidence": confidence,
        "rsi":        rsi,
        "macd_h":     macd_h,
        "stoch_k":    stoch_k,
        "atr":        atr,
        "adx":        adx,
        "sentiment":  random.choice(sentiments),
        "pnl_pred":   pnl_pred,
        "tp1":        round(p * random.uniform(1.015, 1.04), 4),
        "tp2":        round(p * random.uniform(1.04,  1.08), 4),
        "sl":         round(p * random.uniform(0.95,  0.985), 4),
    }


def prediction_ai(sym: str) -> dict:
    p = _prices[sym]
    models = ["LSTM + Transformer", "CNN-BiLSTM", "XGBoost Ensemble", "GPT-FineTuned v2"]
    return {
        "h1":  round(p * random.uniform(1.002, 1.015), 4),
        "h4":  round(p * random.uniform(1.005, 1.025), 4),
        "d1":  round(p * random.uniform(1.010, 1.045), 4),
        "w1":  round(p * random.uniform(1.020, 1.080), 4),
        "acc_h1": round(random.uniform(79, 95), 1),
        "acc_d1": round(random.uniform(68, 88), 1),
        "model":  random.choice(models),
        "dp":     random.randint(48_000, 250_000),
    }


# ══════════════════════════════════════════════════════════════
#  BASE DE DATOS EN MEMORIA (sesiones)
# ══════════════════════════════════════════════════════════════

SESSIONS: dict[int, dict] = {}


def get_session(uid: int) -> dict | None:
    s = SESSIONS.get(uid)
    return s if (s and s.get("logged")) else None


def new_session(uid: int, username: str) -> dict:
    balance = round(random.uniform(2_500, 15_000), 2)
    session = {
        "logged":       True,
        "username":     username,
        "balance":      balance,
        "total_profit": round(random.uniform(480, 3_200), 2),
        "trades":       random.randint(12, 340),
        "win_rate":     round(random.uniform(71, 94), 1),
        "joined":       datetime.utcnow(),
        "plan":         random.choice(["PRO", "ELITE", "INSTITUTIONAL"]),
        "open_trades":  _gen_open_trades(),
        "daily_pnl":    [],
    }
    SESSIONS[uid] = session
    return session


def _gen_open_trades() -> list[dict]:
    symbols = ["BTC", "ETH", "NVDA", "XAUUSD", "SOL", "EURUSD", "TSLA"]
    trades  = []
    for _ in range(random.randint(2, 5)):
        sym = random.choice(symbols)
        ep  = _prices[sym] * random.uniform(0.96, 1.04)
        pnl = round(random.uniform(8, 450), 2)         # siempre positivo
        trades.append({
            "sym":  sym,
            "side": random.choice(["LONG", "SHORT"]),
            "entry": round(ep, 4),
            "pnl":   pnl,
            "emoji": ASSETS[sym]["emoji"],
        })
    return trades


def add_profit(uid: int) -> float:
    profit = round(random.uniform(8, 450), 2)
    s = SESSIONS.get(uid, {})
    if s:
        s["balance"]      = round(s.get("balance", 0) + profit, 2)
        s["total_profit"] = round(s.get("total_profit", 0) + profit, 2)
        s["trades"]       = s.get("trades", 0) + 1
        s.setdefault("daily_pnl", []).append(profit)
    return profit


# ══════════════════════════════════════════════════════════════
#  TEXTOS DE PANTALLA
# ══════════════════════════════════════════════════════════════

def market_snapshot() -> str:
    _tick()
    ts = datetime.utcnow().strftime("%Y-%m-%d  %H:%M:%S")
    lines = [
        "```",
        "╔══════════════════════════════════════════╗",
        "║   NEXUS AI ·  MARKET LIVE FEED           ║",
        f"║   {ts} UTC    ║",
        "╚══════════════════════════════════════════╝",
        "",
    ]
    for tipo, label in [("crypto","CRYPTO"),("stock","STOCKS"),
                        ("forex","FOREX"),("commodity","COMMODITIES")]:
        subset = [(s, i) for s, i in ASSETS.items() if i["type"] == tipo]
        lines.append(f"  ── {label} {'─'*(30-len(label))}")
        for sym, info in subset:
            p, _, pct = get_price(sym)
            arrow = "▲" if pct >= 0 else "▼"
            lines.append(
                f"  {info['emoji']} {sym:<8} {fmt_price(sym,p):>13}  "
                f"{arrow}{pct:+.2f}%"
            )
        lines.append("")
    lines += ["  ⚡ NEXUS Quantum Engine  ·  latencia 12ms", "```"]
    return "\n".join(lines)


def portfolio_text(uid: int) -> str:
    s = SESSIONS.get(uid, {})
    holdings = [("BTC",0.42),("ETH",3.80),("NVDA",8.0),("XAUUSD",1.5),("SOL",22.0)]
    _tick()
    total = 0.0
    lines = [
        "```",
        "╔══════════════════════════════════════════╗",
        "║        💼  MI PORTFOLIO — NEXUS AI        ║",
        "╚══════════════════════════════════════════╝",
        "",
        f"  Usuario  : @{s.get('username','demo')}",
        f"  Plan     : {s.get('plan','PRO')} ✦",
        f"  Balance  : ${s.get('balance',0):>10,.2f}",
        f"  P&L Total: +${s.get('total_profit',0):>9,.2f}  ✅",
        f"  Win Rate : {s.get('win_rate',0)}%",
        f"  Trades   : {s.get('trades',0)}",
        "",
        f"  {'ACTIVO':<8} {'CANT':>7} {'VALOR USD':>13} {'P&L':>10}",
        "  " + "─" * 43,
    ]
    for sym, qty in holdings:
        p, _, _ = get_price(sym)
        val = p * qty
        pnl = round(val * random.uniform(0.04, 0.18), 2)   # ganancia positiva
        total += val
        lines.append(
            f"  {ASSETS[sym]['emoji']}{sym:<7} {qty:>7.3f} ${val:>12,.2f} +${pnl:>8.2f}"
        )
    last_pnl = (s.get("daily_pnl") or [round(random.uniform(8,450),2)])[-1]
    lines += [
        "  " + "─" * 43,
        f"  {'TOTAL':>8}        ${total:>12,.2f}",
        "",
        f"  Ganancia hoy     : +${last_pnl:.2f}",
        f"  Sharpe ratio(30d): {random.uniform(1.8,3.4):.2f}",
        f"  Max Drawdown     : -{random.uniform(0.8,3.2):.1f}%",
        f"  Sortino ratio    : {random.uniform(2.1,4.5):.2f}",
        "```",
    ]
    return "\n".join(lines)


def open_trades_text(uid: int) -> str:
    s      = SESSIONS.get(uid, {})
    trades = s.get("open_trades", [])
    _tick()
    lines = [
        "```",
        "╔══════════════════════════════════════════╗",
        "║     📂  OPERACIONES ABIERTAS              ║",
        "╚══════════════════════════════════════════╝",
        "",
        f"  {'PAR':<10} {'LADO':>6} {'ENTRADA':>13} {'P&L USD':>10}",
        "  " + "─" * 45,
    ]
    total_pnl = 0.0
    for t in trades:
        sym       = t["sym"]
        side_icon = "🟢" if t["side"] == "LONG" else "🔴"
        pnl       = t["pnl"]
        total_pnl += pnl
        lines.append(
            f"  {t['emoji']}{sym:<9} {side_icon}{t['side']:>4} "
            f"{fmt_price(sym, t['entry']):>13} +${pnl:>8.2f}"
        )
    lines += [
        "  " + "─" * 45,
        f"  {'P&L TOTAL':>33} +${total_pnl:>8.2f}",
        "",
        "  Todas las posiciones en beneficio  ✅",
        "```",
    ]
    return "\n".join(lines)


def account_summary(uid: int) -> str:
    s      = SESSIONS.get(uid, {})
    joined = s.get("joined", datetime.utcnow())
    days   = max(1, (datetime.utcnow() - joined).days)
    daily_avg = round(s.get("total_profit", 0) / days, 2)
    lines = [
        "```",
        "╔══════════════════════════════════════════╗",
        "║   👤  RESUMEN DE CUENTA  —  NEXUS AI      ║",
        "╚══════════════════════════════════════════╝",
        "",
        f"  Usuario       : @{s.get('username','demo')}",
        f"  Plan          : {s.get('plan','PRO')} ✦",
        f"  Registro      : {joined.strftime('%Y-%m-%d')}",
        f"  Días activo   : {days}",
        "",
        "  ── BALANCE ──────────────────────────",
        f"  Capital total : ${s.get('balance',0):>10,.2f}",
        f"  P&L acumulado : +${s.get('total_profit',0):>9,.2f}",
        f"  Ganancia/día  : +${daily_avg:>9.2f}",
        "",
        "  ── RENDIMIENTO ──────────────────────",
        f"  Win rate      : {s.get('win_rate',0)}%",
        f"  Trades totales: {s.get('trades',0)}",
        f"  ROI mensual   : +{random.uniform(12,38):.1f}%",
        f"  Volatilidad   : {random.uniform(3,9):.1f}%",
        "",
        "  ── MOTOR IA ─────────────────────────",
        "  Modelo        : NEXUS-GPT Quant v3.1",
        f"  Señales hoy   : {random.randint(8,24)}",
        f"  Precisión 7d  : {random.uniform(78,95):.1f}%",
        "```",
    ]
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════
#  TECLADOS INLINE
# ══════════════════════════════════════════════════════════════

SPLASH = (
    "```\n"
    "  ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗\n"
    "  ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝\n"
    "  ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗\n"
    "  ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║\n"
    "  ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║\n"
    "  ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝\n"
    "         TRADING AI  ·  v3.1  PROFESSIONAL\n"
    "```"
)


def login_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Iniciar Sesión",  callback_data="do_login")],
        [InlineKeyboardButton("ℹ️ Acerca de NEXUS", callback_data="menu_about_public")],
    ])


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Mercado Live",     callback_data="menu_market"),
         InlineKeyboardButton("🤖 Señales IA",       callback_data="menu_signals")],
        [InlineKeyboardButton("🔮 Predicciones IA",  callback_data="menu_predict"),
         InlineKeyboardButton("📈 Análisis Técnico", callback_data="menu_analysis")],
        [InlineKeyboardButton("💼 Mi Portfolio",     callback_data="menu_portfolio"),
         InlineKeyboardButton("📂 Operaciones",      callback_data="menu_trades")],
        [InlineKeyboardButton("💰 Ejecutar Trade",   callback_data="menu_execute"),
         InlineKeyboardButton("📰 Noticias",         callback_data="menu_news")],
        [InlineKeyboardButton("🏆 Rankings",         callback_data="menu_top"),
         InlineKeyboardButton("👤 Mi Cuenta",        callback_data="menu_account")],
        [InlineKeyboardButton("🔔 Alertas",          callback_data="menu_alerts"),
         InlineKeyboardButton("⚙️ Ajustes",          callback_data="menu_settings")],
        [InlineKeyboardButton("🚪 Cerrar Sesión",    callback_data="do_logout")],
    ])


def market_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("₿ Cripto",       callback_data="market_crypto"),
         InlineKeyboardButton("📉 Forex",        callback_data="market_forex")],
        [InlineKeyboardButton("🏢 Acciones",    callback_data="market_stocks"),
         InlineKeyboardButton("🛢 Commodities", callback_data="market_commodities")],
        [InlineKeyboardButton("🔄 Actualizar",  callback_data="market_all"),
         InlineKeyboardButton("🏠 Menú",        callback_data="back_main")],
    ])


def signal_kb() -> InlineKeyboardMarkup:
    buttons, row = [], []
    for sym in list(ASSETS.keys())[:15]:
        info = ASSETS[sym]
        row.append(InlineKeyboardButton(f"{info['emoji']}{sym}", callback_data=f"sig_{sym}"))
        if len(row) == 3:
            buttons.append(row); row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🏠 Menú", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def predict_kb() -> InlineKeyboardMarkup:
    syms = ["BTC","ETH","SOL","NVDA","AAPL","XAUUSD","TSLA","EURUSD"]
    buttons, row = [], []
    for sym in syms:
        info = ASSETS[sym]
        row.append(InlineKeyboardButton(f"{info['emoji']}{sym}", callback_data=f"pred_{sym}"))
        if len(row) == 2:
            buttons.append(row); row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🏠 Menú", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def execute_trade_kb() -> InlineKeyboardMarkup:
    syms = ["BTC","ETH","NVDA","XAUUSD","SOL"]
    rows = []
    for sym in syms:
        rows.append([
            InlineKeyboardButton(f"🟢 LONG  {ASSETS[sym]['emoji']}{sym}",
                                 callback_data=f"exec_long_{sym}"),
            InlineKeyboardButton(f"🔴 SHORT {ASSETS[sym]['emoji']}{sym}",
                                 callback_data=f"exec_short_{sym}"),
        ])
    rows.append([InlineKeyboardButton("🔙 Volver", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def back_kb(dest: str = "back_main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data=dest)]])


# ══════════════════════════════════════════════════════════════
#  HELPERS INTERNOS
# ══════════════════════════════════════════════════════════════

async def _show_main_menu(obj, edit: bool = False) -> None:
    """Muestra el menú principal. obj puede ser Update o CallbackQuery."""
    if hasattr(obj, "callback_query"):          # Update
        uid  = obj.effective_user.id
        send = obj.message.reply_text if not edit else None
    else:                                        # CallbackQuery
        uid  = obj.from_user.id
        send = None

    s    = get_session(uid) or {}
    name = s.get("username", "trader")
    bal  = s.get("balance", 0)
    pnl  = s.get("total_profit", 0)

    text = (
        f"*🏠 NEXUS AI — Panel Principal*\n\n"
        f"┌─────────────────────────────┐\n"
        f"│  👤 *@{name}*  \\|  Plan: *{s.get('plan','PRO')}*\n"
        f"│  💵 Balance: `${bal:,.2f}`\n"
        f"│  📈 P\\&L Total: `+${pnl:,.2f}` ✅\n"
        f"│  🎯 Win Rate: `{s.get('win_rate',0)}%`\n"
        f"└─────────────────────────────┘\n\n"
        f"_Mercados activos · Motor IA corriendo_"
    )
    kb = main_menu_kb()

    if edit and hasattr(obj, "edit_message_text"):
        await obj.edit_message_text(text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=kb)
    elif hasattr(obj, "message") and obj.message:
        await obj.message.reply_text(text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=kb)
    else:
        await obj.edit_message_text(text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=kb)


def _require_login(func):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.callback_query.from_user.id
        if not get_session(uid):
            await update.callback_query.answer("🔐 Debes iniciar sesión primero", show_alert=True)
            await update.callback_query.edit_message_text(
                f"{SPLASH}\n\n🔐 *Sesión expirada*\\. Inicia sesión de nuevo\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=login_kb()
            )
            return
        return await func(update, ctx)
    return wrapper


# ══════════════════════════════════════════════════════════════
#  LOGIN — ConversationHandler
# ══════════════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if get_session(uid):
        await _show_main_menu(update)
        return
    await update.message.reply_text(
        f"{SPLASH}\n\n"
        "*Bienvenido a NEXUS Trading AI*\n\n"
        "La plataforma de trading cuantitativo más avanzada del mercado\\.\n"
        "Motor IA de última generación con predicciones en tiempo real\\.\n\n"
        "🔐 _Inicia sesión para acceder a tu dashboard_",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=login_kb()
    )


async def cb_do_login(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "🔐 *NEXUS AI — Autenticación Segura*\n\n"
        "Introduce tu *nombre de usuario*:\n\n"
        "_Credenciales de demo:_\n"
        "`usuario: demo`\n"
        "`contraseña: demo1234`",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return ASK_USER


async def ask_password(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text.strip().lower()
    ctx.user_data["login_user"] = username
    await update.message.reply_text(
        "🔑 *Introduce tu contraseña:*\n\n"
        "_Tu mensaje será eliminado automáticamente por seguridad\\._",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return ASK_PASS


async def check_password(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    uid      = update.effective_user.id
    username = ctx.user_data.get("login_user", "")
    password = update.message.text.strip()

    try:
        await update.message.delete()
    except Exception:
        pass

    if VALID_USERS.get(username) == password:
        s = new_session(uid, username)
        await update.effective_chat.send_message(
            f"✅ *¡Acceso concedido\\!*\n\n"
            f"Bienvenido de nuevo, *@{username}* 🎉\n\n"
            f"```\n"
            f"  Autenticando...          ████████ 100%\n"
            f"  Cargando portfolio...    ████████ 100%\n"
            f"  Conectando mercados...   ████████ 100%\n"
            f"  Motor IA iniciado...     ████████ 100%\n"
            f"```\n\n"
            f"_Sistema listo\\. Latencia: 12ms_",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await asyncio.sleep(1.2)
        bal = s.get("balance", 0)
        pnl = s.get("total_profit", 0)
        await update.effective_chat.send_message(
            f"*🏠 NEXUS AI — Panel Principal*\n\n"
            f"┌─────────────────────────────┐\n"
            f"│  👤 *@{username}*  \\|  Plan: *{s.get('plan','PRO')}*\n"
            f"│  💵 Balance: `${bal:,.2f}`\n"
            f"│  📈 P\\&L Total: `+${pnl:,.2f}` ✅\n"
            f"│  🎯 Win Rate: `{s.get('win_rate',0)}%`\n"
            f"└─────────────────────────────┘\n\n"
            f"_Mercados activos · Motor IA corriendo_",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_kb()
        )
    else:
        await update.effective_chat.send_message(
            "❌ *Credenciales incorrectas*\n\n"
            "Usa `/start` para intentarlo de nuevo\\.\n\n"
            "_Demo:_ `demo / demo1234`",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    return ConversationHandler.END


async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Login cancelado\\.", parse_mode=ParseMode.MARKDOWN_V2)
    return ConversationHandler.END


# ══════════════════════════════════════════════════════════════
#  CALLBACK HANDLER (botones del menú)
# ══════════════════════════════════════════════════════════════

@_require_login
async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    q    = update.callback_query
    data = q.data
    uid  = q.from_user.id
    await q.answer()

    # ── Menú principal ──────────────────────────────────────
    if data == "back_main":
        await _show_main_menu(q, edit=True)

    # ── Mercado ─────────────────────────────────────────────
    elif data in ("menu_market", "market_all"):
        await q.edit_message_text(market_snapshot(), parse_mode=ParseMode.MARKDOWN_V2,
                                  reply_markup=market_kb())

    elif data.startswith("market_"):
        tipo_map = {"crypto":"crypto","forex":"forex","stocks":"stock","commodities":"commodity"}
        tipo  = tipo_map.get(data.split("_")[1], "crypto")
        _tick()
        subset = [(s, i) for s, i in ASSETS.items() if i["type"] == tipo]
        lines  = ["```",
                  f"  {'SYM':<8} {'PRECIO':>14} {'CAMBIO%':>9}  {'BAR':>10}",
                  "  " + "─" * 46]
        for sym, info in subset:
            p, _, pct = get_price(sym)
            arrow = "▲" if pct >= 0 else "▼"
            bar   = trend_bar(abs(pct))
            lines.append(
                f"  {info['emoji']}{sym:<7} {fmt_price(sym,p):>14} "
                f"{arrow}{pct:+.2f}%  {bar}"
            )
        lines.append("```")
        await q.edit_message_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN_V2,
                                  reply_markup=market_kb())

    # ── Señales IA ──────────────────────────────────────────
    elif data == "menu_signals":
        await q.edit_message_text(
            "*🤖 SEÑALES IA — Tiempo Real*\n\nSelecciona un activo:",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=signal_kb()
        )

    elif data.startswith("sig_"):
        sym = data[4:]
        _tick()
        sig  = ai_signal(sym)
        info = ASSETS[sym]
        p, _, pct = get_price(sym)
        bar  = trend_bar(abs(pct))
        msg  = (
            f"*🤖 SEÑAL IA — {info['emoji']} {sym}*\n\n"
            f"*Señal:*  `{sig['signal']}`\n"
            f"*Confianza IA:* `{sig['confidence']}%`  `{bar}`\n\n"
            f"```\n"
            f"  ── PRECIO ──────────────────────\n"
            f"  Actual        : {fmt_price(sym,p)}\n"
            f"  Take Profit 1 : {fmt_price(sym,sig['tp1'])}\n"
            f"  Take Profit 2 : {fmt_price(sym,sig['tp2'])}\n"
            f"  Stop Loss     : {fmt_price(sym,sig['sl'])}\n"
            f"  P&L esperado  : +${sig['pnl_pred']:.2f}\n"
            f"\n"
            f"  ── INDICADORES ─────────────────\n"
            f"  RSI(14)   : {sig['rsi']}\n"
            f"  MACD Hist : {sig['macd_h']:+.3f}\n"
            f"  Stoch %K  : {sig['stoch_k']}\n"
            f"  ATR       : {sig['atr']}\n"
            f"  ADX       : {sig['adx']}\n"
            f"  Sentim.   : {sig['sentiment']}\n"
            f"```\n"
            f"_⚠️ Solo con fines informativos\\. No asesoramiento financiero\\._"
        )
        await q.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Actualizar", callback_data=f"sig_{sym}"),
                 InlineKeyboardButton("🔮 Predicción", callback_data=f"pred_{sym}")],
                [InlineKeyboardButton("🔙 Señales",    callback_data="menu_signals")]
            ])
        )

    # ── Predicciones IA ─────────────────────────────────────
    elif data == "menu_predict":
        await q.edit_message_text(
            "*🔮 PREDICCIONES IA — NEXUS Neural Engine*\n\nElige un activo:",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=predict_kb()
        )

    elif data.startswith("pred_"):
        sym  = data[5:]
        _tick()
        pred = prediction_ai(sym)
        info = ASSETS[sym]
        p, _, pct = get_price(sym)
        bar_h1 = trend_bar(pred["acc_h1"] / 10)
        bar_d1 = trend_bar(pred["acc_d1"] / 10)
        msg = (
            f"*🔮 PREDICCIÓN IA — {info['emoji']} {sym}*\n\n"
            f"*Modelo:* `{pred['model']}`\n"
            f"*Dataset:* `{pred['dp']:,} velas históricas`\n\n"
            f"```\n"
            f"  ── PROYECCIÓN DE PRECIO ────────\n"
            f"  Actual  :  {fmt_price(sym,p)}\n"
            f"  1H  ▲  :  {fmt_price(sym,pred['h1'])}  (acc {pred['acc_h1']}%)\n"
            f"  4H  ▲  :  {fmt_price(sym,pred['h4'])}\n"
            f"  1D  ▲  :  {fmt_price(sym,pred['d1'])}  (acc {pred['acc_d1']}%)\n"
            f"  1W  ▲  :  {fmt_price(sym,pred['w1'])}\n"
            f"\n"
            f"  ── CONFIANZA DEL MODELO ────────\n"
            f"  Corto plazo :  {bar_h1}  {pred['acc_h1']}%\n"
            f"  Largo plazo :  {bar_d1}  {pred['acc_d1']}%\n"
            f"\n"
            f"  Tendencia general : ALCISTA ▲\n"
            f"```\n"
            f"_Predicciones basadas en IA cuantitativa\\._"
        )
        await q.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Actualizar",   callback_data=f"pred_{sym}"),
                 InlineKeyboardButton("🤖 Señal",        callback_data=f"sig_{sym}")],
                [InlineKeyboardButton("🔙 Predicciones", callback_data="menu_predict")]
            ])
        )

    # ── Análisis técnico ────────────────────────────────────
    elif data == "menu_analysis":
        sym  = random.choice(["BTC","ETH","NVDA","XAUUSD","SOL","TSLA"])
        info = ASSETS[sym]
        _tick()
        p, _, pct = get_price(sym)
        sig  = ai_signal(sym)
        ema9   = round(p * random.uniform(0.98, 1.02), 4)
        ema21  = round(p * random.uniform(0.96, 1.04), 4)
        ema50  = round(p * random.uniform(0.93, 1.07), 4)
        bb_up  = round(p * random.uniform(1.02, 1.05), 4)
        bb_dn  = round(p * random.uniform(0.95, 0.98), 4)
        vwap   = round(p * random.uniform(0.99, 1.01), 4)
        vol24  = round(random.uniform(1.2, 62.4), 1)
        msg = (
            f"*📈 ANÁLISIS TÉCNICO AVANZADO*\n"
            f"*{info['emoji']} {info['name']} \\({sym}\\)*\n\n"
            f"```\n"
            f"  ── PRECIO Y VOLUMEN ────────────\n"
            f"  Precio actual :  {fmt_price(sym,p)}\n"
            f"  VWAP          :  {fmt_price(sym,vwap)}\n"
            f"  Volumen 24h   :  ${vol24}B\n"
            f"\n"
            f"  ── MEDIAS MÓVILES ──────────────\n"
            f"  EMA  9  :  {fmt_price(sym,ema9)}\n"
            f"  EMA 21  :  {fmt_price(sym,ema21)}\n"
            f"  EMA 50  :  {fmt_price(sym,ema50)}\n"
            f"\n"
            f"  ── BANDAS DE BOLLINGER ─────────\n"
            f"  Superior:  {fmt_price(sym,bb_up)}\n"
            f"  Inferior:  {fmt_price(sym,bb_dn)}\n"
            f"\n"
            f"  ── OSCILADORES ─────────────────\n"
            f"  RSI(14) :  {sig['rsi']}\n"
            f"  MACD H  :  {sig['macd_h']:+.3f}\n"
            f"  Stoch%K :  {sig['stoch_k']}\n"
            f"  ADX     :  {sig['adx']}\n"
            f"  ATR     :  {sig['atr']}\n"
            f"\n"
            f"  ── CONCLUSIÓN IA ───────────────\n"
            f"  Señal   :  {sig['signal']}\n"
            f"  Conf.   :  {sig['confidence']}%\n"
            f"  P&L est.:  +${sig['pnl_pred']:.2f}\n"
            f"```"
        )
        await q.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Otro activo", callback_data="menu_analysis"),
                 InlineKeyboardButton("🏠 Menú",        callback_data="back_main")]
            ])
        )
