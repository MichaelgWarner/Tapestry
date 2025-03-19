import os
import subprocess
import logging

# Configure logging
logging.basicConfig(
    filename="tapestry_execution_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def display_splash():
    splash = """
                               ████████                  
                         █████████████████████           
                    █████████████████████████████        
                 ███████████     ███     ██████████      
              █████████     ███████████       ███████    
            ███████    ████████████████████     ██████   
          ███████   ████████   ████  █████████   ██████  
        ██████   ███████      ████        █████   ██████ 
       █████   ██████         ████          ████   █████ 
      █████   ████           █████           ████   █████
    █████   ████            █████             ███   █████
   ██████__████           ████████ _          ███    ████
  █|__   __|██         ███████████| |         ███    ████
  ████| |██__ _  _ __ ████████████| |_  _ __  ███ _  ████
 █████| |█/ _` || '_ \██/ _ \/ __|| __|| '__|| |█| | ███ 
 ████ | || (_| || |_) ||  __/\__ \| |_ | |   | |_| | ███ 
█████ |_|█\__,_|| .__/██\___||___/ \__||_|  ██\__, | ██  
████    ███     | |  ████████████          ████__/ | █   
████    ███     |_| ███████████           ████|___/██    
█████   ███        █████                 ████  ██████    
█████   ████      ████                 ████   █████      
 █████   ████   ████                █████   ██████       
 █████    ████████                ██████  ██████         
  ██████    ███████         █████████   ███████          
   ██████   ██████████████████████    ███████            
    █████████     ███████████     ████████               
      █████████              ███████████                 
        ████████████████████████████                     
       █   ██████████████████████                         
                 █████████                                
    """
    print(splash)

def load_rules(rule_file, log_type, analysis_choice):
    """Load rules from the rule file based on the log type and analysis choice."""
    rules = []
    
    with open(rule_file, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("//"):
                continue
            
            # Split only on the first '|'
            parts = line.split("|", 1)
            if len(parts) != 2:
                continue
            
            rule_code, command = parts
            
            # Ensure rule code is exactly 6 digits
            if len(rule_code) != 6 or not rule_code.isdigit():
                continue
            
            # Extract relevant digits
            rule_log_type = int(rule_code[2])
            rule_analysis_choice = int(rule_code[3])
            
            rules.append((rule_code, rule_log_type, rule_analysis_choice, command))
    
    return rules

def execute_rules(rules, log_file, field_positions, is_summary_report=False):
    """Execute the given list of rules on the specified log file."""
    # Create results directory inside the current working directory
    results_directory = os.path.join(os.getcwd(), "Tapestry_Results")
    os.makedirs(results_directory, exist_ok=True)
    
    summary_report_path = os.path.join(results_directory, "summary_report.txt")
    first_command = True  # Track if it's the first command for summary report

    log_path = log_file
    if os.path.isfile(log_path):
        for rule_code, _, _, rule in rules:
            # Check if all placeholders in the rule exist in field_positions
            missing_fields = [
                field_name for field_name in field_positions.keys()
                if f"${{{field_name}}}" in rule and field_name not in field_positions
            ]
            if missing_fields:
                logging.warning(f"Skipping rule {rule_code} due to missing fields: {', '.join(missing_fields)}")
                continue
            
            # Replace placeholders like ${field_name} with corresponding field positions
            for field_name, position in field_positions.items():
                rule = rule.replace(f"${{{field_name}}}", str(position))
            
            # Properly quote the log file path
            formatted_command = rule.replace("{log_file}", f'"{log_path}"')
            output_file = summary_report_path if is_summary_report else os.path.join(results_directory, f"output_{os.path.basename(log_file)}.txt")
            
            try:
                logging.info(f"Executing rule {rule_code} on file {log_file}: {formatted_command}")
                with open(output_file, "a" if not is_summary_report or not first_command else "w") as out:
                    subprocess.run(formatted_command, shell=True, stdout=out, stderr=subprocess.PIPE, check=True)
                first_command = False  # After the first command, always append
            except subprocess.CalledProcessError as e:
                logging.error(f"Error executing rule {rule_code} on file {log_file}: {e}")
                print(f"Error executing rule {rule_code}. Check the log file for details.")

def get_valid_input(prompt, valid_options):
    """Prompt the user until they enter a valid option."""
    while True:
        choice = input(prompt).strip()
        if choice in valid_options:
            return choice
        print("Invalid selection. Please try again.")

def get_valid_directory():
    """Prompt the user until they enter a valid directory path."""
    while True:
        dir_input = input("Enter the target directory containing log files: ").strip()
        expanded_path = os.path.abspath(os.path.expanduser(dir_input))
        print(f"DEBUG: Expanded directory path: {expanded_path}")  # Debugging output
        if os.path.isdir(expanded_path):
            tapestry_log_path = os.path.join(expanded_path, "tapestry_logs.csv")
            print(f"DEBUG: Expected log file path: {tapestry_log_path}")  # Debugging output
            if os.path.exists(tapestry_log_path):
                return expanded_path, tapestry_log_path
            print(f"Error: Required file 'tapestry_logs.csv' not found in {expanded_path}.")
        else:
            print("Invalid directory. Please enter a valid path.")

def gather_field_placements(log_file):
    """Build a dictionary of field names and their numerical positions from the log file."""
    if not os.path.exists(log_file):
        print(f"Error: Log file '{log_file}' does not exist.")
        return {}

    # Properly quote the file path
    command = f"head -n 1 \"{log_file}\" | awk -F',' '{{for (i=1; i<=NF; i++) print $i, i}}'"
    print(f"DEBUG: Command to gather field placements: {command}")  # Debugging output
    field_positions = {}
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        print(f"DEBUG: Raw field placement output:\n{result}")  # Debugging output
        for line in result.strip().split("\n"):
            if " " not in line:
                continue  # Skip lines that don't have a field name and position
            field_name, position = line.rsplit(" ", 1)
            field_positions[field_name.strip()] = int(position)
        print("\nField Placements:\n", field_positions)  # Debugging output
        return field_positions
    except subprocess.CalledProcessError as e:
        print("Error gathering field placements:", e)
        return {}

def run_xgfw_unpacker(directory_path):
    """Run the xgfw_unpacker.py script with the specified directory path."""
    script_path = os.path.join(os.getcwd(), "xgfw_unpacker.py")
    if not os.path.exists(script_path):
        print(f"Error: xgfw_unpacker.py not found in {os.getcwd()}.")
        return

    # Use python3 explicitly
    command = f'python3 "{script_path}" "{directory_path}"'
    try:
        print(f"Running xgfw_unpacker.py on directory: {directory_path}")
        subprocess.run(command, shell=True, check=True)
        print("xgfw_unpacker.py executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running xgfw_unpacker.py: {e}")

def main():
    """Main menu system for Tapestry CLI."""
    display_splash()
    while True:
        print("\nTapestry - Log Analysis Tool")
        print("1. Log Analysis")
        print("2. Log Extraction")
        print("3. Manual")
        print("4. Exit")
        
        choice = get_valid_input("Select an option: ", ["1", "2", "3", "4"])
        if choice == "4":
            print("Exiting Tapestry. Goodbye!")
            return
        
        if choice == "2":
            print("\nLog Extraction:")
            print("1. XGFW Event Logs")
            print("2. Other (Not Implemented)")
            extraction_choice = get_valid_input("Select extraction type: ", ["1", "2"])
            
            if extraction_choice == "1":
                log_directory = input("Enter the directory containing .db files: ").strip()
                expanded_path = os.path.abspath(os.path.expanduser(log_directory))
                if os.path.isdir(expanded_path):
                    run_xgfw_unpacker(expanded_path)
                else:
                    print("Invalid directory. Please enter a valid path.")
            else:
                print("Only XGFW Event Logs extraction is implemented for now.")
            continue
        
        if choice != "1":
            print("Only Log Analysis is implemented for now.")
            continue
        
        print("\nLog Type Selection:")
        print("1. XGFW Event Logs")
        print("2. IIS")
        print("3. General FW (Experimental")
        print("4. General SSLVPN (Experimental)")
        log_type = get_valid_input("Select log type: ", ["1", "2", "3", "4"])
        
        print("\nAnalysis Choice:")
        print("1. Generate Summary Report")
        print("2. Run Rules File")
        print("3. Identifier Search (WIP)")
        analysis_choice = get_valid_input("Select analysis choice: ", ["1", "2"])
        
        log_directory, tapestry_log_path = get_valid_directory()
        
        rule_file = "rules.txt"  # Define the rule file name
        
        # Debugging Output: Show the values used to generate rule codes
        print("\nDEBUG: Rule Code Generation Values")
        print(f"Log Type: {log_type}, Analysis Choice: {analysis_choice}")
        
        # If XGFW Event Logs are selected, gather field placements
        field_positions = {}
        if log_type == "1":
            field_positions = gather_field_placements(tapestry_log_path)
        
        rules = load_rules(rule_file, int(log_type), int(analysis_choice))
        
        print("\nExecuting rules on logs...")
        is_summary_report = analysis_choice == "1"
        execute_rules(rules, tapestry_log_path, field_positions, is_summary_report)
        print(f"Log analysis completed. Check output files in: {os.path.join(os.getcwd(), 'Tapestry_Results')}")
    
if __name__ == "__main__":
    main()
