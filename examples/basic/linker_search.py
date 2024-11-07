import re
from linker import load_files_to_dict, file_list

def search_label_in_files(files_dict, label, output_file):
    """Searches for a label in the files dictionary and writes occurrences to an output file,
    excluding instances found within comments.
    
    Args:
        files_dict (dict): The original dictionary with filenames as keys and lists of lines as values.
        label (str): The label to search for.
        output_file (str): The file path where results should be written.
    """
    label_pattern = re.compile(rf'\b{label}\b')  # Whole-word match, case-sensitive

    with open(output_file, 'w') as file:
        file.write(f"Search results for label '{label}':\n\n")
        
        for filename in sorted(files_dict.keys()):  # Sort filenames alphabetically
            matching_lines = []
            
            for line_num, line in enumerate(files_dict[filename], start=1):
                # Split line into code and comment parts
                code_part = line.split(';', 1)[0]  # Exclude anything after ';'

                # Search for label as a whole word in the code part only
                if label_pattern.search(code_part):
                    matching_lines.append((line_num, line.strip()))
            
            # Write results for the current file if any matches were found
            if matching_lines:
                file.write(f"; ======= File: {filename} =======\n")
                for line_num, code in matching_lines:
                    file.write(f"{line_num:4}: {code}\n")
                file.write("\n")  # Add a blank line after each file's results

    print(f"Search results written to {output_file}")


if __name__ == "__main__":
    # Define the directory and list of include files
    directory = "examples/basic"

    # Load files into a dictionary
    files_dict = load_files_to_dict(directory, file_list)

    # Define the label to search for and the output file
    search_label = "BAD"
    search_output_file = f"{directory}/label_search.txt"

    # Call the search function from search_util.py
    search_label_in_files(files_dict, search_label, search_output_file)