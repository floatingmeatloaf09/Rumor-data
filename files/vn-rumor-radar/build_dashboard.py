# -*- coding: utf-8 -*-
"""
build_dashboard.py — Sinh docs/index.html (dashboard tĩnh) từ data/items.json.
Dashboard có: bộ lọc nguồn/cảm xúc/xác thực, tìm kiếm, link gốc từng bài.
"""
import json
import os
from datetime import datetime, timedelta, timezone

VN_TZ = timezone(timedelta(hours=7))
BASE = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE, "data", "items.json")
OUT_FILE = os.path.join(BASE, "docs", "index.html")

TEMPLATE = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Radar Tin Đồn — Công ty đại chúng VN</title>
<style>
:root{
  --bg:#0E1726;--panel:#16223A;--panel2:#1B2A45;--line:#24365A;
  --text:#E8EDF7;--muted:#8DA2C0;
  --green:#2EDB81;--red:#FF5C5C;--amber:#FFC53D;--cyan:#4DD6FF;--violet:#B388FF;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:inherit}
.wrap{max-width:1080px;margin:0 auto;padding:18px 14px}
.tape{overflow:hidden;background:#0A1120;border-bottom:1px solid var(--line);padding:7px 0}
.tape-inner{display:flex;gap:26px;white-space:nowrap;font:12px var(--mono);
  animation:tape 32s linear infinite}
@keyframes tape{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media(prefers-reduced-motion:reduce){.tape-inner{animation:none}}
h1{font-size:21px;margin:0;letter-spacing:-.02em}
.sub{color:var(--muted);font-size:13px;margin-top:3px}
.head{display:flex;flex-wrap:wrap;gap:10px;align-items:center;
  justify-content:space-between;margin-bottom:14px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:10px;margin-bottom:14px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:11px 13px}
.stat .l{color:var(--muted);font-size:10.5px;text-transform:uppercase;letter-spacing:.08em}
.stat .v{font:700 21px var(--mono);margin-top:3px}
.filters{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:11px;margin-bottom:14px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.search{display:flex;align-items:center;gap:7px;background:var(--bg);
  border:1px solid var(--line);border-radius:8px;padding:6px 10px;flex:1 1 190px}
.search input{background:none;border:none;outline:none;color:var(--text);
  font-size:13px;width:100%}
.chip{cursor:pointer;font:12px var(--mono);padding:4px 11px;border-radius:999px;
  border:1px solid var(--line);background:none;color:var(--muted);transition:.15s}
.chip.on{border-color:currentColor;background:rgba(255,255,255,.05)}
.grid{display:grid;grid-template-columns:minmax(0,1fr) 240px;gap:14px}
@media(max-width:760px){.grid{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:13px 15px;margin-bottom:10px}
.card .row1{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin-bottom:5px}
.tk{font:700 14px var(--mono);background:var(--panel2);border:1px solid var(--line);
  border-radius:6px;padding:1px 8px}
.tag{font:11px var(--mono);padding:2px 8px;border-radius:999px;
  border:1px solid;white-space:nowrap}
.title a{font-size:14.5px;font-weight:600;line-height:1.4;text-decoration:none}
.title a:hover{text-decoration:underline;color:var(--cyan)}
.snip{color:var(--muted);font-size:13px;margin-top:4px}
.meta{display:flex;flex-wrap:wrap;gap:13px;align-items:center;margin-top:9px;
  font-size:12px;color:var(--muted)}
.meta .link a{color:var(--cyan);text-decoration:none;font:11px var(--mono)}
.meta .link a:hover{text-decoration:underline}
.side{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:13px;margin-bottom:12px}
.side h3{margin:0 0 9px;font-size:11px;color:var(--muted);
  text-transform:uppercase;letter-spacing:.08em}
.srow{display:flex;justify-content:space-between;align-items:center;
  padding:6px 0;border-bottom:1px solid var(--line);font:13px var(--mono)}
.srow:last-child{border-bottom:none}
.srow .t{font-weight:700;cursor:pointer}
.srow .t:hover{color:var(--cyan)}
.warn{border:1px solid rgba(255,197,61,.35);background:rgba(255,197,61,.07);
  border-radius:10px;padding:13px;font-size:12px;color:var(--muted);line-height:1.6}
.warn b{color:var(--amber)}
.heat{display:inline-flex;align-items:center;gap:5px}
.heatbar{width:50px;height:4px;background:var(--line);border-radius:2px;overflow:hidden}
.heatbar i{display:block;height:4px}
.empty{border:1px dashed var(--line);border-radius:10px;padding:22px;
  text-align:center;color:var(--muted)}
.day{font:600 12px var(--mono);color:var(--muted);margin:16px 0 8px;
  text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid var(--line);
  padding-bottom:5px}
button:focus-visible,a:focus-visible{outline:2px solid var(--cyan);outline-offset:2px}
</style>
</head>
<body>
<div class="tape"><div class="tape-inner" id="tape"></div></div>
<div class="wrap">
  <div class="head">
    <div>
      <h1>📡 Radar Tin Đồn — Công ty đại chúng VN</h1>
      <div class="sub">Cập nhật tự động lúc __UPDATED__ · __TOTAL__ tin / __DAYS__ ngày gần nhất</div>
    </div>
  </div>
  <div class="stats" id="stats"></div>
  <div class="filters">
    <div class="search">🔎<input id="q" placeholder="Tìm mã CK, công ty, từ khoá..."></div>
    <div id="chips"></div>
  </div>
  <div class="grid">
    <div id="feed"></div>
    <div>
      <div class="side"><h3>📈 Mã được nhắc nhiều</h3><div id="top"></div></div>
      <div class="warn"><b>⚠ Lưu ý:</b> Tin đồn chưa kiểm chứng có thể sai lệch hoặc bị
      thao túng nhằm tác động giá cổ phiếu. Luôn đối chiếu công bố thông tin chính thức
      (HOSE, HNX, website doanh nghiệp) trước khi ra quyết định. Trang này không phải
      khuyến nghị đầu tư.</div>
    </div>
  </div>
</div>
<script>
const ITEMS = __ITEMS_JSON__;
const SRC = {press:["Báo chính thống","var(--cyan)","📰"],
             forum:["Diễn đàn","var(--amber)","💬"],
             social:["Mạng xã hội","var(--violet)","👥"]};
const SEN = {positive:["Tích cực","var(--green)"],negative:["Tiêu cực","var(--red)"],
             neutral:["Trung lập","var(--muted)"]};
const VER = {verified:["✓ Đã kiểm chứng","var(--cyan)"],
             unverified:["⚠ Chưa kiểm chứng","var(--amber)"],
             debunked:["✕ Đã bác bỏ","var(--violet)"]};
let f = {q:"",src:"all",sen:"all",ver:"all"};

function heatColor(h){return h>=80?"var(--red)":h>=60?"var(--amber)":"var(--green)"}
function heatHtml(h){return `<span class="heat">🔥<span class="heatbar">
  <i style="width:${h}%;background:${heatColor(h)}"></i></span>
  <span style="color:${heatColor(h)};font:11px var(--mono)">${h}</span></span>`}

function chips(){
  const groups=[["src","all","Mọi nguồn","var(--text)"],
    ...Object.entries(SRC).map(([k,v])=>["src",k,v[2]+" "+v[0],v[1]]),
    ...Object.entries(SEN).map(([k,v])=>["sen",k,v[0],v[1]]),
    ...Object.entries(VER).map(([k,v])=>["ver",k,v[0],v[1]])];
  document.getElementById("chips").innerHTML=groups.map(([g,k,label,c])=>
    `<button class="chip ${f[g]===k?"on":""}" style="color:${f[g]===k?c:""}"
      onclick="toggle('${g}','${k}')">${label}</button>`).join(" ");
}
function toggle(g,k){f[g]=(f[g]===k&&k!=="all")?"all":k;render()}

function pass(it){
  if(f.src!=="all"&&it.source_type!==f.src)return false;
  if(f.sen!=="all"&&it.sentiment!==f.sen)return false;
  if(f.ver!=="all"&&it.verify!==f.ver)return false;
  if(f.q){const q=f.q.toLowerCase();
    if(!(it.tickers.join(" ")+" "+it.title+" "+it.snippet).toLowerCase().includes(q))
      return false;}
  return true;
}

function render(){
  chips();
  const list=ITEMS.filter(pass);
  // stats
  const uv=list.filter(i=>i.verify==="unverified").length;
  const hot=list.reduce((a,b)=>b.heat>(a?a.heat:0)?b:a,null);
  document.getElementById("stats").innerHTML=[
    ["Tin hiển thị",list.length,"var(--text)"],
    ["Công ty",new Set(list.flatMap(i=>i.tickers)).size,"var(--cyan)"],
    ["Chưa kiểm chứng",uv,"var(--amber)"],
    ["Nóng nhất",hot?hot.tickers[0]+" · "+hot.heat:"—","var(--red)"],
  ].map(([l,v,c])=>`<div class="stat"><div class="l">${l}</div>
    <div class="v" style="color:${c}">${v}</div></div>`).join("");
  // top tickers
  const m={};ITEMS.forEach(i=>i.tickers.forEach(t=>{
    m[t]=m[t]||{c:0,h:0};m[t].c++;m[t].h=Math.max(m[t].h,i.heat);}));
  const top=Object.entries(m).sort((a,b)=>b[1].h-a[1].h).slice(0,8);
  document.getElementById("top").innerHTML=top.map(([t,v])=>
    `<div class="srow"><span class="t" onclick="f.q=f.q==='${t}'?'':'${t}';
      document.getElementById('q').value=f.q;render()">${t}
      <span style="color:var(--muted);font-weight:400">·${v.c}</span></span>
      ${heatHtml(v.h)}</div>`).join("");
  document.getElementById("tape").innerHTML=[...top,...top].map(([t,v])=>
    `<span style="color:${heatColor(v.h)}">▮ ${t} · ${v.c} tin · nhiệt ${v.h}</span>`).join("");
  // feed nhóm theo ngày
  let html="",lastDay="";
  if(!list.length)html=`<div class="empty">Không có tin khớp bộ lọc.</div>`;
  list.forEach(it=>{
    const d=new Date(it.published);
    const day=d.toLocaleDateString("vi-VN",{weekday:"long",day:"2-digit",month:"2-digit"});
    if(day!==lastDay){html+=`<div class="day">${day}</div>`;lastDay=day;}
    const hhmm=d.toLocaleTimeString("vi-VN",{hour:"2-digit",minute:"2-digit"});
    const s=SRC[it.source_type]||SRC.press,v=VER[it.verify]||VER.unverified,
          se=SEN[it.sentiment]||SEN.neutral;
    let host="";try{host=new URL(it.link).hostname.replace("www.","")}catch(e){}
    html+=`<div class="card" style="border-left:3px solid ${se[1]}">
      <div class="row1">${it.tickers.map(t=>`<span class="tk">${t}</span>`).join("")}
        <span style="margin-left:auto;display:flex;gap:6px">
          <span class="tag" style="color:${v[1]};border-color:${v[1]}55;background:${v[1].replace(')','')!==v[1]?'':''}">${v[0]}</span>
          <span class="tag" style="color:${se[1]};border-color:${se[1]}55">${se[0]}</span>
        </span></div>
      <div class="title"><a href="${it.link}" target="_blank" rel="noopener">${it.title}</a></div>
      ${it.snippet?`<div class="snip">${it.snippet}</div>`:""}
      <div class="meta">
        <span style="color:${s[1]}">${s[2]} ${s[0]} · ${it.source_name}</span>
        <span>🕐 ${hhmm}</span>
        <span class="link"><a href="${it.link}" target="_blank" rel="noopener">↗ ${host||"mở bài gốc"}</a></span>
        <span style="margin-left:auto">${heatHtml(it.heat)}</span>
      </div></div>`;
  });
  document.getElementById("feed").innerHTML=html;
}
document.getElementById("q").addEventListener("input",e=>{f.q=e.target.value;render()});
render();
</script>
</body>
</html>"""


def build():
    with open(DATA_FILE, encoding="utf-8") as f:
        items = json.load(f)
    updated = datetime.now(VN_TZ).strftime("%H:%M %d/%m/%Y")
    html = (TEMPLATE
            .replace("__ITEMS_JSON__", json.dumps(items, ensure_ascii=False))
            .replace("__UPDATED__", updated)
            .replace("__TOTAL__", str(len(items)))
            .replace("__DAYS__", "14"))
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Đã sinh dashboard: {OUT_FILE} ({len(items)} tin)")


if __name__ == "__main__":
    build()
