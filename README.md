
# v16 — Pump.fun Token Tracker (Polling + Flask)

## 📡 Что делает
- Каждые 10 сек опрашивает последние 50 транзакций SPL Token Program
- Ищет инструкции `initializeMint`
- Сохраняет токены в `tokens_cache.json`
- Отдаёт JSON по `/tokens`

## 🚀 Деплой
1. Залей в GitHub
2. Подключи к Railway (Deploy from GitHub)
3. Открой `https://your-app.up.railway.app/tokens`
