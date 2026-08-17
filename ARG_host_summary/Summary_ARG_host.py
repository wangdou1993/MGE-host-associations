import pandas as pd
import os

### First, extract rows based on host ID to avoid duplicate counting when calculating host abundance. Then split the taxonomy annotations into separate columns, and calculate the abundance of a specific taxa at each level (e.g., phylum)
# Define folder path
folder_path = "0-ARG-host-info"
# Define output folder path
output_folder_path = "1-amr-host-summary"
# Create output folder if it does not exist
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# Get all TSV file names in the folder
tsv_files = [f for f in os.listdir(folder_path) if f.endswith('.tsv')]

# Iterate through each TSV file
for tsv_file in tsv_files:
    # Construct the full file path
    file_path = os.path.join(folder_path, tsv_file)

    # Read the TSV file
    data = pd.read_csv(file_path, sep='\t')

    # Keep rows with unique values in the 30th column
    data_unique = data.drop_duplicates(subset=data.columns[29])

    # Split the 35th column elements by ";" and fill into subsequent columns
    #data_unique[data.columns[28]] = data_unique[data.columns[28]].astype(str)
    split_columns = data_unique.iloc[:, 34].str.split(';', expand=True)

    # Remove empty rows from the split columns
    split_columns = split_columns.apply(lambda col: col.dropna().reset_index(drop=True))

    # Add the split columns to the original dataframe
    data_with_splits = pd.concat([data_unique.reset_index(drop=True), split_columns], axis=1)

    # Get abundance values from the 32nd column
    abundance_values = data_with_splits.iloc[:, 31]

    # Create a dictionary to store the sum of identical elements from the split columns
    element_sums = {}

    # Iterate through each split column
    for col in split_columns.columns:
        for element in data_with_splits[col].dropna().unique():
            element_sum = data_with_splits[data_with_splits[col] == element][abundance_values.name].sum()
            if element in element_sums:
                element_sums[element] += element_sum
            else:
                element_sums[element] = element_sum

    # Create a DataFrame to store each element and its sum
    result_data = []
    for element, total_sum in element_sums.items():
        result_data.append({
            'Element': element,
            'Sum': total_sum
        })

    result_df = pd.DataFrame(result_data)

    # Create a new DataFrame to store element names and their sums from different columns
    final_result = pd.DataFrame()

    for i, col in enumerate(split_columns.columns):
        col_result = result_df[result_df['Element'].isin(data_with_splits[col].dropna().unique())].copy()
        col_result.columns = [f'Element_{i + 1}', f'Sum_{i + 1}']
        final_result = pd.concat([final_result, col_result.reset_index(drop=True)], axis=1)

    # Save the results to a new TSV file
    result_file_name = f"{os.path.splitext(tsv_file)[0]}_output_with_sums.tsv"
    result_file_path = os.path.join(output_folder_path, result_file_name)
    final_result.to_csv(result_file_path, sep='\t', index=False)
    print(f"Element sums saved to {result_file_path}")

    # Save the data with calculation results to split_output_file as well
    for i, col in enumerate(split_columns.columns):
        col_result = result_df[result_df['Element'].isin(data_with_splits[col].dropna().unique())].copy()
        col_result.columns = [f'Element_{i + 1}', f'Sum_{i + 1}']
        data_with_splits = pd.concat([data_with_splits, col_result.reset_index(drop=True)], axis=1)

    # Save the data with calculation results to a new TSV file
    split_output_file_name = f"{os.path.splitext(tsv_file)[0]}_split_output_with_sums.tsv"
    split_output_file_path = os.path.join(output_folder_path, split_output_file_name)
    data_with_splits.to_csv(split_output_file_path, sep='\t', index=False)
    print(f"Data with calculation results saved to {split_output_file_path}")


### Merge the host abundance results calculated at each taxonomic level by sample
# Define folder path
sum_input_folder_path = "1-amr-host-summary"
# Define output folder path
combine_output_folder_path = "2-combine-all-sample-taxa"
# Create output folder if it does not exist
if not os.path.exists(combine_output_folder_path):
    os.makedirs(combine_output_folder_path)

