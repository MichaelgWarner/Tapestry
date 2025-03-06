grep header values for awk
```bash
grep -E 'start_time' combinedlog.csv | awk -F',' '{for (i=1; i<=NF; i++) print i, $i}'
```

Regex grep to find time range
```bash
grep -Eo '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' combinedlog.csv | sort | awk 'NR==1{print "Earliest timestamp:", $0} END{print "Latest timestamp:", $0}'
```

regex to grep all logs referencing IOC addresses, pipe to print status, dst ip, src ip, time, message, subtype
```bash
grep -E '96\.126\.110\.74|103\.188\.234\.230|144\.48\.80\.122|167\.172\.77\.157|172\.105\.158\.219|198\.167\.193\.[0-9]{1,3}|200\.73\.8\.20' combinedlog.csv | awk -F',' '{print $3, $5, $29, $53, $77, $82}'
```

For all traffic involving DEMONEXCH2, Awk all src IP, clean src column, exclude private IP's, sort and count occurrences
```bash
grep -E '72\.175\.210\.194|172\.16\.16\.16' combinedlog.csv | awk -F',' '{print $56}' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' | grep -Ev '^(10\..*|192\.168\..*|172\.(1[6-9]|2[0-9]|3[0-1])\..*)' | sort | uniq -c | sort
```

cat wildcard log path in cwd
```bash
cat *.log > combinedlogs.txt
```

```bash
awk 'pattern { action }' filename
```
- This is the general structure of an `awk` command.
- It means: "If a line matches `pattern`, perform `action` on it."
- Example: `awk '/error/ {print $0}' log.txt` prints all lines containing "error" from `log.txt`.

```bash
awk -F ","
```
- This tells `awk` to use a **comma (`,`)** as the field separator instead of the default (which is spaces or tabs).
- Example: If you have a CSV file, `awk -F "," '{print $1}' file.csv` will print the first column.

```bash
awk '{print $1, $2, $3}' log_file.log
```
- This prints only the first three columns (fields) from each line of `log_file.log`.
- Example: If a line is `2024-01-01 12:30:00 INFO Process started`, it prints `2024-01-01 12:30:00`.

```bash
awk '$3 == "STRING" {print $0}' log_file.log
```
- This prints the entire line (`$0`) if the third column (`$3`) is exactly `"STRING"`.
- Example: If a line is `2024-01-01 12:30:00 ERROR Process failed` and you search for `ERROR`, it prints that line.

```bash
awk '$3 == "STRING" {count++} END {print count}' log_file.log
```
- This counts how many times `"STRING"` appears in the third column and prints the total at the end.
- Example: If `"ERROR"` appears in `$3` five times, it prints `5`.

```bash
awk '$1 == "2024-01-01" && $2 >= "10:00:00" && $2 <= "11:00:00" {print $0}' log_file.log
```
- This prints lines where:
    - The first column (`$1`) is `"2024-01-01"`
    - The second column (`$2`, which is time) is between `"10:00:00"` and `"11:00:00"`.
- Useful for extracting logs within a specific date and time range.


```bash
grep -o 'src=[^ ]*' "log_file.csv" | cut -d '=' -f 2 | sort | uniq > unique_src_values.txt
```
- **`grep -o 'src=[^ ]*' "log_file.csv"`**
    
    - `grep` searches for **`src=`** followed by any characters except spaces (`[^ ]*`).
    - The `-o` option ensures only the **matching part** (e.g., `src=192.168.1.1`) is extracted.
- **`cut -d '=' -f 2`**
    
    - `cut` splits the extracted text by the `=` delimiter and keeps the **second part** (`f 2`), which is the **actual source value** (e.g., `192.168.1.1`).
- **`sort`**
    
    - Sorts the extracted values in ascending order.
- **`uniq`**
    
    - Removes duplicate entries, keeping only unique `src` values.
- **`> unique_src_values.txt`**
    
    - Saves the result into `unique_src_values.txt`.

```bash
grep -o 'dst=[^ ]*' "firewall.csv" | cut -d '=' -f 2 | sort | uniq > unique_dst_values.txt
```
- **Same process** as the `src` extraction, but this time for `dst=` (destination values).

REGEX Operators
```
[ ]
```
Defines a **character class**, meaning it will match any one character that is included inside.
```
^
```
Means **negation**, so it matches anything **except** the characters inside the brackets.
```
*
```
Matches **zero or more** of the preceding pattern (i.e., any character except space).

Useful REGEX Samples
```
[^ ]*
```
Match a character, everything except space - zero or more.
When used inside of a firewall log that formats directionality as `src=192.168.0.1` This ensures that we only capture the value of src= without extra words. You can replace the space with whichever character is used to delimit the line between columns to effectively "select all up to the chosen character"
