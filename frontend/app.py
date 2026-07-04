import html
import os
from datetime import datetime

import requests
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

API = os.getenv("BACKEND_URL", "http://localhost:8000")
CATEGORIES = ["Festival", "Recipe", "Farming Practice", "Local History", "Language Phrase", "Craft", "Story", "Ritual", "Education Tradition"]
EXAMPLES = [
    "How was Dashain celebrated in the village?",
    "What foods were prepared during festivals?",
    "What farming practices were used in the past?",
    "Which memories mention community gatherings?",
]

st.set_page_config(page_title="Heritage Memory", page_icon="🏔️", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
:root{--wine:#7b3044;--clay:#b85d3f;--forest:#29483d;--gold:#d59a45;--paper:#fffaf1;--ink:#26372f}
.stApp{background:radial-gradient(circle at 8% 5%,#f9e6cc 0,transparent 25%),linear-gradient(145deg,#fffaf2,#f2eadc 58%,#e6eee8);color:var(--ink)}
.block-container{max-width:1220px;padding-top:1.8rem;padding-bottom:4rem}
.hero{position:relative;overflow:hidden;padding:3.2rem 3rem;border-radius:28px;color:white;background:linear-gradient(125deg,#67283b 0%,#a84e3b 62%,#cf8747 100%);box-shadow:0 20px 48px #5b302338;margin-bottom:1.6rem}
.hero:after{content:'✦';position:absolute;right:5%;top:-35%;font-size:14rem;opacity:.07}.eyebrow{letter-spacing:.14em;text-transform:uppercase;font-size:.76rem;font-weight:700;opacity:.8}
.hero h1{font-family:Georgia,serif;font-size:3.6rem;margin:.3rem 0}.hero .tagline{font-size:1.28rem;margin:.2rem 0 1rem}.hero .problem{max-width:760px;line-height:1.65;opacity:.9}
.section-title{font-family:Georgia,serif;font-size:1.75rem;margin:1.5rem 0 .25rem;color:#552b35}.section-copy{color:#63716b;margin-bottom:1.2rem}
.value-grid,.life-grid,.metric-grid,.status-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1rem 0 2rem}.value-card,.life-card,.memory-card,.answer-card,.context-card,.metric-card,.status-card{background:#fffdf8;border:1px solid #eadfce;border-radius:18px;padding:1.25rem;box-shadow:0 7px 22px #49372a12}
.value-card .icon{font-size:1.5rem}.value-card h3,.life-card h3{font-family:Georgia,serif;margin:.55rem 0 .35rem;color:#633142}.value-card p,.life-card p{font-size:.92rem;line-height:1.5;color:#64706b}
.life-grid{grid-template-columns:repeat(4,1fr);position:relative}.life-card{border-top:4px solid var(--clay)}.life-num{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;background:#f2dfc7;color:#733547;font-weight:700}
.metric-grid{grid-template-columns:repeat(5,1fr);margin-bottom:1rem}.metric-card{text-align:center;padding:1rem .5rem}.metric-number{font-family:Georgia,serif;font-size:2rem;color:#713448;font-weight:700}.metric-label{font-size:.78rem;color:#737e78;margin-top:.15rem}
.insight-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:2rem}.insight{background:linear-gradient(145deg,#2b493f,#3d6556);color:#fff;border-radius:17px;padding:1.2rem;box-shadow:0 8px 24px #29483d2c}.insight small{opacity:.7;text-transform:uppercase;letter-spacing:.08em}.insight strong{display:block;font-family:Georgia,serif;font-size:1.2rem;margin-top:.4rem}
.compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1rem 0 2rem}.compare{border-radius:18px;padding:1.35rem}.compare.normal{background:#f3eee7;border:1px solid #ded4c8}.compare.memory{background:#e9f0eb;border:1px solid #cdded2}.compare h3{font-family:Georgia,serif;margin-top:0}.compare ul{padding-left:1.2rem;line-height:1.8}
.status-grid{grid-template-columns:repeat(3,1fr);margin-bottom:2rem}.status-card{padding:1rem}.status-dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:#4d916a;margin-right:.45rem;box-shadow:0 0 0 4px #4d916a20}.status-card b{display:block;margin-bottom:.3rem}.status-card span{font-size:.83rem;color:#758079}
.status-dot.fallback{background:#d09842;box-shadow:0 0 0 4px #d0984220}.status-dot.offline{background:#b85248;box-shadow:0 0 0 4px #b8524820}
.architecture-flow{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:.45rem;background:#253f36;color:#fff;border-radius:20px;padding:1.5rem;margin:1rem 0 2rem}.arch-node{background:#345b4d;border:1px solid #527766;border-radius:12px;padding:.75rem .9rem;font-size:.84rem;text-align:center}.arch-node.cognee{background:#884253;border-color:#b06b79}.arch-arrow{color:#d7ad6a;font-size:1.1rem}
.memory-card{margin:.8rem 0;border-left:5px solid var(--clay)}.memory-card h4{font-family:Georgia,serif;margin:0;color:#5d3040}.meta{color:#78827d;font-size:.82rem;margin:.3rem 0 .65rem}.pill{display:inline-block;background:#f0e5d5;color:#684353;border-radius:99px;padding:.2rem .55rem;font-size:.75rem;margin:.12rem}
.answer-card{border:1px solid #decba9;background:linear-gradient(135deg,#fffdf8,#f8efdf);padding:1.6rem}.answer-label{color:#934b3e;font-size:.76rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
.context-card{background:#eef3ef;border-color:#d6e1da}.empty{padding:2.2rem;text-align:center;border:1px dashed #cdbfae;border-radius:18px;color:#748079}
.before{border-left:5px solid #8a8278}.after{border-left:5px solid #4f7c64}.improvement{padding:1rem;border-radius:14px;background:#f7ead5;border:1px solid #ead3ae}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#233f36,#315347)}[data-testid="stSidebar"] *{color:#fff}
[data-testid="stForm"]{background:#fffdf8;border:1px solid #e7dac8;padding:1.4rem;border-radius:20px}
div[data-baseweb="tab-list"]{position:sticky;top:3.4rem;z-index:900;display:flex;flex-wrap:wrap;gap:.35rem;background:#fffaf1f2;border:1px solid #e4d5c2;border-radius:16px;padding:.45rem .55rem;box-shadow:0 7px 22px #49372a18;backdrop-filter:blur(10px)}
button[data-baseweb="tab"]{color:#58333d!important;background:#f3e8d8!important;border-radius:10px!important;padding:.55rem .85rem!important;font-weight:700!important}
button[data-baseweb="tab"]:hover{background:#ead6bd!important;color:#702f43!important}
button[data-baseweb="tab"][aria-selected="true"]{background:#7b3044!important;color:white!important;box-shadow:0 4px 12px #7b304433}
button[data-baseweb="tab"] p{color:inherit!important;font-size:.88rem!important}
.quick-ask{background:linear-gradient(135deg,#263f37,#3b6455);color:#fff;border-radius:22px;padding:1.4rem 1.6rem;margin:1rem 0 1.4rem}.quick-ask h2{font-family:Georgia,serif;margin:0 0 .35rem}.quick-ask p{opacity:.82;margin:0}
@media(max-width:800px){.value-grid,.life-grid,.metric-grid,.insight-grid,.compare-grid,.status-grid{grid-template-columns:1fr}.hero{padding:2rem}.hero h1{font-size:2.6rem}}
</style>
""", unsafe_allow_html=True)


def api(method: str, path: str, quiet: bool = False, **kwargs):
    try:
        response = requests.request(method, f"{API}{path}", timeout=90, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        if not quiet:
            st.error(f"The memory archive is unavailable: {exc}")
        return None


def esc(value) -> str:
    return html.escape(str(value))


def format_date(value: str) -> str:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d %b %Y")
    except (TypeError, ValueError):
        return "Date unknown"


def memory_card(memory: dict, compact: bool = False) -> str:
    text = memory["memory_text"]
    if compact and len(text) > 220:
        text = text[:217].rsplit(" ", 1)[0] + "…"
    pills = "".join(f'<span class="pill">{esc(tag)}</span>' for tag in memory.get("tags", []))
    date_label = f'Added {format_date(memory["created_at"])}' if memory.get("created_at") else "Demo preview"
    return f'''<div class="memory-card"><h4>{esc(memory["elder_name"])}</h4>
    <div class="meta">{esc(memory["location"])} · {esc(memory["category"])} · {date_label}</div>
    <p>{esc(text)}</p><div>{pills}</div></div>'''


def archive() -> list[dict]:
    return api("GET", "/memory", quiet=True) or []


def load_demo():
    result = api("POST", "/demo/reset-sample-data")
    if result:
        st.toast(f"Demo reset · {result['loaded']} sample memories · {result['total']} total")
        st.rerun()


with st.sidebar:
    st.markdown("## Heritage Memory")
    st.caption("A living archive of people, places, and wisdom.")
    health = api("GET", "/health", quiet=True)
    if health:
        st.success("Archive connected")
        st.caption(f"Memory · {health['memory_mode']}  \nAnswers · {health['llm_mode']}  \nSearch · {health['embedding_mode']}")
    else:
        st.warning("Start the FastAPI backend on port 8000.")
    st.divider()
    if st.button("Reset / load Nepal demo", type="primary", use_container_width=True):
        load_demo()
    st.caption("Built around continuing consent: knowledge can be corrected or withdrawn at any time.")

home, remember, recall, graph_tab, timeline, improve, forget, demo = st.tabs([
    "Home", "Remember", "Recall", "Memory Graph", "Timeline", "Improve", "Forget", "Demo Archive"
])

with home:
    st.markdown('''<section class="hero"><div class="eyebrow">A living cultural archive</div><h1>Heritage Memory</h1>
    <div class="tagline">Preserving oral culture with persistent AI memory</div>
    <div class="problem">When an elder’s voice is lost, a community can lose recipes, rituals, language, local history, and ways of reading the land. Heritage Memory helps that wisdom remain attributable, connected, correctable, and available to future generations.</div></section>''', unsafe_allow_html=True)
    st.markdown('<div class="quick-ask"><h2>Ask the archive now</h2><p>Try the core experience immediately. Every answer is grounded in preserved memories and shows its sources.</p></div>', unsafe_allow_html=True)
    quick_cols = st.columns(2)
    for index, example in enumerate(EXAMPLES[:2]):
        if quick_cols[index].button(example, key=f"home_example_{index}", use_container_width=True):
            st.session_state.home_question = example
    home_question = st.text_input(
        "Ask a cultural question",
        key="home_question",
        placeholder="For example: How was Dashain celebrated in the village?",
    )
    if st.button("Ask Heritage Memory", type="primary", disabled=not home_question, key="home_ask"):
        with st.spinner("Recalling connected cultural memories…"):
            st.session_state.home_answer = api(
                "POST", "/memory/recall", json={"question": home_question, "limit": 4}
            )
    home_answer = st.session_state.get("home_answer")
    if home_answer:
        st.markdown(f'<div class="answer-card"><div class="answer-label">Answer from persistent memory</div><p>{esc(home_answer["answer"])}</p></div>', unsafe_allow_html=True)
        if home_answer["memories"]:
            with st.expander(f'See {len(home_answer["memories"])} source memories used', expanded=True):
                for source in home_answer["memories"]:
                    st.markdown(memory_card(source, compact=True), unsafe_allow_html=True)
        else:
            st.info("No related memory was found yet. Reset/load the Nepal demo from the sidebar, then ask again.")
    st.markdown('''<div class="value-grid">
    <div class="value-card"><div class="icon">◉</div><h3>Remember oral stories</h3><p>Preserve an elder’s account with its person, place, meaning, and cultural context.</p></div>
    <div class="value-card"><div class="icon">⌕</div><h3>Recall cultural knowledge</h3><p>Ask natural questions and receive grounded answers linked to remembered sources.</p></div>
    <div class="value-card"><div class="icon">✦</div><h3>Carry heritage forward</h3><p>Build a living archive that can grow through correction while respecting consent.</p></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Memory has a lifecycle</div><div class="section-copy">Persistent memory is useful because knowledge survives the conversation—and remains governable afterward.</div>', unsafe_allow_html=True)
    st.markdown('''<div class="life-grid">
    <div class="life-card"><span class="life-num">1</span><h3>Remember</h3><p>Capture an attributed oral memory and preserve it beyond this session.</p></div>
    <div class="life-card"><span class="life-num">2</span><h3>Recall</h3><p>Retrieve related knowledge and answer only from remembered context.</p></div>
    <div class="life-card"><span class="life-num">3</span><h3>Improve</h3><p>Add corrections and details while retaining the earlier account.</p></div>
    <div class="life-card"><span class="life-num">4</span><h3>Forget</h3><p>Withdraw knowledge when privacy, consent, or sensitivity requires it.</p></div></div>''', unsafe_allow_html=True)
    home_memories = archive()
    elder_count = len({item["elder_name"] for item in home_memories})
    location_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    tag_counts: dict[str, int] = {}
    for item in home_memories:
        location_counts[item["location"]] = location_counts.get(item["location"], 0) + 1
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1
        for tag in item.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    top_location = max(location_counts, key=location_counts.get) if location_counts else "Waiting for memories"
    top_tag = max(tag_counts, key=tag_counts.get) if tag_counts else "Waiting for connections"
    top_categories = sorted(category_counts.items(), key=lambda pair: (-pair[1], pair[0]))[:3]
    category_summary = ", ".join(f"{name} ({count})" for name, count in top_categories) or "Waiting for memories"
    st.markdown('<div class="section-title">Memory Intelligence</div><div class="section-copy">A live view of what the persistent archive knows—and how its cultural relationships are growing.</div>', unsafe_allow_html=True)
    st.markdown(f'''<div class="metric-grid">
    <div class="metric-card"><div class="metric-number">{len(home_memories)}</div><div class="metric-label">Total memories</div></div>
    <div class="metric-card"><div class="metric-number">{elder_count}</div><div class="metric-label">Elders represented</div></div>
    <div class="metric-card"><div class="metric-number">{len(location_counts)}</div><div class="metric-label">Locations represented</div></div>
    <div class="metric-card"><div class="metric-number">{len(category_counts)}</div><div class="metric-label">Categories represented</div></div>
    <div class="metric-card"><div class="metric-number">{len(tag_counts)}</div><div class="metric-label">Tags connected</div></div></div>''', unsafe_allow_html=True)
    st.markdown(f'''<div class="insight-grid">
    <div class="insight"><small>Most connected tag</small><strong>#{esc(top_tag)}</strong></div>
    <div class="insight"><small>Most mentioned location</small><strong>{esc(top_location)}</strong></div>
    <div class="insight"><small>Leading categories</small><strong>{esc(category_summary)}</strong></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Why Cognee matters</div>', unsafe_allow_html=True)
    st.markdown('''<div class="compare-grid">
    <div class="compare normal"><h3>Normal chatbot</h3><ul><li>Context disappears after the session</li><li>Stories remain isolated in a conversation</li><li>No durable cultural relationships</li><li>No governed memory lifecycle</li></ul></div>
    <div class="compare memory"><h3>Heritage Memory + Cognee</h3><ul><li>Remembers attributed stories across sessions</li><li>Connects people, places, traditions, and tags</li><li>Improves as elders add detail or correction</li><li>Supports forgetting for privacy and consent</li></ul></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Memory architecture</div><div class="section-copy">Each contribution moves through a persistent intelligence layer before it becomes a grounded answer.</div>', unsafe_allow_html=True)
    st.markdown('''<div class="architecture-flow">
    <div class="arch-node">Oral Memory</div><div class="arch-arrow">→</div>
    <div class="arch-node cognee">Cognee<br>Remember</div><div class="arch-arrow">→</div>
    <div class="arch-node">Graph + Vector<br>Memory</div><div class="arch-arrow">→</div>
    <div class="arch-node cognee">Recall</div><div class="arch-arrow">→</div>
    <div class="arch-node">Gemini<br>Answer</div><div class="arch-arrow">→</div>
    <div class="arch-node">Improve / Forget</div></div>''', unsafe_allow_html=True)
    memory_status = health["memory_mode"] if health else "offline"
    gemini_status = health["llm_mode"] if health else "offline"
    embedding_status = health["embedding_mode"] if health else "offline"
    memory_class = "" if "cognee" in memory_status else ("offline" if memory_status == "offline" else "fallback")
    gemini_class = "" if gemini_status == "gemini" else ("offline" if gemini_status == "offline" else "fallback")
    embedding_class = "" if embedding_status == "huggingface" else ("offline" if embedding_status == "offline" else "fallback")
    st.markdown('<div class="section-title">API and intelligence status</div>', unsafe_allow_html=True)
    st.markdown(f'''<div class="status-grid">
    <div class="status-card"><b><i class="status-dot {memory_class}"></i>Cognee memory</b><span>{esc(memory_status)} · persistent JSON fallback remains available</span></div>
    <div class="status-card"><b><i class="status-dot {gemini_class}"></i>Gemini answers</b><span>{esc(gemini_status)} · grounded mock answers activate without a key</span></div>
    <div class="status-card"><b><i class="status-dot {embedding_class}"></i>Embedding model</b><span>{esc(embedding_status)} · multilingual semantic retrieval with lexical fallback</span></div></div>''', unsafe_allow_html=True)
    left, right = st.columns([1, 2])
    if left.button("Explore the Nepal demo", type="primary", use_container_width=True):
        load_demo()
    right.info("Demo path: load memories → ask about Dashain → explore the graph → improve an account → explain consent-aware forgetting.")

with remember:
    st.markdown('<div class="section-title">Sit with a memory</div><div class="section-copy">Record the story with enough context that another generation can understand who shared it and where it belongs.</div>', unsafe_allow_html=True)
    with st.form("remember_form"):
        st.markdown("#### Who shared this memory?")
        elder = st.text_input("Elder or storyteller", placeholder="Aama Dhan Maya Gurung", label_visibility="collapsed")
        st.markdown("#### Where is it from?")
        location = st.text_input("Place", placeholder="Lamjung, Nepal", label_visibility="collapsed")
        st.markdown("#### What type of heritage is it?")
        category = st.selectbox("Category", CATEGORIES, label_visibility="collapsed")
        st.markdown("#### What did they share?")
        text = st.text_area("Memory", placeholder="Write the account in their words, with the details they want remembered…", height=180, label_visibility="collapsed")
        st.markdown("#### Tags")
        tags = st.text_input("Tags", placeholder="Dashain, tika, jamara, family", label_visibility="collapsed")
        submitted = st.form_submit_button("Preserve this memory", type="primary")
    if submitted:
        result = api("POST", "/memory/remember", json={"elder_name": elder, "location": location, "category": category, "memory_text": text, "tags": [tag.strip() for tag in tags.split(",") if tag.strip()]})
        if result:
            st.success("This memory is now part of the living archive.")
            st.markdown(memory_card(result), unsafe_allow_html=True)

with recall:
    st.markdown('<div class="section-title">Ask the living archive</div><div class="section-copy">Answers are generated only from memories the community has preserved.</div>', unsafe_allow_html=True)
    st.caption("Try an example")
    cols = st.columns(2)
    for index, example in enumerate(EXAMPLES):
        if cols[index % 2].button(example, key=f"example_{index}", use_container_width=True):
            st.session_state.recall_question = example
    question = st.text_input("Question", key="recall_question", placeholder="What would you like to learn from the archive?")
    if st.button("Recall cultural knowledge", type="primary", disabled=not question):
        with st.spinner("Listening across remembered voices…"):
            result = api("POST", "/memory/recall", json={"question": question, "limit": 5})
        if result:
            st.session_state.last_recall = result
    result = st.session_state.get("last_recall")
    if result:
        st.markdown(f'<div class="answer-card"><div class="answer-label">Grounded AI answer</div><p>{esc(result["answer"])}</p></div>', unsafe_allow_html=True)
        memories = result["memories"]
        if memories:
            people = sorted({m["elder_name"] for m in memories}); places = sorted({m["location"] for m in memories}); tags_used = sorted({tag for m in memories for tag in m["tags"]})
            st.markdown(f'<div class="context-card"><b>Source context</b><br>{len(memories)} remembered source(s) · People: {esc(", ".join(people))} · Places: {esc(", ".join(places))}<br><span class="meta">Connected tags: {esc(", ".join(tags_used))}</span></div>', unsafe_allow_html=True)
            st.caption("Confidence comes from source coverage, not an invented percentage. Inspect every memory used below.")
            with st.expander("Related memories used", expanded=True):
                for item in memories:
                    st.markdown(memory_card(item), unsafe_allow_html=True)

with graph_tab:
    st.markdown('<div class="section-title">The cultural memory graph</div><div class="section-copy">Follow how a voice connects to a place, a form of heritage, a remembered account, and the ideas carried within it.</div>', unsafe_allow_html=True)
    st.markdown("**Person → Place → Category → Memory → Tags**")
    graph = api("GET", "/memory/graph", quiet=True)
    if graph and graph["nodes"]:
        colors = {"person":"#7b3044","place":"#397060","category":"#d08a3d","memory":"#769064","tag":"#8a6ca8"}
        try:
            net = Network(height="680px", width="100%", bgcolor="#fffaf1", font_color="#26372f", directed=True)
            for node in graph["nodes"]:
                size = {"person":25,"place":22,"category":20,"memory":16,"tag":12}[node["type"]]
                net.add_node(node["id"], label=node["label"], color=colors[node["type"]], title=node["type"].title(), size=size)
            for edge in graph["edges"]:
                net.add_edge(edge["source"], edge["target"], title=edge["label"], color="#b6a896")
            net.set_options('{"physics":{"barnesHut":{"gravitationalConstant":-6200,"springLength":155,"springConstant":0.035},"stabilization":{"iterations":180}},"interaction":{"hover":true,"navigationButtons":true},"edges":{"smooth":{"type":"continuous"},"arrows":{"to":{"enabled":true,"scaleFactor":0.35}}}}')
            components.html(net.generate_html(), height=700)
        except Exception:
            st.warning("Interactive view unavailable; showing relationships as a table.")
            st.dataframe(graph["edges"], use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="empty">The graph will grow as memories are preserved. Load the Nepal demo archive to see it come alive.</div>', unsafe_allow_html=True)

with timeline:
    st.markdown('<div class="section-title">Memory timeline</div><div class="section-copy">The archive in the order it was entrusted to Heritage Memory.</div>', unsafe_allow_html=True)
    memories = sorted(archive(), key=lambda item: item.get("created_at", ""), reverse=True)
    if memories:
        st.metric("Memories preserved", len(memories))
        for item in memories:
            st.markdown(memory_card(item, compact=True), unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty">No memories have been preserved yet.</div>', unsafe_allow_html=True)

with improve:
    st.markdown('<div class="section-title">Knowledge can grow</div><div class="section-copy">Add a correction or detail and see the lifecycle happen clearly. The earlier account remains in revision history.</div>', unsafe_allow_html=True)
    memories = archive()
    by_id = {m["memory_id"]: m for m in memories}
    selected = st.selectbox("Choose a memory", list(by_id), format_func=lambda key: f'{by_id[key]["elder_name"]} — {by_id[key]["memory_text"][:75]}…') if by_id else None
    detail = st.text_area("What detail or correction should be added?", placeholder="Jamara was grown at home several days before Dashain.")
    correction = st.checkbox("Replace the current account instead of appending this detail")
    if st.button("Improve this memory", type="primary", disabled=not (selected and detail)):
        before = by_id[selected]
        updated = api("POST", "/memory/improve", json={"memory_id": selected, "additional_detail": detail, "correction": correction})
        if updated:
            st.session_state.improve_proof = {"before": before, "detail": detail, "after": updated}
            st.success("Memory improved. Its previous version remains preserved.")
    proof = st.session_state.get("improve_proof")
    if proof:
        before_col, after_col = st.columns(2)
        with before_col:
            st.markdown("#### Before memory")
            st.markdown(f'<div class="memory-card before"><p>{esc(proof["before"]["memory_text"])}</p></div>', unsafe_allow_html=True)
        with after_col:
            st.markdown("#### Updated memory")
            st.markdown(f'<div class="memory-card after"><p>{esc(proof["after"]["memory_text"])}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="improvement"><b>Improvement added</b><br>{esc(proof["detail"])}</div>', unsafe_allow_html=True)

with forget:
    st.markdown('<div class="section-title">The right to be forgotten</div><div class="section-copy">Forgetting is essential for privacy, continuing consent, and cultural sensitivity. Not every memory should remain public forever, and communities must retain the right to withdraw knowledge.</div>', unsafe_allow_html=True)
    memories = archive(); by_id = {m["memory_id"]: m for m in memories}
    selected = st.selectbox("Choose a memory to withdraw", list(by_id), format_func=lambda key: f'{by_id[key]["elder_name"]} — {by_id[key]["category"]}', key="forget_select") if by_id else None
    if selected:
        st.markdown(memory_card(by_id[selected], compact=True), unsafe_allow_html=True)
    confirmed = st.checkbox("I understand this removes the memory from the archive and visible graph")
    if st.button("Forget this memory", disabled=not (selected and confirmed)):
        if api("DELETE", f"/memory/forget/{selected}"):
            st.success("The community’s decision has been respected. This memory was forgotten.")
            st.rerun()

with demo:
    st.markdown('<div class="section-title">Nepal heritage demo archive</div><div class="section-copy">Eight vivid accounts show how festivals, food, land, language, learning, and craft become connected persistent memory.</div>', unsafe_allow_html=True)
    if st.button("Reset to the eight demo memories", type="primary", key="demo_load"):
        load_demo()
    samples = api("GET", "/demo/sample-memories", quiet=True) or []
    for sample in samples:
        st.markdown(memory_card(sample, compact=True), unsafe_allow_html=True)
