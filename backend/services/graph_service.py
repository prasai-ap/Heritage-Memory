from collections import Counter

from backend.models.schemas import Memory


class GraphService:
    COLORS = {"elder": "#D18B47", "location": "#5E8C6A", "category": "#B4563A", "memory": "#E9C46A", "tag": "#517A8A"}

    def build(self, memories: list[Memory]) -> dict:
        nodes, edges, seen = [], [], set()

        def node(node_id: str, label: str, kind: str, size: int = 18):
            if node_id not in seen:
                seen.add(node_id)
                nodes.append({"id": node_id, "label": label, "group": kind, "color": self.COLORS[kind], "size": size})

        for memory in memories:
            mid = f"memory:{memory.memory_id}"
            eid, lid, cid = f"elder:{memory.elder_name}", f"location:{memory.location}", f"category:{memory.category}"
            node(eid, memory.elder_name, "elder", 23)
            node(lid, memory.location, "location", 21)
            node(cid, memory.category, "category", 20)
            node(mid, memory.summary[:48] + ("…" if len(memory.summary) > 48 else ""), "memory", 17)
            edges += [{"from": eid, "to": mid}, {"from": lid, "to": mid}, {"from": cid, "to": mid}]
            for tag in memory.tags:
                tid = f"tag:{tag.casefold()}"
                node(tid, f"#{tag}", "tag", 14)
                edges.append({"from": mid, "to": tid})
        return {"nodes": nodes, "edges": edges, "legend": self.COLORS}


class InsightService:
    def calculate(self, memories: list[Memory]) -> dict:
        tags = Counter(tag for m in memories for tag in m.tags)
        locations = Counter(m.location for m in memories)
        categories = Counter(m.category for m in memories)
        return {
            "total_memories": len(memories),
            "elders_represented": len({m.elder_name for m in memories}),
            "locations_represented": len(locations),
            "categories_represented": len(categories),
            "total_tags": sum(tags.values()),
            "unique_tags": len(tags),
            "most_connected_tag": tags.most_common(1)[0][0] if tags else None,
            "most_mentioned_location": locations.most_common(1)[0][0] if locations else None,
            "category_distribution": dict(categories),
        }

