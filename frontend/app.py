import html, json, os
from datetime import datetime
from pathlib import Path
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

LOGO_PATH=Path(__file__).resolve().parent/"assets"/"heritage-memory-logo.png"
st.set_page_config(page_title="Heritage Memory", page_icon=Image.open(LOGO_PATH), layout="wide")
API=os.getenv("BACKEND_URL","http://localhost:8000").rstrip("/")
CATEGORIES=["Festival","Recipe","Farming Practice","Local History","Language Phrase","Craft","Story","Ritual","Education Tradition"]
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=Playfair+Display:wght@600;700&display=swap');
:root{--ink:#2b2118;--rust:#a64b32;--gold:#d8a446;--muted:#75685d}.stApp{background:linear-gradient(145deg,#fbf7ee,#f5ecdc);color:var(--ink);font-family:'DM Sans',sans-serif}
h1,h2,h3{font-family:'Playfair Display',serif!important;color:var(--ink)!important}.block-container{padding-top:2rem;max-width:1250px}[data-testid="stSidebar"]{background:#28251f}[data-testid="stSidebar"] *{color:#f8edda!important}
.eyebrow{text-transform:uppercase;letter-spacing:.18em;color:var(--rust);font-size:.72rem;font-weight:700}.hero{padding:3.7rem 3.5rem;border-radius:24px;background:linear-gradient(105deg,#1f221bf5,#53442de0);color:#fff;box-shadow:0 18px 50px #69492b2b;margin-bottom:2rem}.hero h1{font-size:4rem!important;color:#fff!important;margin:.25rem 0}.hero p{font-size:1.25rem;color:#eee0c9}
.card{height:100%;padding:1.5rem;border:1px solid #e6d7c1;border-radius:16px;background:#fffaf1;box-shadow:0 7px 20px #50361a0c}.soft{color:var(--muted)}.pill{display:inline-block;padding:.3rem .65rem;background:#eee2cc;border-radius:20px;margin:.15rem;font-size:.8rem}.flow{padding:1.1rem;text-align:center;border-radius:14px;background:#322e27;color:#f3dcae;font-weight:600}.answer{border-left:5px solid var(--gold);padding:1.5rem;background:#fff;border-radius:4px 16px 16px 4px;font-size:1.08rem}.memory{padding:1.15rem 1.3rem;margin:.6rem 0;border-radius:14px;background:#fffaf3;border:1px solid #eadcc7}.consent{padding:1rem 1.2rem;background:#f1e7d7;border-radius:12px;border-left:4px solid #8d6147}.stButton>button{border-radius:10px;font-weight:600;border:none;background:#a64b32;color:white;padding:.6rem 1.1rem}
</style>""",unsafe_allow_html=True)

def api(method,path,**kwargs):
    try:
        r=requests.request(method,API+path,timeout=90,**kwargs);r.raise_for_status();return r.json()
    except requests.RequestException:
        st.error(f"The archive service is not reachable at {API}. Start the backend and try again.");return None
def title(k,h,c): st.markdown(f'<div class="eyebrow">{k}</div><h1>{h}</h1><p class="soft">{c}</p>',unsafe_allow_html=True)
def label(m): return f"{m['elder_name']} · {m['category']} · {m['summary'][:55]}"
def graph(data):
    p=json.dumps(data).replace("</","<\\/")
    doc=f"""<!doctype html><html><head><script src="https://unpkg.com/vis-network@9.1.9/dist/vis-network.min.js"></script><style>html,body,#g{{width:100%;height:100%;margin:0;background:radial-gradient(circle,#fffaf0,#efe3cf);font-family:Arial}}#l{{position:absolute;z-index:2;left:18px;top:18px;background:#ffffffdd;padding:12px;border-radius:12px}}</style></head><body><div id="l"><b>Living memory graph</b><br>🟠 Elder　🟢 Place　🔴 Category<br>🟡 Memory　🔵 Tag</div><div id="g"></div><script>const d={p};new vis.Network(document.getElementById('g'),{{nodes:new vis.DataSet(d.nodes),edges:new vis.DataSet(d.edges)}},{{interaction:{{hover:true}},nodes:{{shape:'dot',font:{{color:'#30271f',size:13}}}},edges:{{color:'#b9a98e',smooth:true}},physics:{{barnesHut:{{gravitationalConstant:-3800,springLength:120}}}}}});</script></body></html>"""
    components.html(doc,height=650)

with st.sidebar:
    st.image(str(LOGO_PATH),use_container_width=True)
    st.caption("A living archive for oral culture")
    page=st.radio("Explore",["Home","Remember","Recall","Memory Graph","Timeline","Improve","Forget","Insights","Demo Dataset"],label_visibility="collapsed")
    st.divider();status=api("GET","/status")
    if status:
        st.caption("SYSTEM STATUS");st.write("● Memory layer","Cognee" if status["cognee"]["operational"] else "Local fallback");st.write("● Gemini",status["gemini"]["status"]);st.write("● Embeddings",status["embeddings"]["status"])

if page=="Home":
    brand,hero=st.columns([1,2.25],vertical_alignment="center")
    with brand:
        st.image(str(LOGO_PATH),use_container_width=True)
    with hero:
        st.markdown('<section class="hero"><div class="eyebrow" style="color:#e8b967">A living archive for communities</div><h1>Heritage Memory</h1><p>Preserving oral culture with persistent AI memory.</p></section>',unsafe_allow_html=True)
    st.markdown("### What disappears when a voice is not remembered?");st.write("Every community carries knowledge through elders. When those stories are not documented, traditions, recipes, local history, and lived experiences can disappear.")
    cols=st.columns(3)
    for col,num,head,body in zip(cols,["01","02","03"],["Remember oral stories","Recall cultural knowledge","Preserve what connects us"],["Capture a memory with its person, place, and cultural context.","Ask natural questions and receive answers grounded only in the archive.","Let future generations discover a connected, evolving cultural record."]): col.markdown(f'<div class="card"><div class="eyebrow">{num}</div><h3>{head}</h3><p class="soft">{body}</p></div>',unsafe_allow_html=True)
    st.markdown("### Memory is a lifecycle");st.markdown('<div class="flow">REMEMBER &nbsp; → &nbsp; RECALL &nbsp; → &nbsp; IMPROVE &nbsp; → &nbsp; FORGET</div>',unsafe_allow_html=True)
    st.markdown("### Built around persistent memory");st.markdown('<div class="flow" style="background:#f1e4cf;color:#473629">Oral Memory → Cognee Memory → Graph + Vector Recall → Gemini Answer → Improve / Forget</div>',unsafe_allow_html=True)
elif page=="Remember":
    title("Remember","Preserve a voice","Record the story as it was shared. Context gives a memory its roots.")
    with st.form("remember"):
        a,b=st.columns(2);elder=a.text_input("Who shared this memory?",placeholder="e.g. Aama Maya Gurung");location=b.text_input("Where is this memory from?",placeholder="Village, district or region")
        category=st.selectbox("What type of heritage is it?",CATEGORIES);text=st.text_area("What did they share?",height=210,placeholder="Capture their words, details, feelings, and context…");tags=st.text_input("Tags",placeholder="dashain, family, food");consent=st.checkbox("The storyteller has consented to preserve this memory.");submitted=st.form_submit_button("Preserve this memory →",disabled=not consent)
    if submitted:
        r=api("POST","/memory/remember",json={"elder_name":elder,"location":location,"category":category,"memory_text":text,"tags":[t.strip() for t in tags.split(",") if t.strip()]})
        if r: st.success("This memory is now preserved.");st.markdown(f'<div class="card"><div class="eyebrow">Generated summary</div><h3>{html.escape(r["summary"])}</h3><p>Connected to <b>{html.escape(elder)}</b> · <b>{html.escape(location)}</b> · <b>{category}</b></p></div>',unsafe_allow_html=True)
elif page=="Recall":
    title("Recall","Ask the living archive","Answers are assembled only from preserved memories—never from outside assumptions.")
    st.caption("TRY: How was Dashain celebrated? · What foods were prepared? · What did elders teach children?")
    q=st.text_input("Your question",placeholder="What do you want to remember?",label_visibility="collapsed")
    if st.button("Recall from memory →") and q:
        r=api("POST","/memory/recall",json={"query":q,"limit":4})
        if r:
            st.markdown(f'<div class="answer"><div class="eyebrow">Grounded answer</div><br>{html.escape(r["answer"])}</div>',unsafe_allow_html=True)
            if r["grounded"]:
                st.markdown("### Memory threads used");x,y,z=st.columns(3);x.write("**Elders**",*r["connected_elders"]);y.write("**Places**",*r["connected_locations"]);z.write("**Tags**",*["#"+t for t in r["connected_tags"]])
                with st.expander(f"View {len(r['related_memories'])} source memories"):
                    for m,s in zip(r["related_memories"],r["scores"]): st.markdown(f"**{m['elder_name']} · {m['location']}**  \n{m['memory_text']}  \nRelevance: {s:.2f}")
elif page=="Memory Graph":
    title("Connections","The living memory graph","Every story becomes part of a web of elders, places, traditions, and themes.");d=api("GET","/memory/graph")
    if d and d["nodes"]:
        graph(d)
        with st.expander("Accessible relationship index"):
            labels={node["id"]:node["label"] for node in d["nodes"]}
            rows=[{"From":labels.get(e["from"],e["from"]),"Connected to":labels.get(e["to"],e["to"])} for e in d["edges"]]
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    elif d is not None: st.info("The graph is waiting for its first memory. Load the demo archive to see it bloom.")
elif page=="Timeline":
    title("Timeline","Memories across time","A chronological path through the voices entrusted to the archive.")
    for m in sorted(api("GET","/memory/all") or [],key=lambda x:x["created_at"],reverse=True):
        date=datetime.fromisoformat(m["created_at"].replace("Z","+00:00")).strftime("%d %b %Y");pills="".join(f'<span class="pill">#{html.escape(t)}</span>' for t in m["tags"])
        st.markdown(f'<div class="memory"><div class="eyebrow">{date} · {m["category"]}</div><h3>{html.escape(m["summary"])}</h3><p>{html.escape(m["elder_name"])} · {html.escape(m["location"])}</p>{pills}</div>',unsafe_allow_html=True)
elif page=="Improve":
    title("Improve","Let a memory grow","Add a correction or newly remembered detail without erasing its history.");mem=api("GET","/memory/all") or []
    if mem:
        chosen=st.selectbox("Choose a memory",mem,format_func=label);st.markdown(f'<div class="memory"><div class="eyebrow">Previous memory</div><p>{html.escape(chosen["memory_text"])}</p></div>',unsafe_allow_html=True);detail=st.text_area("New detail or correction",placeholder="Jamara was grown at home before Dashain.")
        if st.button("Improve this memory →") and detail:
            r=api("POST","/memory/improve",json={"memory_id":chosen["memory_id"],"improvement":detail})
            if r: st.success("The archive now carries this added detail.");st.markdown(f'<div class="card"><div class="eyebrow">Updated memory</div><p>{html.escape(r["memory_text"])}</p></div>',unsafe_allow_html=True)
    else: st.info("Preserve or load a memory before improving it.")
elif page=="Forget":
    title("Forget","Respect the right to remove","A trustworthy archive must honor privacy, consent, and cultural sensitivity—not everything should remain forever.");st.markdown('<div class="consent">Forgetting immediately rebuilds recall, graph, and insight views without this memory.</div>',unsafe_allow_html=True);mem=api("GET","/memory/all") or []
    if mem:
        chosen=st.selectbox("Choose a memory to review",mem,format_func=label);st.markdown(f'<div class="memory"><b>{html.escape(chosen["elder_name"])}</b><p>{html.escape(chosen["memory_text"])}</p></div>',unsafe_allow_html=True);ok=st.checkbox("I understand this removes the preserved memory.")
        if st.button("Forget this memory",disabled=not ok) and api("DELETE",f"/memory/forget/{chosen['memory_id']}"): st.success("Memory removed. The graph and insights have been updated.");st.rerun()
    else: st.info("There are no memories to remove.")
elif page=="Insights":
    title("Intelligence","What the archive holds","A community-level view of voices, places, and patterns.");s=api("GET","/memory/insights")
    if s:
        cols=st.columns(5)
        for c,v,l in zip(cols,[s["total_memories"],s["elders_represented"],s["locations_represented"],s["categories_represented"],s["unique_tags"]],["Memories","Elders","Places","Categories","Unique tags"]): c.metric(l,v)
        a,b=st.columns([2,1])
        with a:
            st.markdown("### Cultural knowledge by category")
            if s["category_distribution"]: st.bar_chart(pd.Series(s["category_distribution"]),color="#a64b32")
        with b: st.markdown("### Strongest threads");st.markdown(f'<div class="card"><div class="eyebrow">Most connected tag</div><h3>#{html.escape(s["most_connected_tag"] or "—")}</h3><div class="eyebrow">Most mentioned place</div><h3>{html.escape(s["most_mentioned_location"] or "—")}</h3><div class="eyebrow">Tag connections</div><h3>{s["total_tags"]}</h3></div>',unsafe_allow_html=True)
else:
    title("Demo archive","Eight voices from Nepal","Festivals, food, farming, language, learning, local history, and craft.");samples=api("GET","/demo/sample-memories") or [];st.markdown(f'<div class="consent"><b>{len(samples)} demonstration memories</b> are ready. Loading is idempotent—no duplicates.</div>',unsafe_allow_html=True)
    if st.button("Preserve the Nepal demo archive →"):
        r=api("POST","/demo/load-sample-data")
        if r: st.success(r["message"]+f" The archive now holds {r['total']} memories.")
    for m in samples:
        with st.expander(f"{m['category']} · {m['elder_name']} · {m['location']}"): st.write(m["memory_text"])
