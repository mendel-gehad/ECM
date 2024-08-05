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
    for code in gold_df['Code']:
        gold_row = gold_df[gold_df['Code'] == code]
        eval_row = eval_df[eval_df['Code'] == code]
        
        if not eval_row.empty:
            eval_row = eval_row.iloc[0]
            gold_row = gold_row.iloc[0]
            
            result = {'Code': code}
            if gold_row['Decision'] == eval_row['Decision']:
                result['Decision'] = 'Correct'
                if gold_row['Mendel ID'] == eval_row['Mendel ID']:
                    result['Mendel ID'] = 'Correct'
                    if gold_row['Missing Concept'] == eval_row['Missing Concept']:
                        result['Missing Concept'] = 'Correct'
                        if gold_row['Parent Mendel ID If Missing Concept'] == eval_row['Parent Mendel ID If Missing Concept']:
                            result['Parent Mendel ID If Missing Concept'] = 'Correct'
                        else:
                            result['Parent Mendel ID If Missing Concept'] = 'Incorrect'
                    else:
                        result['Missing Concept'] = 'Incorrect'
                else:
                    result['Mendel ID'] = 'Incorrect'
            else:
                result['Decision'] = 'Incorrect'
            results.append(result)
    
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
