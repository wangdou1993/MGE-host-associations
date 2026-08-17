import os
import csv
import glob
from collections import defaultdict
import pandas as pd


def detect_delimiter(file_path, sample_size=1024):
    """Automatically detect the file delimiter"""
    delimiters = [',', '\t', ';', '|', ' ']
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        sample = f.read(sample_size)
    # Count the frequency of each delimiter
    delimiter_counts = {delim: sample.count(delim) for delim in delimiters}
    # Select the delimiter with the highest frequency
    detected_delim = max(delimiter_counts, key=delimiter_counts.get)
    return detected_delim if delimiter_counts[detected_delim] > 0 else '\t'


def process_file(file_path, output_dir, columns_to_analyze):
    """Process a single file, count specified columns and output results"""
    try:
        # Get filename
        filename = os.path.basename(file_path)

        # Detect delimiter
        delimiter = detect_delimiter(file_path)

        # Read file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f, delimiter=delimiter)
            header = next(reader)

            # Check if the columns to be analyzed exist
            valid_columns = {}
            for col in columns_to_analyze:
                try:
                    col_index = header.index(col)
                    valid_columns[col] = col_index
                except ValueError:
                    print(f"⚠️ Warning: Column '{col}' not found in {filename}")

            # If no valid columns found, skip this file
            if not valid_columns:
                print(f"⚠️ Warning: No specified columns found in {filename}, skipping file")
                return {}

            # Initialize counters
            counters = {col: defaultdict(int) for col in valid_columns}

            # Count data
            for row in reader:
                for col, col_index in valid_columns.items():
                    if len(row) > col_index:
                        col_val = row[col_index].strip()
                        if col_val:  # Ignore empty values
                            counters[col][col_val] += 1

        # Output results
        results = {}
        for col, counter in counters.items():
            if counter:
                # Create column-specific output directory
                col_output_dir = os.path.join(output_dir, f"{col}_Stats")
                os.makedirs(col_output_dir, exist_ok=True)

                # Create output file path
                output_file = os.path.join(col_output_dir, f"{os.path.splitext(filename)[0]}_{col}_count.tsv")

                # Write statistics results
                with open(output_file, 'w', encoding='utf-8', newline='') as out_f:
                    writer = csv.writer(out_f, delimiter='\t')
                    writer.writerow([f"{col} Value", "Count", "Percentage(%)"])

                    total = sum(counter.values())
                    for val, count in sorted(counter.items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / total) * 100
                        writer.writerow([val, count, f"{percentage:.2f}"])

                    # Add total row
                    writer.writerow(["Total", total, "100.00"])

                print(f"✅ Created: {output_file}")
                results[col] = {
                    "counts": counter,
                    "total": total,
                    "filename": filename
                }
            else:
                print(f"⚠️ Warning: No valid '{col}' values in {filename}")

        return results

    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return {}


