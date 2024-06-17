
# LLM NDT Knowledge Graph

This project extracts information about Non-Destructive Testing (NDT) methods and their related deterioration mechanisms for various materials from provided documents. The information is then structured and imported into a Neo4j knowledge graph for better visualization and analysis.

## Features

- Extracts NDT information from RTF documents.
- Uses OpenAI GPT-3.5 to extract deterioration mechanisms and NDT tools.
- Consolidates and finds relationships between NDT tools and materials.
- Creates a knowledge graph in Neo4j to represent the extracted information.

## Requirements

- Python 3.7 or higher
- Neo4j 4.0 or higher
- Required Python packages (listed in `requirements.txt`)

## Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/ndt-knowledge-graph.git
cd ndt-knowledge-graph
```

### Step 2: Set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set up Neo4j

1. Download and install Neo4j from [neo4j.com](https://neo4j.com/download/).
2. Start the Neo4j server.
3. Set up a database and note down the credentials (username and password).

### Step 5: Set up OpenAI API

1. Sign up for an API key at [OpenAI](https://beta.openai.com/signup/).
2. Replace `Your_API_KEY` in the script with your actual OpenAI API key.

## Usage

1. Ensure you have the required RTF files (`Concrete.rtf`, `Wood.rtf`, `Bricks.rtf`, `Metal.rtf`) in the `data` directory.

2. Run the main script to extract information and create the Neo4j graph:

```bash
python main_file.py
```

### Directory Structure

```
ndt-knowledge-graph/
├── data/
│   ├── Concrete.rtf
│   ├── Wood.rtf
│   ├── Bricks.rtf
│   ├── Metal.rtf
├── requirements.txt
├── main_file.py
├── graph_neo4j.py
└── README.md
```

## Script Overview

### main_file.py

- **Purpose**: Extracts NDT information from RTF files using OpenAI GPT-3.5 and consolidates relationships.
- **Functions**:
  - `read_rtf_file(file_path)`: Reads an RTF file and converts it to plain text.
  - `extract_information(material_text, material_name)`: Extracts deterioration mechanisms and NDT tools from the text using OpenAI.
  - `find_relationships(combined_text)`: Analyzes and finds relationships between NDT tools and materials.
- **Output**: Writes extracted information and relationships to text files.

### graph_neo4j.py

- **Purpose**: Creates a Neo4j knowledge graph from the extracted information.
- **Functions**:
  - `create_neo4j_graph(driver, extracted_info)`: Processes the extracted information and creates nodes and relationships in Neo4j.
  - `create_relationships(session, tool, mechanism, material)`: Creates relationships between NDT tools, deterioration mechanisms, and materials in Neo4j.

## How to Contribute

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact [your email].
```

