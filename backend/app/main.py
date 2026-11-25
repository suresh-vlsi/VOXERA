from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.api.routes import router
from app.api.analytics import router as analytics_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title="VOXERA API", version="0.1.0", description="Independent voice intelligence platform")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(analytics_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "voxera-api", "version": "0.1.0"}


@app.get("/", response_class=HTMLResponse)
def home():
    return '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VOXERA</title><style>
    *{box-sizing:border-box}body{margin:0;background:#0b1220;color:#e8eef9;font:16px system-ui;display:grid;place-items:center;min-height:100vh;padding:24px}.panel{width:min(760px,100%);background:#121e32;border:1px solid #263a59;border-radius:22px;padding:28px;box-shadow:0 20px 80px #0006}h1{letter-spacing:.18em;margin:0;color:#8cc7ff}p{color:#aabbd3}.row{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}button,input,select{border-radius:10px;padding:12px;background:#1b2c46;color:#e8eef9;border:1px solid #395477}button{cursor:pointer;background:#2563a8}button:disabled{opacity:.5}textarea{width:100%;min-height:120px;background:#0b1628;color:#e8eef9;border:1px solid #304967;border-radius:12px;padding:14px;margin-top:8px}label{display:block;margin-top:16px;color:#aabbd3;font-size:14px}.muted{font-size:13px;color:#8196b3}.status{min-height:24px;color:#8cc7ff}</style></head><body><main class="panel"><h1>VOXERA</h1><p>Voice intelligence, starting with accurate dictation.</p><form id="form"><label>Audio clip (maximum upload size: 20 MB)</label><input id="audio" type="file" accept="audio/*" required><div class="row"><select id="language"><option value="auto">Auto detect</option><option value="en-IN">English (India)</option><option value="hi-IN">Hindi</option><option value="te-IN">Telugu</option><option value="ta-IN">Tamil</option><option value="kn-IN">Kannada</option><option value="ml-IN">Malayalam</option><option value="bn-IN">Bengali</option><option value="mr-IN">Marathi</option><option value="gu-IN">Gujarati</option><option value="pa-IN">Punjabi</option></select><button id="submit">Transcribe audio</button></div></form><div class="status" id="status" role="status"></div><label>Finished dictation</label><textarea id="text" readonly placeholder="Your cleaned dictation will appear here..."></textarea><label>Raw transcript</label><textarea id="transcript" readonly placeholder="Raw speech recognition output..."></textarea><p class="muted" id="meta">Your audio is sent to the VOXERA backend and then to Sarvam. Configure the API key on the server.</p></main><script>
    const form=document.getElementById('form');form.addEventListener('submit',async e=>{e.preventDefault();const file=document.getElementById('audio').files[0];if(!file)return;const btn=document.getElementById('submit'),status=document.getElementById('status');btn.disabled=true;status.textContent='Processing audio…';const data=new FormData();data.append('file',file);data.append('language_code',document.getElementById('language').value);try{const r=await fetch('/api/v1/dictate',{method:'POST',body:data});const payload=await r.json();if(!r.ok)throw new Error(payload.detail||'Request failed');const x=payload.result;document.getElementById('text').value=x.text||'';document.getElementById('transcript').value=x.transcript||'';document.getElementById('meta').textContent=x.degraded?'Finishing step degraded: '+x.degraded+' — displayed text may be raw. Usage: '+JSON.stringify(x.usage):'Dictation completed. Corrections: '+JSON.stringify(x.corrections)+' | Usage: '+JSON.stringify(x.usage);status.textContent=x.degraded?'Completed with degraded status.':'Dictation complete.'}catch(err){status.textContent='Error: '+err.message}finally{btn.disabled=false}});
    </script></body></html>'''
