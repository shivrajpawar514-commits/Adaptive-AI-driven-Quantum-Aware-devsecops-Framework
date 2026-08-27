from typing import List, Dict, Set


def topological_sort(playbooks: List[Dict]) -> List[Dict]:
    """Return a list of playbooks sorted respecting dependencies.

    Each playbook dict is expected to have an 'id' and optional 'dependencies' list of ids.
    Simple Kahn's algorithm implementation; raises ValueError on cycles.
    """
    # Build adjacency and indegree maps
    id_to_pb = {pb['id']: pb for pb in playbooks}
    indegree: Dict[str, int] = {pb_id: 0 for pb_id in id_to_pb}
    adj: Dict[str, Set[str]] = {pb_id: set() for pb_id in id_to_pb}
    for pb in playbooks:
        deps = pb.get('dependencies', []) or []
        for d in deps:
            if d not in id_to_pb:
                continue  # ignore missing deps for now
            adj[d].add(pb['id'])
            indegree[pb['id']] += 1
    # Kahn's algorithm
    ready = [pb_id for pb_id, deg in indegree.items() if deg == 0]
    order: List[Dict] = []
    while ready:
        current = ready.pop()
        order.append(id_to_pb[current])
        for neighbor in list(adj[current]):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                ready.append(neighbor)
            adj[current].remove(neighbor)
    if len(order) != len(playbooks):
        raise ValueError("Cyclic dependency detected among playbooks")
    return order
