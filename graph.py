from neo4j import GraphDatabase
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

class NDTKnowledgeGraph:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_node(self, label, name):
        with self.driver.session() as session:
            session.execute_write(self._create_and_return_node, label, name)

    def create_relationship(self, from_label, from_name, to_label, to_name, relationship_type):
        with self.driver.session() as session:
            session.execute_write(self._create_and_return_relationship, from_label, from_name, to_label, to_name, relationship_type)

    @staticmethod
    def _create_and_return_node(tx, label, name):
        query = (
            f"MERGE (n:{label} {{name: $name}}) "
            "ON CREATE SET n.created = timestamp() "
            "ON MATCH SET n.lastSeen = timestamp() "
            "RETURN n.name AS name"
        )
        print(f"Running query: {query} with name={name}")
        result = tx.run(query, name=name)
        record = result.single()
        if record is None:
            raise ValueError(f"No record found for node {name}")
        return record['name']

    @staticmethod
    def _create_and_return_relationship(tx, from_label, from_name, to_label, to_name, relationship_type):
        query = (
            f"MATCH (a:{from_label} {{name: $from_name}}), (b:{to_label} {{name: $to_name}}) "
            f"MERGE (a)-[r:{relationship_type}]->(b) "
            "RETURN type(r) AS type"
        )
        print(f"Running query: {query} with from_name={from_name}, to_name={to_name}")
        result = tx.run(query, from_name=from_name, to_name=to_name)
        record = result.single()
        if record is None:
            raise ValueError(f"No record found for relationship between {from_name} and {to_name}")
        return record['type']

# Connect to the Neo4j database
uri = "neo4j://localhost:7687"
user = "neo4j"
password = "eklil@2017"
graph = NDTKnowledgeGraph(uri, user, password)

# Example data
mechanisms = {
    "Overloading": ["Structural damage"],
    "Temperature": ["Expansion", "Contraction"],
    "Shrinkage": ["Cracks", "Stress"],
    "Fire": ["Compromised integrity", "Spalling"],
    "Freeze and Thaw": ["Cracking", "Scaling"],
    "Carbonation": ["pH reduction", "Steel reinforcement corrosion"],
    "Chloride Penetration": ["Reinforcement corrosion"],
    "Corrosion": ["Steel reinforcement deterioration"],
    "Alkali-Aggregate Reaction (AAR)": ["Expansion", "Cracking"],
    "Sulphate Attack": ["Expansion", "Deterioration"],
    "Leaching": ["Loss of material", "Strength reduction"],
    "Ammonium Nitrate Attack": ["Expansive reactions", "Cracking"]
}

solutions = {
    "Structural damage": ["Ultrasonic Testing", "Radiographic Testing"],
    "Expansion": ["Thermographic Testing"],
    "Contraction": ["Thermographic Testing"],
    "Cracks": ["Visual Inspection", "Acoustic Emission"],
    "Stress": ["Strain Gauge Testing"],
    "Compromised integrity": ["Radiographic Testing"],
    "Spalling": ["Visual Inspection"],
    "Cracking": ["Acoustic Emission", "Ultrasonic Testing"],
    "Scaling": ["Visual Inspection"],
    "pH reduction": ["Chemical Analysis"],
    "Steel reinforcement corrosion": ["Corrosion Potential Measurement", "Radiographic Testing"],
    "Reinforcement corrosion": ["Corrosion Potential Measurement"],
    "Steel reinforcement deterioration": ["Radiographic Testing"],
    "Loss of material": ["Ultrasonic Testing"],
    "Strength reduction": ["Load Testing"],
    "Expansive reactions": ["Acoustic Emission", "Ultrasonic Testing"]
}

# Create nodes and relationships
for mechanism, effects in mechanisms.items():
    graph.create_node("DeteriorationMechanism", mechanism)
    for effect in effects:
        graph.create_node("Effect", effect)
        graph.create_relationship("DeteriorationMechanism", mechanism, "Effect", effect, "CAUSES")

for effect, tools in solutions.items():
    for tool in tools:
        graph.create_node("NDTTool", tool)
        graph.create_relationship("Effect", effect, "NDTTool", tool, "CAN_BE_TESTED_WITH")

graph.close()
