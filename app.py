import streamlit as st
import pandas as pd

def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.ExcelFile(uploaded_file)
    return None

def evaluate(gold_df, eval_df):
    # Filter rows where status is 'Done'
    gold_df = gold_df[gold_df['Status'] == 'Done']
    eval_df = eval_df[eval_df['Status'] == 'Done']
    
    # Align rows based on 'Code'
    results = []
    for assignee in gold_df['Assignee'].unique():
        gold_rows = gold_df[gold_df['Assignee'] == assignee]
        eval_rows = eval_df[eval_df['Assignee'] == assignee]
        
        decision_correct = 0
        mendel_id_correct = 0
        missing_concept_correct = 0
        parent_mendel_id_correct = 0
        
        for code in gold_rows['Code']:
            gold_row = gold_rows[gold_rows['Code'] == code]
            eval_row = eval_rows[eval_rows['Code'] == code]
            
            if not eval_row.empty:
                eval_row = eval_row.iloc[0]
                gold_row = gold_row.iloc[0]
                
                if gold_row['Decision'] == eval_row['Decision']:
                    decision_correct += 1
                    if gold_row['Mendel ID'] == eval_row['Mendel ID']:
                        mendel_id_correct += 1
                        if gold_row['Missing Concept'] == eval_row['Missing Concept']:
                            missing_concept_correct += 1
                            if gold_row['Parent Mendel ID If Missing Concept'] == eval_row['Parent Mendel ID If Missing Concept']:
                                parent_mendel_id_correct += 1
        
        total = len(gold_rows)
        if total > 0:
            results.append({
                'Assignee': assignee,
                'Decision': f"{(decision_correct / total) * 100:.2f}%",
                'Mendel ID': f"{(mendel_id_correct / total) * 100:.2f}%",
                'Missing Concept': f"{(missing_concept_correct / total) * 100:.2f}%",
                'Parent Mendel ID If Missing Concept': f"{(parent_mendel_id_correct / total) * 100:.2f}%"
            })
    
    results_df = pd.DataFrame(results)
    return results_df

def main():
    st.title("Sheet Comparison App")
    
    st.sidebar.header("Upload Sheets")
    gold_file = st.sidebar.file_uploader("Upload Gold Sheet", type=["xlsx"])
    eval_file = st.sidebar.file_uploader("Upload Evaluation Sheet", type=["xlsx"])
    
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
                st.write("Evaluation Results")
                st.dataframe(results_df)
                
                csv = results_df.to_csv(index=False)
                st.download_button("Download CSV", csv, "evaluation_results.csv", "text/csv")
    
if __name__ == "__main__":
    main()
