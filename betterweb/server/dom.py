import typing as t
from collections import defaultdict


class DOMNode(t.TypedDict):
    tag: str
    properties: dict
    children: list["DOMNode| str"]


class DOM:
    events: dict[str, dict[str, t.Callable]] = defaultdict(dict)
    id: int = 0
    void = ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"]

    @classmethod
    def create(
        cls, tag: str, properies: dict, children: list["DOMNode |str"]
    ) -> "DOMNode":
        id = f"dom-{cls.id}"
        properies["id"] = id
        cls.id += 1

        for k, v in properies.items():
            if isinstance(v, t.Callable):
                cls.events[id][k] = v
                properies[k] = (
                    f"socket.send(JSON.stringify({{type: &quot;event&quot;, data: {{id: &quot;{id}&quot;, event: &quot;{k}&quot;}}}}))"
                )

        return {
            "tag": tag,
            "properties": properies,
            "children": children,
        }

    @classmethod
    def to_html(cls, node: "DOMNode") -> str:
        if node["tag"] in cls.void:
            return f"<{node['tag']} {" ".join([f'{k}="{v}"' for k, v in node['properties'].items()])} />"

        return f"<{node['tag']} {" ".join([f'{k}="{v}"' for k, v in node['properties'].items()])} >{''.join([c if isinstance(c, str) else cls.to_html(c) for c in node['children']])}</{node['tag']}>"

# () => socket.send({type: &quot;event&quot;, data: {id: this.id, event: &quot;onclick&quot;}})
