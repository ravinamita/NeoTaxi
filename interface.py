from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def bfs(self, starting_node_name, destination_names):
        with self._driver.session() as session:
            try:
                if not isinstance(destination_names, list):
                    destination_names = [destination_names]

                bfsQuery = "MATCH path = shortestPath((start:Location)-[:TRIP*]-(dest:Location)) WHERE start.name = $starting_node_name AND dest.name IN $destination_names RETURN [node IN nodes(path) | node.name] AS path, reduce(cost = 0, r IN relationships(path) | cost + r.distance) AS totalCost"
                res = session.run(bfsQuery, starting_node_name=starting_node_name, destination_names=destination_names)

                bfsPath = []
                for record in res:
                    paths = [{'name': nodeName} for nodeName in record["path"]]
                    bfsPath.append({"path": paths, "totalCost": record["totalCost"]})

                return bfsPath if bfsPath else None
            except Exception as e:
                return []

    def pagerank(self, max_iterations=20, weight_attr='distance'):
        with self._driver.session() as session:
            try:
                dropProjectionQuery = "CALL gds.graph.exists('graphPagerank') YIELD exists WHERE exists CALL gds.graph.drop('graphPagerank', false) YIELD graphName RETURN graphName"
                session.run(dropProjectionQuery)

                projectionQuery = f"CALL gds.graph.project('graphPagerank','Location',{{TRIP: {{properties: ['{weight_attr}']}}}})"
                session.run(projectionQuery)

                pagerankQuery = f"CALL gds.pageRank.stream('graphPagerank', {{maxIterations: {max_iterations}, dampingFactor: 0.85, relationshipWeightProperty: '{weight_attr}'}}) YIELD nodeId, score RETURN nodeId, score"
                pagerankRes = session.run(pagerankQuery)

                nodeRes = session.run("MATCH (n:Location) RETURN n")
                nodeMap = {node["n"].id: node["n"]["name"] for node in nodeRes}

                nodes = []
                for record in pagerankRes:
                    nodeName = nodeMap.get(record["nodeId"])
                    if nodeName:
                        nodes.append({"name": nodeName, "score": round(record["score"], 5)})

                nodeSorted = sorted(nodes, key=lambda x: x["score"], reverse=True)
                topRes = nodeSorted[0] if nodeSorted else None
                bottom_res = nodeSorted[-1] if nodeSorted else None

                return [topRes, bottom_res] if topRes and bottom_res else []
            except Exception as e:
                return []