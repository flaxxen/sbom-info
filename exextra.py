
# Check all subdirectories for the filetype and numer of files in each subdir.
def check_subdir_file_types_with_count(start_dir, output_csv):
    records = []

    for root, dirs, files in os.walk(start_dir):
        file_count = len(files)  # Count the number of files in the current subdirectory

        if file_count == 0:  # Skip if the directory has no files
            continue

        file_types = set(os.path.splitext(file)[1].lower() for file in files if os.path.isfile(os.path.join(root, file)))

        if len(file_types) == 1:           file_type = file_types.pop()
        else:
            file_type = "N/A"

        subdir_name = os.path.relpath(root, start_dir)
        records.append([subdir_name, file_type, file_count])

    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Subdirectory', 'FileType', 'FileCount'])
        writer.writerows(records)
		
# Run Grype on all SBOMs in a directory and output reports to another directory
def run_grype_on_sbom_folder(sbom_dir, output_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(sbom_dir):
        if filename.startswith("20"):  # Assuming all filenames start with '20' indicating the year
            date_part = filename.split("_")[0]  # Extract the date part from the filename
            sbom_path = os.path.join(sbom_dir, filename)
            output_filename = f"{date_part}_grype_output.json"
            output_path = os.path.join(output_dir, output_filename)
			sbom_path_wsl = subprocess.getoutput(f'wsl wslpath -a "{sbom_path}"') 	
            # Run Grype and redirect output to a file
            with open(output_path, "w") as output_file:
                subprocess.run(["wsl", "grype", "-o", "json", f"sbom:{sbom_path_wsl}"], stdout=output_file)
				
				
				
# Read a single json file
def parse_grype_output(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Read a directory of grype reports into memory and return
def read_reports(sbom_directory):
    reports = []
    for filename in os.listdir(sbom_directory):
        full_path = os.path.join(sbom_directory, filename)  # Full path to the file
        try:
            date_str = filename.split("_")[0]  # Extract the date part from the filename
            report_date = datetime.strptime(date_str, '%Y%m%d')
            report_content = parse_grype_output(full_path)
            reports.append([report_date, report_content])
        except Exception as e:  # Generic exception handling, consider specifying exceptions
            print(f"Error processing file {filename}: {e}")
    reports.sort(key=lambda x: x[0])  # Sort reports by date
    return reports
 