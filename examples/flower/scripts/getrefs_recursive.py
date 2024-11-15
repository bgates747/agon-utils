import json
import os
from collections import defaultdict

def load_json(path):
    """Load JSON data from a file."""
    with open(path, 'r') as f:
        return json.load(f)

def query_unique_label_refs(label_refs):
    """Generate a dictionary with one instance of each label per file."""
    unique_references = defaultdict(dict)

    for label, references in label_refs.items():
        for ref in references:
            ref_file = ref["ref_file"]
            if label not in unique_references[ref_file]:
                unique_references[ref_file][label] = (ref["ref_line"], ref["ref_content"].split(';')[0].strip())

    return unique_references

def gather_dependencies(label, unique_references, visited, dependencies):
    """Recursively gather dependencies for a given label, excluding self-references."""
    if label in visited:
        return  # Prevent circular dependency loops
    visited.add(label)

    for ref_file, labels in unique_references.items():
        if label in labels:
            dependencies[ref_file].add(label)
            for dep_label in labels:
                if dep_label != label:  # Avoid self-referencing
                    gather_dependencies(dep_label, unique_references, visited, dependencies)

def save_references_to_file(output_path, self_references, dependencies):
    """Save the referenced labels to an output file with self-references at the top."""
    with open(output_path, 'w') as f:
        # Write self-references at the top
        f.write("Self-references:\n")
        for label in sorted(self_references):
            f.write(f"  {label}\n")
        f.write("\n")

        # Write dependencies
        f.write("Referenced labels with dependencies:\n")
        for label in sorted(dependencies):
            f.write(f"  {label}\n")
        f.write("\n")
    print(f"Referenced labels saved to {output_path}")

if __name__ == "__main__":
    # Define paths to input and output files
    label_refs_path = "basic/label_refs.json"
    label_defs_path = "basic/label_defs.json"
    output_directory = "basic"
    output_path = os.path.join(output_directory, "referenced_labels.txt")

    # Set the specific file name you want to analyze
    file_name = "eval.asm"  # Specify the file to analyze

    # Load label references and definitions from JSON files
    label_refs = load_json(label_refs_path)
    label_defs = load_json(label_defs_path)

    # Generate unique references excluding multiple occurrences of the same label per file
    unique_references = query_unique_label_refs(label_refs)

    # Identify self-references and recursive dependencies for the specified file
    self_references = set()
    dependencies = set()

    if file_name in unique_references:
        for label in unique_references[file_name]:
            # Check if the label has a definition in label_defs and if it's self-referenced
            if label in label_defs and file_name == label_defs[label][0]["def_file"]:
                self_references.add(label)
            else:
                # Gather dependencies recursively
                gather_dependencies(label, unique_references, set(), dependencies)
    else:
        print(f"No references found for file: {file_name}")

    # Save the results to a file in the basic directory
    save_references_to_file(output_path, self_references, dependencies)
