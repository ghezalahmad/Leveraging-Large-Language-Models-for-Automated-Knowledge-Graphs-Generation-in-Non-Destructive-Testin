
# Leveraging Large Language Models for Automated Knowledge Graphs Generation in Non-Destructive Testing

This repository contains the code and resources for the "Automated Knowledge Graph Generation for Non-Destructive Testing Using Large Language Models" paper. The project aims to extract information from heterogeneous scientific articles in the Non-Destructive Testing (NDT) domain and organize it into a Knowledge Graph (KG) using Neo4j and OpenAI's GPT-4o.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Results](#results)
- [Challenges and Future Work](#challenges-and-future-work)
- [Acknowledgements](#acknowledgements)
- [License](#license)

## Introduction

Non-Destructive Testing (NDT) is a crucial field in materials science and engineering, offering techniques to evaluate the properties of materials without causing damage. This project leverages advanced natural language processing (NLP) techniques, specifically large language models (LLMs) such as OpenAI's GPT-4o, to automate the extraction and organization of NDT methods, deterioration mechanisms, and physical changes into a comprehensive Knowledge Graph (KG).

## Features

- **Automated Data Extraction**: Uses GPT-4o to extract NDT-related information from scientific literature.
- **Knowledge Graph Construction**: Structures the extracted data into a Neo4j graph database.
- **Querying and Analysis**: Enables exploration and analysis of relationships between materials, deterioration mechanisms, physical changes, and NDT methods.


![Diagram](https://raw.githubusercontent.com/ghezalahmad/LLM_NDT_Knowledge_Graph/main/graph.svg)


## Installation

### Prerequisites

- Python 3.7 or higher
- Neo4j 4.0 or higher
- Required Python packages (listed in `requirements.txt`)

## Installation

### Step-by-Step Installation

1. **Clone the Repository**
    ```bash
    git clone https://github.com/ghezalahmad/LLM_NDT_Knowledge_Graph.git
    cd LLM_NDT_Knowledge_Graph

2. **Set Up a Virtual Environment (Optional)**
    ```bash
    pip install pipenv
    pipenv install
    pipenv shell

    And then: 
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`
    ```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set up Neo4j
4. **Set Up Neo4j**
    - Follow the instructions to install Neo4j: [Neo4j Installation Guide](https://neo4j.com/docs/operations-manual/current/installation/)
    - Start the Neo4j service:
    ```bash
    sudo systemctl start neo4j
    sudo systemctl enable neo4j
    ```

5. **Configure Neo4j Connection**
    - Update the connection details in the `config.py` file with your Neo4j credentials and address:
    ```python
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "your-password"
    
### Step 6: Set up OpenAI API

1. Sign up for an API key at [OpenAI](https://beta.openai.com/signup/).
2. Replace `Your_API_KEY` in the script with your actual OpenAI API key.


## Usage

### Data Extraction and KG Construction

1. **Data Collection**: Ensure your scientific literature and technical document dataset is ready. Place your documents in the `data/` directory.

2. **Run the Extraction Script**
    ```bash
    python agent_bricks.py
    ```

3. **Generate the Knowledge Graph**
    ```bash
    python create_kg.py
    ```
### Directory Structure

```
ndt-knowledge-graph/
├── data/
│   ├── Concrete.rtf
│   ├── Wood.rtf
│   ├── Bricks.rtf
│   ├── Metal.rtf
├──Code
├   ├── agent_bricks.py
│   ├── agent_woods.py
│   ├── agent_concrete.py
│   ├── agent_steel.py
│   ├── agent_kg.py
├── requirements.txt
└── README.md
```


### Querying the Knowledge Graph

- You can query the Neo4j database using Cypher queries. Access the Neo4j browser at `http://localhost:7474` and use the provided queries in the `queries/` directory to explore the KG.

### Example Queries

```cypher
MATCH (m:Material)-[:HAS_DETERIORATION_MECHANISM]->(d:DeteriorationMechanism)-[:CAUSES_PHYSICAL_CHANGE]->(p:PhysicalChange)-[:DETECTED_BY]->(n:NDTMethod)
RETURN m.name, d.name, p.name, n.name
```


## Results

The constructed Knowledge Graph includes nodes representing four primary materials: concrete, steel, wood, and bricks. Each material node is linked to various deterioration mechanisms, physical changes, and corresponding NDT methods. The KG enables the exploration and analysis of how different NDT techniques are applied to detect specific types of deterioration across various materials.

## How to Contribute

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## Challenges and Future Work

### Challenges

- Ensuring consistent terminology across diverse documents.
- Balancing specificity and generalizability in the extracted data.
- Distinguishing between natural features and actual deterioration mechanisms.

### Future Work

- Expanding the corpus of scientific articles to include more diverse sources and materials.
- Improving the accuracy and depth of entity and relationship extraction through advanced machine learning techniques.
- Integrating the KG with other scientific databases and ontologies to enrich its content.

## Acknowledgements

We thank Reincarnate for funding this project. Special thanks to Benjamin, Andre, and Sabine for their support and contributions.
## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact ghezalahmad.zia@outlook.com.
```

