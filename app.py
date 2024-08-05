limport streamlit as st
import pandas as pd

def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.ExcelFile(uploaded_file)
    return None

def evaluate(gold_df, eval_df):
    # Ensure consistent column names
    gold_df.columns = gold_df.columns.str.strip()
    eval_df.columns = eval_df.columns.str.strip()

    # Define the required columns
    required_columns = [
        'Code', 'Decision', 'Mendel ID', 'Missing Concept', 
        'Parent Mendel ID If Missing Concept', 'Assignee', 'Status'
    ]

    # Check for missing columns
    for col in required_columns:
        if col not in gold_df.columns:
            st.error(f"Missing column in gold standard sheet: {col}")
            return pd.DataFrame()
        if col not in eval_df.columns:
            st.error(f"Missing column in evaluation sheet: {col}")
            return pd.DataFrame()

    # Filter rows where status is 'Done'
    gold_df = gold_df[gold_df['Status'] == 'Done']
    eval_df = eval_df[eval_df['Status'] == 'Done']
    
    # Initialize counters
    decision_correct = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    mendel_id_correct = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    missing_concept_correct = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    parent_mendel_id_correct = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    total_counts = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    
    # Align rows based on 'Code'
    for code in gold_df['Code']:
        gold_row = gold_df[gold_df['Code'] == code]
        eval_row = eval_df[eval_df['Code'] == code]
        
        if not gold_row.empty and not eval_row.empty:
            eval_row = eval_row.iloc[0]
            gold_row = gold_row.iloc[0]
            assignee = eval_row['Assignee']
            
            total_counts[assignee] += 1
            
            if gold_row['Decision'] == eval_row['Decision']:
                decision_correct[assignee] += 1
                if gold_row['Mendel ID'] == eval_row['Mendel ID']:
                    mendel_id_correct[assignee] += 1
                    if gold_row['Missing Concept'] == eval_row['Missing Concept']:
                        missing_concept_correct[assignee] += 1
                        if gold_row['Parent Mendel ID If Missing Concept'] == eval_row['Parent Mendel ID If Missing Concept']:
                            parent_mendel_id_correct[assignee] += 1
    
    # Calculate percentages
    results = []
    for assignee in gold_df['Assignee'].unique():
        total = total_counts[assignee]
        if total > 0:
            results.append({
                'Assignee': assignee,
                'Evaluated Rows': total,
                'Decision': f"{(decision_correct[assignee] / total) * 100:.2f}%",
                'Mendel ID': f"{(mendel_id_correct[assignee] / total) * 100:.2f}%",
                'Missing Concept': f"{(missing_concept_correct[assignee] / total) * 100:.2f}%",
                'Parent Mendel ID If Missing Concept': f"{(parent_mendel_id_correct[assignee] / total) * 100:.2f}%"
            })
    
    results_df = pd.DataFrame(results)
    return results_df

def main():
    st.title("ECM Comparison")
    
    st.sidebar.header("Upload Sheets")
    gold_file = st.sidebar.file_uploader("Upload Gold Sheet", type=["xlsx"])
    eval_file = st.sidebar.file_uploader("Upload Evaluated Sheet", type=["xlsx"])
    
    if gold_file and eval_file:
        gold_xls = load_data(gold_file)
        eval_xls = load_data(eval_file)
        
        if gold_xls is not None and eval_xls is not None:
            gold_sheets = gold_xls.sheet_names
            eval_sheets = eval_xls.sheet_names
            
            tab_selection = st.selectbox("Select Tab to Evaluate", gold_sheets)
            
            if tab_selection:
                st.write(f"Evaluating Tab: {tab_selection}")
                gold_df = gold_xls.parse(tab_selection)
                eval_df = eval_xls.parse(tab_selection)
                
                results_df = evaluate(gold_df, eval_df)
                if not results_df.empty:
                    st.write("Evaluation Results")
                    st.dataframe(results_df)
                    
                    csv = results_df.to_csv(index=False)
                    st.download_button("Download CSV", csv, "evaluation_results.csv", "text/csv")
    
if __name__ == "__main__":
    main()