# Create a dictionary to store extracted results for each group of columns
combined_dict = {}

# Iterate through the generated output files, extracting every two columns into the master DataFrame
output_files = [f for f in os.listdir(sum_input_folder_path) if f.endswith('-host_taxa_output_with_sums.tsv')]

for output_file in output_files:
    # Construct the full file path
    output_file_path = os.path.join(sum_input_folder_path, output_file)

    # Read the TSV file
    data = pd.read_csv(output_file_path, sep='\t')

    # Get the original file name (remove _split_output_with_sums.xlsx part)
    base_file_name = os.path.splitext(output_file)[0].replace('-host_taxa_output_with_sums', '')

    # Iterate through the dataframe columns, extracting every two columns
    for i in range(0, data.shape[1], 2):
        # Extract the current two columns
        extracted_columns = data.iloc[:, i:i + 2].copy()

        # Rename columns with the original file name
        extracted_columns.columns = [f'{base_file_name}_col_{i + 1}', f'{base_file_name}_col_{i + 2}']

        # Construct a key to identify each pair of columns
        key = f'columns_{i + 1}_{i + 2}'

        # If the key does not exist in the dictionary, create a new DataFrame
        if key not in combined_dict:
            combined_dict[key] = extracted_columns
        else:
            # Otherwise, add the current extracted columns to the existing DataFrame
            combined_dict[key] = pd.concat([combined_dict[key], extracted_columns], axis=1)

# Save each combined DataFrame to a new TSV file
for key, df in combined_dict.items():
    output_file_name = f'{key}_combined.tsv'
    output_file_path = os.path.join(combine_output_folder_path, output_file_name)
    df.to_csv(output_file_path, sep='\t', index=False)
    print(f'Extracted columns saved to {output_file_path}')


### Summarize all classifications at a given taxonomic level into a matrix
# Define input folder path
combine_input_folder_path = "2-combine-all-sample-taxa"
# Define output folder path
di_taxa_output_folder_path = "3-summarize-di-taxa"

# Create output folder if it does not exist
if not os.path.exists(di_taxa_output_folder_path):
    os.makedirs(di_taxa_output_folder_path)

# Process the generated files for gene names and gene abundances
combined_files = [f for f in os.listdir(combine_input_folder_path) if f.endswith('_combined.tsv')]

for combined_file in combined_files:
    # Construct the full file path
    combined_file_path = os.path.join(combine_input_folder_path, combined_file)

    # Read the TSV file
    data = pd.read_csv(combined_file_path, sep='\t')

    # Get the header row
    header = data.columns

    # Split the data into gene names and gene abundances
    genes = data.iloc[:, 0::2]
    abundances = data.iloc[:, 1::2]

    # Get the set of all unique genes, excluding blanks and non-string types
    all_genes = pd.unique(genes.values.ravel())
    all_genes = [gene for gene in all_genes if isinstance(gene, str) and gene.strip()]

    # Create a new DataFrame to store gene names and abundance across all samples
    result = pd.DataFrame(columns=["Gene"] + list(header[1::2]))
    result["Gene"] = all_genes

    # Iterate through each sample's gene abundance and add it to the result DataFrame
    for col_num in range(len(abundances.columns)):
        sample_abundance = abundances.iloc[:, col_num]
        sample_genes = genes.iloc[:, col_num]

        for index, gene in enumerate(sample_genes):
            if isinstance(gene, str) and gene.strip():  # Ensure gene name is valid
                abundance = sample_abundance.iloc[index]
                result.loc[result["Gene"] == gene, header[2 * col_num + 1]] = abundance

    # Fill missing values with 0
    result.fillna(0, inplace=True)

    # Ensure object types are correct
    result = result.infer_objects()

    # Save the result to a new TSV file
    output_file_name = f"summarized_{os.path.splitext(combined_file)[0]}.tsv"
    output_file_path = os.path.join(di_taxa_output_folder_path, output_file_name)
    result.to_csv(output_file_path, sep='\t', index=False)
    print(f"Results saved to {output_file_path}")