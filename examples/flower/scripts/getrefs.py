import json
import os

def load_json(path):
    """Load JSON data from a file."""
    with open(path, 'r') as f:
        return json.load(f)

def query_label_refs(file_name, label_refs):
    """Query all labels referenced in a given source file."""
    referenced_labels = {}

    # Go through each label and check if the source file references it
    for label, references in label_refs.items():
        for ref in references:
            if ref["ref_file"] == file_name:
                if label not in referenced_labels:
                    referenced_labels[label] = []
                # Add each reference with line number and content
                referenced_labels[label].append((ref["ref_line"], ref["ref_content"].split(';')[0].strip()))

    return referenced_labels

def save_references_to_file(file_name, references):
    """Save the referenced labels to an output file in the utils directory."""
    output_path = os.path.join(OUTPUT_DIR, "referenced_labels.txt")
    with open(output_path, 'w') as f:
        for label, refs in sorted(references.items()):
            f.write(f"Label: {label}\n")
            for line_num, content in refs:
                f.write(f"  {line_num}: {content}\n")
            f.write("\n")
    print(f"Referenced labels saved to {output_path}")

if __name__ == "__main__":
    # Paths to input and output files
    LABEL_REFS_PATH = "utils/label_refs.json"
    OUTPUT_DIR = "utils"

    # Load label references from the JSON file
    label_refs = load_json(LABEL_REFS_PATH)

    # Get the source file name to query from user input
    file_name = "patch.inc"

    # Query all labels referenced in the given source file
    referenced_labels = query_label_refs(file_name, label_refs)

    # Save the results to a file in the utils directory
    save_references_to_file(file_name, referenced_labels)
