import os

import requests
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

API = os.getenv("BACKEND_URL", "http://localhost:8000")
st.set_page_config(page_title="Heritage Memory", page_icon="🏔️", layout="wide")
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg,#fffaf0 0%,#f6efe2 55%,#e7f0e8 100%); }
.hero { padding:2rem 2.4rem; border-radius:24px; color:#fff; margin-bottom:1.2rem;
 background:linear-gradient(120deg,#7d2637,#b75d32); box-shadow:0 12px 35px #6f342533; }
.hero h1 { margin:0; font-size:2.8rem; } .hero p {font-size:1.05rem;opacity:.92}
.memory-card {background:#fffdf8;border-left:5px solid #b75d32;padding:1rem 1.2rem;
 border-radius:10px;margin:.7rem 0;box-shadow:0 3px 12px #492d1915}
[data-testid="stSidebar"] {background:#263d35;color:white}
</style>
<div class="hero"><h1>🏔️ Heritage Memory</h1><p>Voices remembered. Wisdom carried forward.</p></div>
""", unsafe_allow_html=True)


def api(method: str, path: str, **kwargs):
    try:
        response = requests.request(method, f"{API}{path}", timeout=45, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Could not reach the memory service: {exc}")
        return None


with st.sidebar:
    st.header("Heritage Memory")
    health = api("GET", "/health")
    if health:
        st.success("Memory service is ready")
        st.caption(f"Memory: {health['memory_mode']} · Answers: {health['llm_mode']}")
    if st.button("Load Nepal demo memories", use_container_width=True):
        result = api("POST", "/demo/load-sample-data")
        if result:
            st.toast(f"{result['loaded']} new memories loaded")
            st.rerun()
    st.caption("Built for communities who want their stories to outlive the moment.")

remember_tab, recall_tab, improve_tab, graph_tab = st.tabs([
    "✍️ Remember", "🔎 Recall", "🌱 Improve & Forget", "🕸️ Living graph"
])

with remember_tab:
    st.subheader("Preserve an oral memory")
    with st.form("remember"):
        left, right = st.columns(2)
        elder = left.text_input("Elder or storyteller", placeholder="Aama Maya")
        location = right.text_input("Place", placeholder="Bhaktapur, Nepal")
        category = left.selectbox("Category", ["Tradition", "Story", "Food", "Farming", "Festival", "Language", "Craft", "Learning"])
        tags = right.text_input("Tags (comma separated)", placeholder="rice, harvest, community")
        memory_text = st.text_area("Their memory, in their words", height=180)
        submitted = st.form_submit_button("Preserve this memory", type="primary")
    if submitted:
        payload = {"elder_name": elder, "location": location, "category": category,
                   "memory_text": memory_text, "tags": [x.strip() for x in tags.split(",") if x.strip()]}
        result = api("POST", "/memory/remember", json=payload)
        if result:
            st.success(f"Memory preserved with ID {result['id']}")

with recall_tab:
    st.subheader("Ask the ancestors")
    question = st.text_input("What would you like to learn?", placeholder="How was millet traditionally planted?")
    if st.button("Recall cultural knowledge", type="primary", disabled=not question):
        result = api("POST", "/memory/recall", json={"question": question, "limit": 5})
        if result:
            st.markdown(f"### Answer\n{result['answer']}")
            st.caption(f"Generated in {result['llm_mode']} mode from {len(result['memories'])} preserved memories")
            with st.expander("See the memories behind this answer"):
                for memory in result["memories"]:
                    st.markdown(f"""<div class="memory-card"><b>{memory['elder_name']}</b> · {memory['location']}<br>
                    <small>{memory['category']} · {' · '.join(memory['tags'])}</small><p>{memory['memory_text']}</p>
                    <code>{memory['id']}</code></div>""", unsafe_allow_html=True)

with improve_tab:
    st.subheader("Knowledge changes through careful conversation")
    memory_id = st.text_input("Memory ID")
    detail = st.text_area("Correction or additional detail")
    correction = st.checkbox("Replace the current account (keeps revision history)")
    col1, col2, _ = st.columns([1, 1, 2])
    if col1.button("Improve", type="primary", disabled=not (memory_id and detail)):
        result = api("POST", "/memory/improve", json={"memory_id": memory_id, "additional_detail": detail, "correction": correction})
        if result:
            st.success("Memory improved; its earlier version remains in revision history.")
    if col2.button("Forget", disabled=not memory_id):
        result = api("DELETE", f"/memory/forget/{memory_id}")
        if result:
            st.warning("The memory has been forgotten.")

with graph_tab:
    st.subheader("A living map of people, places, and knowledge")
    graph = api("GET", "/memory/graph")
    if graph and graph["nodes"]:
        colors = {"person": "#8b2f45", "place": "#3c6e71", "category": "#d48736", "memory": "#718355", "tag": "#80669d"}
        net = Network(height="620px", width="100%", bgcolor="#fffaf0", font_color="#263d35", directed=True)
        for node in graph["nodes"]:
            net.add_node(node["id"], label=node["label"], color=colors.get(node["type"], "#999"), title=node["type"], shape="dot")
        for edge in graph["edges"]:
            net.add_edge(edge["source"], edge["target"], title=edge["label"], color="#9b8b78")
        net.set_options('{"physics":{"barnesHut":{"gravitationalConstant":-4500,"springLength":130}},"edges":{"smooth":true,"arrows":{"to":{"enabled":true,"scaleFactor":0.4}}}}')
        components.html(net.generate_html(), height=640)
    else:
        st.info("Load demo memories or preserve a story to grow the graph.")
