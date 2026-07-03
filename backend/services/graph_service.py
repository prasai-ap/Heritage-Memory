from backend.models.schemas import GraphEdge, GraphNode, GraphResponse, Memory


class GraphService:
    @staticmethod
    def build(memories: list[Memory]) -> GraphResponse:
        nodes: dict[str, GraphNode] = {}
        edges: dict[tuple[str, str], GraphEdge] = {}

        def add_node(node_id: str, label: str, kind: str) -> None:
            nodes[node_id] = GraphNode(id=node_id, label=label, type=kind)

        def add_edge(source: str, target: str, label: str) -> None:
            edges[(source, target)] = GraphEdge(source=source, target=target, label=label)

        for memory in memories:
            person = f"person:{memory.elder_name.lower()}"
            place = f"place:{memory.location.lower()}"
            category = f"category:{memory.category.lower()}"
            item = f"memory:{memory.memory_id}"
            add_node(person, memory.elder_name, "person")
            add_node(place, memory.location, "place")
            add_node(category, memory.category, "category")
            add_node(item, memory.memory_text[:65] + ("…" if len(memory.memory_text) > 65 else ""), "memory")
            add_edge(person, place, "from")
            add_edge(place, category, "holds")
            add_edge(category, item, "includes")
            for tag in memory.tags:
                tag_id = f"tag:{tag.lower()}"
                add_node(tag_id, f"#{tag}", "tag")
                add_edge(item, tag_id, "tagged")
        return GraphResponse(nodes=list(nodes.values()), edges=list(edges.values()))
