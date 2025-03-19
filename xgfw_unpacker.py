import os
import sqlite3
import json
import csv
import argparse

"""
This Module is used to convert all .db files from the event logs directory of an XGFW into parsable .csv files. Each row 
in tbllog is stored as a JSON object inside a single column. My solution to misalligned columns between .db files on export 
requires we scan all .db files to collect a universal set of JSON keys. Returns a sorted list of unique column names. Super 
time intensive but the best solution without a .db schema and should be flexible for any updated version changes.
"""

def get_all_column_names(directory_path):

    all_columns = set()
    total_files = len([f for f in os.listdir(directory_path) if f.endswith(".db")])

    print(f"Scanning {total_files} database files to determine universal column headers...")

    for i, filename in enumerate(os.listdir(directory_path), start=1):
        if filename.endswith(".db"):
            db_path = os.path.join(directory_path, filename)
            print(f"[{i}/{total_files}] Processing: {filename}")

            try:
                conn = sqlite3.connect(db_path)
                c = conn.cursor()

                c.execute("SELECT * FROM tbllog")
                data = c.fetchall()

                for row in data:
                    try:
                        json_data = json.loads(row[0])  # Extract JSON object
                        all_columns.update(json_data.keys())  # Collect unique keys
                    except json.JSONDecodeError:
                        print(f"⚠️  Skipping non-JSON row in {filename}")

                conn.close()

            except sqlite3.Error as e:
                print(f"❌ Error processing {filename}: {e}")

    return sorted(all_columns)  # Sort columns for consistency

def export_data_to_csv(directory_path, universal_columns):
    """
    Exports data from each .db file to build the universal header.
    Outputs all CSVs into a new 'converted' directory inside the current working directory.
    """
    output_dir = os.path.join(os.getcwd(), "converted")
    os.makedirs(output_dir, exist_ok=True)  # Create 'converted' folder if it doesn't exist

    total_files = len([f for f in os.listdir(directory_path) if f.endswith(".db")])
    print(f"\nExporting {total_files} databases to CSV format in '{output_dir}'...\n")

    for i, filename in enumerate(os.listdir(directory_path), start=1):
        if filename.endswith(".db"):
            db_path = os.path.join(directory_path, filename)
            csv_filename = os.path.splitext(filename)[0] + ".csv"
            csv_path = os.path.join(output_dir, csv_filename)

            print(f"[{i}/{total_files}] Converting: {filename} → {csv_filename}")

            try:
                conn = sqlite3.connect(db_path)
                c = conn.cursor()

                c.execute("SELECT * FROM tbllog")
                data = c.fetchall()

                csv_data = [universal_columns]  # Start CSV with universal headers

                for row in data:
                    try:
                        json_data = json.loads(row[0])
                        csv_row = [json_data.get(col, "") for col in universal_columns]
                        csv_data.append(csv_row)
                    except json.JSONDecodeError:
                        print(f"⚠️  Skipping invalid JSON row in {filename}")

                with open(csv_path, "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(csv_data)

                print(f"✅ Exported: {csv_filename}")

            except sqlite3.Error as e:
                print(f"❌ Error processing {filename}: {e}")

            finally:
                conn.close()

def concatenate_csv_files(output_dir, output_filename="tapestry_logs.csv"):
    """
    Concatenates all CSV files in the output directory into a single CSV file.
    """
    output_path = os.path.join(output_dir, output_filename)
    csv_files = [f for f in os.listdir(output_dir) if f.endswith(".csv")]

    print(f"\nConcatenating {len(csv_files)} CSV files into '{output_filename}'...\n")

    with open(output_path, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        header_written = False

        for index, csv_file in enumerate(csv_files, start=1):
            print(f"[{index}/{len(csv_files)}] Processing: {csv_file}")
            csv_path = os.path.join(output_dir, csv_file)
            with open(csv_path, "r") as infile:
                reader = csv.reader(infile)
                for i, row in enumerate(reader):
                    if i == 0 and header_written:
                        continue  # Skip header row if already written
                    writer.writerow(row)
            header_written = True

    print(f"✅ All CSV files concatenated into '{output_filename}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export data from SQLite .db files matching JSON field to CSV header.")
    parser.add_argument("directory_path", help="Path to the directory containing the .db files.")
    args = parser.parse_args()

    # Step 1: Collect universal column names
    universal_columns = get_all_column_names(args.directory_path)

    # Step 2: Export data to CSV using the universal column headers
    export_data_to_csv(args.directory_path, universal_columns)

    # Step 3: Concatenate all CSV files into a single output file
    output_dir = os.path.join(os.getcwd(), "converted")
    concatenate_csv_files(output_dir)

    print("\n Conversion complete! All CSV files are in the 'converted' folder.\n")