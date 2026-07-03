import os

import requests
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

API = os.getenv("BACKEND_URL", "http://localhost:8000")
CATEGORIES = ["Festival", "Recipe", "Farming Practice", "Local History", "Language Phrase", "Craft", "Story", "Ritual", "Education Tradition"]

st.set_page_config(page_title="Heritage Memory", page_icon="🏔️", layout="wide")
st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#fffaf0,#f3eadc 58%,#e5eee8);color:#293b34}
.hero{padding:2rem 2.4rem;border-radius:24px;color:white;margin-bottom:1rem;background:linear-gradient(120deg,#792d3d,#b45c35);box-shadow:0 12px 35px #6f342533}
.hero h1{margin:0;font-size:2.7rem}.hero p{font-size:1.1rem;margin-bottom:0;opacity:.94}
.card{background:#fffdf8;border-left:5px solid #b75d32;padding:1rem 1.2rem;border-radius:12px;margin:.7rem 0;box-shadow:0 3px 12px #492d1915}
.architecture{background:#293b34;color:#f8f2e7;border-radius:14px;padding:1.2rem;text-align:center;font-family:monospace}
[data-testid="stSidebar"]{background:#293b34}[data-testid="stSidebar"] *{color:#fff}
</style>
<div class="hero"><h1>🏔️ Heritage Memory</h1><p>Preserving oral culture with persistent AI memory.</p></div>
""", unsafe_allow_html=True)


def api(method: str, path: str, **kwargs):
    try:
        response = requests.request(method, f"{API}{path}", timeout=60, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Memory service unavailable: {exc}")
        return None


def memory_options():
    graph = api("GET", "/memory/graph")
    if not graph:
        return {}
    return {node["id"].removeprefix("memory:"): node["label"] for node in graph["nodes"] if node["type"] == "memory"}


def load_demo():
    result = api("POST", "/demo/load-sample-data")
    if result:
        st.toast(f"{result['loaded']} new memories loaded · {result['total']} total")


with st.sidebar:
    st.header("Living archive")
    health = api("GET", "/health")
    if health:
        st.success("Service ready")
        st.caption(f"Memory: {health['memory_mode']}\n\nAnswers: {health['llm_mode']}")
    st.info("Forget supports privacy, consent, and a community's right to withdraw knowledge.")

tabs = st.tabs(["🏠 Home", "✍️ Remember", "🔎 Recall", "🕸️ Memory Graph", "🌱 Improve", "🕊️ Forget", "🇳🇵 Demo Dataset"])

with tabs[0]:
    st.subheader("Culture becomes durable when memory persists")
    st.write("Heritage Memory preserves stories, recipes, rituals, language, and practical knowledge shared by elders. Unlike a disposable chatbot conversation, each account becomes persistent, attributable memory that can be recalled later, carefully improved as knowledge grows, visualized through relationships, and forgotten when privacy or consent requires it.")
    if st.button("Load Nepal Heritage Demo Dataset", type="primary", key="home_load"):
        load_demo()
    st.markdown("### Architecture")
    st.markdown('<div class="architecture">Streamlit UI → FastAPI → Cognee memory / JSON fallback<br>↘ Hugging Face multilingual embeddings → Gemini grounded answers<br>↘ PyVis cultural relationship graph</div>', unsafe_allow_html=True)

with tabs[1]:
    st.subheader("Remember an elder's knowledge")
    with st.form("remember"):
        left, right = st.columns(2)
        elder = left.text_input("Elder name", placeholder="Aama")
        location = right.text_input("Location", placeholder="Lamjung, Nepal")
        category = left.selectbox("Category", CATEGORIES)
        tags = right.text_input("Tags", placeholder="Dashain, tika, jamara")
        text = st.text_area("Memory in their words", height=180)
        save = st.form_submit_button("Preserve memory", type="primary")
    if save:
        result = api("POST", "/memory/remember", json={"elder_name": elder, "location": location, "category": category, "memory_text": text, "tags": [tag.strip() for tag in tags.split(",") if tag.strip()]})
        if result:
            st.success(f"Preserved as {result['memory_id']}")

with tabs[2]:
    st.subheader("Recall from remembered cultural context")
    examples = ["How was Dashain celebrated?", "What foods were prepared during festivals?", "What did elders teach children?"]
    st.caption("Try: " + " · ".join(examples))
    question = st.text_input("Ask a question")
    if st.button("Recall", type="primary", disabled=not question):
        result = api("POST", "/memory/recall", json={"question": question, "limit": 5})
        if result:
            st.markdown(f"### Answer\n{result['answer']}")
            st.caption(f"{result['llm_mode']} answer · {len(result['memories'])} supporting memories")
            for memory in result["memories"]:
                st.markdown(f'<div class="card"><b>{memory["elder_name"]}</b> · {memory["location"]}<br><small>{memory["category"]} · {" · ".join(memory["tags"])}</small><p>{memory["memory_text"]}</p></div>', unsafe_allow_html=True)

with tabs[3]:
    st.subheader("Elder → Location → Category → Memory → Tags")
    graph = api("GET", "/memory/graph")
    if graph and graph["nodes"]:
        colors = {"person":"#8b2f45","place":"#3c6e71","category":"#d48736","memory":"#718355","tag":"#80669d"}
        try:
            net = Network(height="610px", width="100%", bgcolor="#fffaf0", font_color="#263d35", directed=True)
            for node in graph["nodes"]:
                net.add_node(node["id"], label=node["label"], color=colors[node["type"]], title=node["type"])
            for edge in graph["edges"]:
                net.add_edge(edge["source"], edge["target"], title=edge["label"], color="#9b8b78")
            net.set_options('{"physics":{"barnesHut":{"gravitationalConstant":-4500,"springLength":130}},"edges":{"smooth":true,"arrows":{"to":{"enabled":true,"scaleFactor":0.4}}}}')
            components.html(net.generate_html(), height=630)
        except Exception:
            st.dataframe(graph["edges"], use_container_width=True)
    else:
        st.info("Preserve or load memories to grow this graph.")

with tabs[4]:
    st.subheader("Improve knowledge without hiding its history")
    options = memory_options()
    selected = st.selectbox("Memory", options, format_func=lambda key: f"{options[key]} · {key}", key="improve_id") if options else None
    detail = st.text_area("Correction or additional detail", key="detail")
    correction = st.checkbox("This replaces the current account (the old version remains in revision history)")
    if st.button("Update memory", type="primary", disabled=not (selected and detail)):
        if api("POST", "/memory/improve", json={"memory_id": selected, "additional_detail": detail, "correction": correction}):
            st.success("Memory and relationship graph updated.")

with tabs[5]:
    st.subheader("Forget with dignity")
    st.write("Cultural memory must respect privacy and continuing consent. Forget removes an account when a contributor or community no longer wants it retained.")
    options = memory_options()
    selected = st.selectbox("Memory to forget", options, format_func=lambda key: f"{options[key]} · {key}", key="forget_id") if options else None
    confirm = st.checkbox("I understand this removes the stored memory")
    if st.button("Forget memory", disabled=not (selected and confirm)):
        if api("DELETE", f"/memory/forget/{selected}"):
            st.warning("Memory forgotten.")
            st.rerun()

with tabs[6]:
    st.subheader("Eight Nepal heritage demo memories")
    if st.button("Load all sample memories", type="primary", key="demo_load"):
        load_demo()
    samples = api("GET", "/demo/sample-memories")
    if samples:
        for sample in samples:
            st.markdown(f'<div class="card"><b>{sample["elder_name"]}</b> · {sample["location"]}<br><small>{sample["category"]}</small><p>{sample["memory_text"]}</p></div>', unsafe_allow_html=True)
