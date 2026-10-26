from flask import Flask, jsonify, render_template_string, request, session
import os
import random

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pixel Quest Arcade</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1020; --panel:#151d35; --muted:#9eabc9; --cyan:#52e0d4; --pink:#ff6bb5; }
    * { box-sizing:border-box; }
    body { margin:0; min-height:100vh; font-family:system-ui,-apple-system,Segoe UI,sans-serif; color:#f4f7ff;
      background:radial-gradient(circle at 15% 10%,#25235a 0,transparent 32%),radial-gradient(circle at 90% 80%,#3b1748 0,transparent 30%),var(--bg); }
    .wrap { max-width:1000px; margin:auto; padding:28px 18px 50px; }
    header { display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; margin-bottom:28px; }
    .brand { font-size:1.2rem; font-weight:900; letter-spacing:.08em; }
    .brand span { color:var(--cyan); }
    .pill { border:1px solid #384567; color:var(--muted); border-radius:999px; padding:8px 13px; font-size:.85rem; }
    .hero { text-align:center; padding:28px 12px 34px; }
    .eyebrow { color:var(--cyan); text-transform:uppercase; font-size:.78rem; font-weight:800; letter-spacing:.2em; }
    h1 { font-size:clamp(2.2rem,6vw,4.5rem); line-height:1.03; margin:14px 0; letter-spacing:-.05em; }
    h1 em { font-style:normal; color:var(--pink); }
    .sub { max-width:600px; margin:0 auto; color:var(--muted); line-height:1.65; }
    .grid { display:grid; grid-template-columns:1.2fr .8fr; gap:18px; }
    .card { background:linear-gradient(145deg,rgba(26,36,65,.96),rgba(17,24,44,.96)); border:1px solid #2a385b; border-radius:22px; padding:24px; box-shadow:0 18px 55px #0003; }
    .card h2 { margin:0 0 8px; font-size:1.25rem; }
    .muted { color:var(--muted); font-size:.93rem; line-height:1.55; }
    .number { font-size:3.4rem; font-weight:900; letter-spacing:.06em; color:var(--cyan); text-align:center; margin:20px 0 8px; }
    .attempts { text-align:center; color:var(--muted); font-size:.9rem; }
    .controls { display:flex; gap:10px; margin-top:22px; }
    input { min-width:0; flex:1; border:1px solid #3b4a70; border-radius:12px; padding:13px 14px; color:white; background:#0d1428; font:inherit; }
    button { border:0; border-radius:12px; padding:13px 18px; background:linear-gradient(90deg,var(--cyan),#8bffc7); color:#07121c; font-weight:900; cursor:pointer; font:inherit; }
    button:hover { filter:brightness(1.08); transform:translateY(-1px); }
    .secondary { width:100%; margin-top:12px; color:#f5d9ff; background:#35244e; border:1px solid #61407a; }
    .message { min-height:28px; margin-top:15px; font-weight:700; text-align:center; }
    .stats { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:18px; }
    .stat { background:#0d1428; border:1px solid #273553; border-radius:14px; padding:14px; }
    .stat strong { display:block; font-size:1.5rem; color:var(--pink); }
    .stat span { color:var(--muted); font-size:.82rem; }
    .rules { padding-left:18px; color:var(--muted); line-height:1.9; }
    footer { text-align:center; color:#7481a2; margin-top:28px; font-size:.82rem; }
    @media(max-width:720px) { .grid { grid-template-columns:1fr; } .controls { flex-direction:column; } }
  </style>
</head>
<body>
  <div class="wrap">
    <header><div class="brand">PIXEL <span>QUEST</span> / ARCADE</div><div class="pill">🎮 MINI GAME • LEVEL 01</div></header>
    <section class="hero">
      <div class="eyebrow">Ready Player One?</div>
      <h1>Guess the <em>Secret</em><br>Number.</h1>
      <p class="sub">A tiny arcade challenge. Find the hidden number between 1 and 100 in as few attempts as possible.</p>
    </section>
    <main class="grid">
      <section class="card">
        <h2>🔐 The Number Vault</h2>
        <p class="muted">Enter a number and let the hints guide you. Can you beat the challenge?</p>
        <div class="number">?</div>
        <div class="attempts">Attempts used: <b id="attempts">0</b></div>
        <form id="guess-form">
          <div class="controls">
            <input id="guess" type="number" min="1" max="100" placeholder="Enter 1–100" required>
            <button type="submit">GUESS ↗</button>
          </div>
        </form>
        <div class="message" id="message" role="status">Your mission starts now.</div>
        <button class="secondary" id="restart" type="button">↻ Start New Game</button>
      </section>
      <aside class="card">
        <h2>🏆 Player Stats</h2>
        <p class="muted">Every guess gets you closer. Keep your streak alive!</p>
        <div class="stats">
          <div class="stat"><strong id="wins">0</strong><span>Games won</span></div>
          <div class="stat"><strong id="best">—</strong><span>Best attempts</span></div>
        </div>
        <h2 style="margin-top:25px">📜 How to Play</h2>
        <ol class="rules">
          <li>Pick a number from 1 to 100.</li>
          <li>Read the hint: too high or too low.</li>
          <li>Find the secret number to win.</li>
          <li>Start a new round and improve your score.</li>
        </ol>
      </aside>
    </main>
    <footer>PIXEL QUEST ARCADE · Built with Python + Flask · Have fun!</footer>
  </div>
<script>
  const form = document.getElementById('guess-form');
  const input = document.getElementById('guess');
  const message = document.getElementById('message');
  const attemptsEl = document.getElementById('attempts');
  const winsEl = document.getElementById('wins');
  const bestEl = document.getElementById('best');
  let attempts = 0;
  let finished = false;
  let wins = Number(localStorage.getItem('pq-wins') || 0);
  let best = localStorage.getItem('pq-best');
  winsEl.textContent = wins;
  bestEl.textContent = best || '—';

  async function newGame() {
    const response = await fetch('/api/new-game', {method:'POST'});
    const data = await response.json();
    attempts = 0; finished = false;
    attemptsEl.textContent = '0';
    message.textContent = 'New number generated. Good luck!';
    input.disabled = false; input.value = ''; input.focus();
  }
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (finished) return;
    const guess = Number(input.value);
    if (!Number.isInteger(guess) || guess < 1 || guess > 100) {
      message.textContent = 'Enter a whole number from 1 to 100.';
      return;
    }
    const response = await fetch('/api/guess', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({guess})
    });
    const data = await response.json();
    if (!response.ok) { message.textContent = data.error || 'Something went wrong.'; return; }
    attempts = data.attempts;
    attemptsEl.textContent = attempts;
    if (data.result === 'correct') {
      finished = true; input.disabled = true;
      message.textContent = `🎉 You cracked the vault in ${attempts} attempt${attempts === 1 ? '' : 's'}!`;
      wins += 1; localStorage.setItem('pq-wins', wins); winsEl.textContent = wins;
      if (!best || attempts < Number(best)) { best = attempts; localStorage.setItem('pq-best', best); bestEl.textContent = best; }
    } else {
      message.textContent = data.result === 'low' ? '⬆️ Too low! Try a higher number.' : '⬇️ Too high! Try a lower number.';
    }
    input.select();
  });
  document.getElementById('restart').addEventListener('click', newGame);
  newGame();
</script>
</body>
</html>
"""

@app.get("/")
def home():
    if "secret_number" not in session:
        session["secret_number"] = random.randint(1, 100)
        session["attempts"] = 0
    return render_template_string(PAGE)

@app.post("/api/new-game")
def new_game():
    session["secret_number"] = random.randint(1, 100)
    session["attempts"] = 0
    return jsonify(message="New game started")

@app.post("/api/guess")
def guess_number():
    data = request.get_json(silent=True) or {}
    try:
        guess = int(data.get("guess"))
    except (TypeError, ValueError):
        return jsonify(error="Please send a whole number."), 400
    if not 1 <= guess <= 100:
        return jsonify(error="Guess must be between 1 and 100."), 400

    if "secret_number" not in session:
        session["secret_number"] = random.randint(1, 100)
        session["attempts"] = 0

    session["attempts"] = session.get("attempts", 0) + 1
    secret = session["secret_number"]
    if guess == secret:
        result = "correct"
    elif guess < secret:
        result = "low"
    else:
        result = "high"

    return jsonify(result=result, attempts=session["attempts"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
