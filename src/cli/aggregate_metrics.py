import os
import json

from src.cli.utils import print_error, print_info

metrics = {}
metrics["sonar"] = ['tests',
                    'test_failures',
                    'test_errors',
                    'coverage',
                    'test_execution_time',
                    'functions',
                    'complexity',
                    'comment_lines_density',
                    'duplicated_lines_density']

metrics["github"] = ['resolved_issues', 'total_issues']

def read_msgram(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_metrics(file_name, metrics):
    # Extract the directory path from the file_name
    directory = os.path.dirname(file_name)

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Save the metrics file
    output_file_path = os.path.join(directory, os.path.basename(file_name).replace('.msgram', '.metrics'))
    with open(output_file_path, 'w') as output_file:
        json.dump(metrics, output_file, indent=2)
    
    print_info('> [blue] Metrics saved to: {output_file_path}\n')



def aggregate_metrics(folder_path):
    # Get all .msgram files in the specified directory
    msgram_files = [file for file in os.listdir(folder_path) if file.endswith('.msgram')]

    # Identify GitHub files based on the file name prefix
    github_files = [file for file in msgram_files if file.startswith('github_')]

    # Check if no GitHub files were found
    if not github_files:
        print_error('GitHub files not found in the directory: {folder_path}\n')
        return

    print_info('> [blue] GitHub metrics found in: {", ".join(github_files)}\n')

    # Extract project key from the first .msgram file
    project_key = read_msgram(os.path.join(folder_path, msgram_files[0])).get('project_key', '')

    # Extract key for GitHub metrics from the first GitHub file
    first_github_file = read_msgram(os.path.join(folder_path, github_files[0]))
    github_key = next(iter(first_github_file.keys() - metrics["sonar"]), '')

    # Iterate through remaining files
    for file in msgram_files:
        if file not in github_files:
            print_info('> [blue] Processing {file}')
            file_content = read_msgram(os.path.join(folder_path, file))

            # Extract Sonar metrics from the current file
            sonar_metrics = file_content.get(project_key, [])

            # Extract GitHub metrics from the GitHub file
            github_metrics = [
                {
                    "metric": metric,
                    "value": next(
                        (m["value"] for m in first_github_file[github_key] if m["metric"] == metric),
                        None
                    )
                }

                for metric in metrics["github"]
            ]

            # Add GitHub metrics to the Sonar metrics block
            sonar_metrics += github_metrics

            # Update the original dictionary with the modified list of metrics
            file_content[project_key] = sonar_metrics

            # Save the modified content to the file
            save_metrics(os.path.join(folder_path, file), file_content)

