import streamlit as st
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
            return pd.DataFrame(), pd.DataFrame()
        if col not in eval_df.columns:
            st.error(f"Missing column in evaluation sheet: {col}")
            return pd.DataFrame(), pd.DataFrame()

    # Filter rows where status is 'Done'
    gold_df = gold_df[gold_df['Status'] == 'Done']
    eval_df = eval_df[eval_df['Status'] == 'Done']
    
    # Initialize counters and disagreement data
    decision_correct = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    mendel_id_correct = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    missing_concept_correct = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    parent_mendel_id_correct = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    decision_total = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    mendel_id_total = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    missing_concept_total = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    parent_mendel_id_total = {assignee: 0 for assignee in eval_df['Assignee'].unique()}
    disagreements = []

    # Align rows based on 'Code'
    for code in gold_df['Code'].unique():
        gold_row = gold_df[gold_df['Code'] == code]
        eval_row = eval_df[eval_df['Code'] == code]
        
        if not gold_row.empty and not eval_row.empty:
            eval_row = eval_row.iloc[0]
            gold_row = gold_row.iloc[0]
            assignee = eval_row['Assignee']
            
            decision_total[assignee] += 1
            mendel_id_total[assignee] += 1
            missing_concept_total[assignee] += 1
            parent_mendel_id_total[assignee] += 1

            disagreement_entry = {
                'Code': code,
                'Assignee': assignee,
                'Gold Decision': gold_row['Decision'],
                'Evaluated Decision': eval_row['Decision'],
                'Gold Mendel ID': gold_row['Mendel ID'],
                'Evaluated Mendel ID': eval_row['Mendel ID'],
                'Gold Missing Concept': gold_row['Missing Concept'],
                'Evaluated Missing Concept': eval_row['Missing Concept'],
                'Gold Parent Mendel ID If Missing Concept': gold_row['Parent Mendel ID If Missing Concept'],
                'Evaluated Parent Mendel ID If Missing Concept': eval_row['Parent Mendel ID If Missing Concept']
            }
            
            if gold_row['Decision'] == eval_row['Decision']:
                decision_correct[assignee] += 1
            if gold_row['Mendel ID'] == eval_row['Mendel ID']:
                mendel_id_correct[assignee] += 1
            if gold_row['Missing Concept'] == eval_row['Missing Concept']:
                missing_concept_correct[assignee] += 1
            if gold_row['Parent Mendel ID If Missing Concept'] == eval_row['Parent Mendel ID If Missing Concept']:
                parent_mendel_id_correct[assignee] += 1
                
            disagreements.append(disagreement_entry)

    # Calculate percentages
    results = []
    for assignee in eval_df['Assignee'].unique():
        decision_acc = (decision_correct[assignee] / decision_total[assignee]) * 100 if decision_total[assignee] > 0 else 0
        mendel_id_acc = (mendel_id_correct[assignee] / mendel_id_total[assignee]) * 100 if mendel_id_total[assignee] > 0 else 0
        missing_concept_acc = (missing_concept_correct[assignee] / missing_concept_total[assignee]) * 100 if missing_concept_total[assignee] > 0 else 0
        parent_mendel_id_acc = (parent_mendel_id_correct[assignee] / parent_mendel_id_total[assignee]) * 100 if parent_mendel_id_total[assignee] > 0 else 0
        results.append({
            'Assignee': assignee,
            'Evaluated Rows': decision_total[assignee],
            'Decision': f"{decision_acc:.2f}%",
            'Mendel ID': f"{mendel_id_acc:.2f}%",
            'Missing Concept': f"{missing_concept_acc:.2f}%",
            'Parent Mendel ID If Missing Concept': f"{parent_mendel_id_acc:.2f}%"
        })
    
    results_df = pd.DataFrame(results)
    disagreements_df = pd.DataFrame(disagreements)
    return results_df, disagreements_df

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
                
                if st.button("Start Evaluation"):
                    results_df, disagreements_df = evaluate(gold_df, eval_df)
                    if not results_df.empty:
                        st.write("Evaluation Results")
                        st.dataframe(results_df)
                        
                        csv = results_df.to_csv(index=False)
                        st.download_button("Download CSV", csv, "evaluation_results.csv", "text/csv")
                        
                        if not disagreements_df.empty:
                            st.write("Disagreements")
                            st.dataframe(disagreements_df)
                            
                            csv_disagreements = disagreements_df.to_csv(index=False)
                            st.download_button("Download Disagreements CSV", csv_disagreements, "disagreements.csv", "text/csv")
    
if __name__ == "__main__":
    main()