def create_summary_report(all_file_stats, output_dir, column_name):
    """Create a comprehensive summary report merging all file results for the specified column"""
    # Collect all unique values
    all_values = set()
    for file_stats in all_file_stats.values():
        if column_name in file_stats:
            all_values.update(file_stats[column_name]["counts"].keys())

    # If no data, skip
    if not all_values:
        print(f"⚠️ Warning: No valid '{column_name}' values found, skipping summary report")
        return

    # Sort values alphabetically
    sorted_values = sorted(all_values)

    # Prepare summary data - counts table
    counts_data = []
    percentages_data = []

    # Calculate global total
    global_total = 0

    # Prepare file data
    for filename, col_stats in all_file_stats.items():
        if column_name not in col_stats:
            continue

        stats = col_stats[column_name]
        counts_row = {"Filename": filename}
        percentages_row = {"Filename": filename}

        file_total = stats["total"]
        global_total += file_total

        for val in sorted_values:
            count = stats["counts"].get(val, 0)
            counts_row[val] = count
            percentages_row[val] = f"{(count / file_total * 100):.2f}%" if count > 0 else "0.00%"

        counts_row["Total"] = file_total
        percentages_row["Total"] = file_total

        counts_data.append(counts_row)
        percentages_data.append(percentages_row)

    # If no valid data, skip
    if not counts_data:
        print(f"⚠️ Warning: No valid '{column_name}' data, skipping summary report")
        return

    # Add global summary row - counts table
    counts_summary = {"Filename": "Global Summary"}
    for val in sorted_values:
        total_count = sum(row.get(val, 0) for row in counts_data)
        counts_summary[val] = total_count
    counts_summary["Total"] = global_total
    counts_data.append(counts_summary)

    # Add global summary row - percentages table
    percentages_summary = {"Filename": "Global Percentage"}
    for val in sorted_values:
        total_count = sum(row.get(val, 0) for row in counts_data[:-1])  # Exclude the last row
        global_percentage = (total_count / global_total * 100) if global_total > 0 else 0
        percentages_summary[val] = f"{global_percentage:.2f}%"
    percentages_summary["Total"] = ""
    percentages_data.append(percentages_summary)

    # Create DataFrames
    df_counts = pd.DataFrame(counts_data)
    df_percentages = pd.DataFrame(percentages_data)

    # Set column order
    columns = ["Filename"] + sorted_values + ["Total"]
    df_counts = df_counts[columns]
    df_percentages = df_percentages[columns]

    # Create column-specific output directory
    col_output_dir = os.path.join(output_dir, f"{column_name}_Stats")
    os.makedirs(col_output_dir, exist_ok=True)

    # Save to Excel (two worksheets)
    excel_file = os.path.join(col_output_dir, f"{column_name}_Summary_Report.xlsx")
    with pd.ExcelWriter(excel_file) as writer:
        df_counts.to_excel(writer, sheet_name="Count Statistics", index=False)
        df_percentages.to_excel(writer, sheet_name="Percentage Statistics", index=False)

    # Save TSV version (counts only)
    tsv_file = os.path.join(col_output_dir, f"{column_name}_Summary_Report_Counts.tsv")
    df_counts.to_csv(tsv_file, sep='\t', index=False)

    print(f"✅ Created {column_name} summary report: {excel_file}")
    print(f"✅ Created {column_name} TSV summary: {tsv_file}")


def main():
    # Configure input path
    input_dir = input("Please enter the folder path containing data files: ").strip()
    if not os.path.isdir(input_dir):
        print(f"❌ Error: Folder '{input_dir}' does not exist")
        return

    # Configure output path
    default_output_dir = os.path.join(os.getcwd(), "MultiColumn_Stats")
    output_dir = input(f"Please enter output folder path (press Enter to use default '{default_output_dir}'): ").strip()
    output_dir = output_dir or default_output_dir
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Output folder: {output_dir}")

    # Get column names to analyze
    default_columns = "Type,location,rank"
    columns_input = input(
        f"Please enter column names to analyze (comma-separated) (press Enter to use default '{default_columns}'): ").strip()
    columns_to_analyze = [col.strip() for col in
                          (columns_input.split(',') if columns_input else default_columns.split(','))]
    print(f"📊 Will analyze the following columns: {', '.join(columns_to_analyze)}")

    # Store statistics results for all files
    all_file_stats = defaultdict(dict)

    # Process all files
    processed_files = 0

    # Get all files
    all_files = []
    for root, _, files in os.walk(input_dir):
        # Skip output directory
        if root.startswith(output_dir):
            continue

        for file in files:
            # Skip possible output files
            if any(file.endswith(ext) for ext in ('_count.tsv', '_Report.xlsx', '_Report.tsv')):
                continue

            file_path = os.path.join(root, file)
            all_files.append(file_path)

    print(f"🔍 Found {len(all_files)} files to process")

    for file_path in all_files:
        if os.path.isfile(file_path):
            results = process_file(file_path, output_dir, columns_to_analyze)
            if results:
                for col, stats in results.items():
                    all_file_stats[file_path][col] = stats
                processed_files += 1

    # Create summary reports for each column
    if all_file_stats:
        print("\n📈 Generating summary reports...")
        for col in columns_to_analyze:
            create_summary_report(all_file_stats, output_dir, col)

        print(f"\n✅ Processing complete! Processed {processed_files} files")

        # Display output file structure
        print("\n📂 Output file structure:")
        for root, dirs, files in os.walk(output_dir):
            level = root.replace(output_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                print(f"{subindent}{f}")
    else:
        print("⚠️ No files containing valid columns were found")


if __name__ == "__main__":
    main()