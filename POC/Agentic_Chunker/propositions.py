import os
import json
from typing import List, Dict, Any
from pathlib import Path
from AWS_utils import S3Handler
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv(override=True)
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("./logs/proposition_generation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PropositionGenerator:
    def __init__(self, bucket_name: str):
        """Initialize the generator with AWS S3 configuration."""
        self.s3_handler = S3Handler(bucket_name)
        self.parsed_prefix = "parsed_docs/"
        self.propositions_prefix = "propositions/"
    
    def load_parsed_json(self, s3_key: str) -> Dict:
        """Download and load the parsed JSON from S3."""
        try:
            json_obj = self.s3_handler.download_fileobj(s3_key)
            if not json_obj:
                raise ValueError(f"Failed to download {s3_key} from S3")
            
            document = json.loads(json_obj.read().decode('utf-8'))
            logger.info(f"Loaded parsed JSON: {s3_key}")
            return document
        except Exception as e:
            logger.error(f"Error loading parsed JSON {s3_key}: {str(e)}")
            return {}

    def resolve_reference(self, json_data: Dict, ref: str) -> Dict:
        """Resolve a $ref reference within the JSON structure."""
        try:
            if not ref.startswith("#/"):
                raise ValueError(f"Invalid reference format: {ref}")
            keys = ref[2:].split("/")
            result = json_data
            for key in keys:
                result = result[key]
            return result
        except KeyError:
            logger.error(f"Could not resolve reference: {ref}")
            return {}

    def extract_propositions(self, json_data: Dict) -> List[Dict]:
        """Extract propositions from the parsed JSON structure."""
        propositions = []
        doc_name = json_data.get("name", "unknown_doc")
        body = json_data.get("body", {})
        children = body.get("children", [])

        for child in children:
            if "$ref" in child:
                element = self.resolve_reference(json_data, child["$ref"])
                if not element:
                    continue

                if "text" in element and isinstance(element, dict):
                    text = element.get("text", "").strip()
                    prov_list = element.get("prov", [])
                    page_no = (
                        prov_list[0].get("page_no", -1)
                        if isinstance(prov_list, list) and prov_list and isinstance(prov_list[0], dict)
                        else -1
                    )
                    if text:
                        propositions.append({
                            "type": element.get("label", "text"),
                            "doc_name": doc_name,
                            "content": text,
                            "page_no": page_no
                        })
                elif "data" in element:  # Handle tables
                    table_text = " ".join(
                        cell.get("text", "")
                        for cell in element.get("data", {}).get("grid", [])
                    ).strip()
                    if table_text:
                        propositions.append({
                            "type": "table",
                            "doc_name": doc_name,
                            "content": table_text
                        })
                elif "image" in element:  # Handle pictures
                    propositions.append({
                        "type": "picture",
                        "doc_name": doc_name,
                        "content": "Image placeholder",
                        "metadata": {"ref": child["$ref"]}
                    })
            else:
                logger.warning(f"Unexpected child structure: {child}")

        logger.info(f"Extracted {len(propositions)} propositions from {doc_name}")
        return propositions

    def save_propositions(self, doc_name: str, propositions: List[Dict]) -> str:
        """Save generated propositions as a JSON file in S3."""
        try:
            json_content = json.dumps(propositions, indent=4)
            s3_key = f"{self.propositions_prefix}{doc_name}_propositions.json"
            self.s3_handler.save_parsed_json(s3_key, json_content)
            logger.info(f"Propositions saved to S3: {s3_key}")
            return s3_key
        except Exception as e:
            logger.error(f"Error saving propositions for {doc_name}: {str(e)}")
            return ""

    def process_documents(self):
        """Process all parsed documents to generate propositions."""
        parsed_files = self.s3_handler.list_files(self.parsed_prefix)
        json_files = [f for f in parsed_files if f.endswith(".json") and "propositions" not in f]

        logger.info(f"Found {len(json_files)} parsed JSON files to process.")
        for s3_key in json_files:
            try:
                # Load parsed JSON
                document = self.load_parsed_json(s3_key)
                if not document:
                    continue

                # Generate propositions
                doc_name = Path(s3_key).stem
                propositions = self.extract_propositions(document)

                # Save propositions to S3
                self.save_propositions(doc_name, propositions)
            except Exception as e:
                logger.error(f"Error processing document {s3_key}: {str(e)}")

def main():
    """Main function to generate propositions."""
    try:
        if not AWS_BUCKET_NAME:
            raise ValueError("AWS_BUCKET_NAME environment variable is not set")

        generator = PropositionGenerator(AWS_BUCKET_NAME)
        generator.process_documents()

    except Exception as e:
        logger.error(f"Critical error in proposition generation: {str(e)}")

if __name__ == "__main__":
    main()
