import os
import subprocess

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
            
            parts = line.split("|")
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

def execute_rules(rules, log_directory):
    """Execute the given list of rules on the log files in the specified directory."""
    # Create results directory inside the current working directory
    results_directory = os.path.join(os.getcwd(), "Tapestry_Results")
    os.makedirs(results_directory, exist_ok=True)
    
    for log_file in os.listdir(log_directory):
        log_path = os.path.join(log_directory, log_file)
        if os.path.isfile(log_path):
            for rule_code, _, _, rule in rules:
                formatted_command = rule.replace("{log_file}", log_path)
                output_file = os.path.join(results_directory, f"output_{os.path.basename(log_file)}.txt")
                print(f"Executing ({rule_code}): {formatted_command}")
                with open(output_file, "a") as out:
                    subprocess.run(formatted_command, shell=True, stdout=out, stderr=subprocess.DEVNULL)

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
        if os.path.isdir(expanded_path):
            return expanded_path
        print("Invalid directory. Please enter a valid path.")

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
        
        log_directory = get_valid_directory()
        
        rule_file = "rules.txt"  # Define the rule file name
        
        # Debugging Output: Show the values used to generate rule codes
        print("\nDEBUG: Rule Code Generation Values")
        print(f"Log Type: {log_type}, Analysis Choice: {analysis_choice}")
        
        rules = load_rules(rule_file, int(log_type), int(analysis_choice))
        
        print("\nExecuting rules on logs...")
        execute_rules(rules, log_directory)
        print(f"Log analysis completed. Check output files in: {os.path.join(os.getcwd(), 'Tapestry_Results')}")
    
if __name__ == "__main__":
    main()
