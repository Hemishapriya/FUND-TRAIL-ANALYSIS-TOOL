import os
import sys
import pandas as pd
import pickle
from functools import lru_cache

# Attempt to find IFSC_CODES.xlsx in a few likely locations
POSSIBLE_PATHS = [
    'IFSC_CODES.xlsx',
    os.path.join('uploads', 'IFSC_CODES.xlsx'),
    os.path.join('instance', 'IFSC_CODES.xlsx')
]

if hasattr(sys, "_MEIPASS"):
    POSSIBLE_PATHS.insert(0, os.path.join(sys._MEIPASS, 'IFSC_CODES.xlsx'))
else:
    POSSIBLE_PATHS.insert(0, os.path.join(os.path.dirname(__file__), 'IFSC_CODES.xlsx'))


@lru_cache(maxsize=1)
def load_ifsc_table():
    # 1. Try to load from a pickle file first (fastest)
    for p in POSSIBLE_PATHS:
        pkl_path = os.path.splitext(p)[0] + '.pkl'
        if os.path.exists(pkl_path):
            try:
                with open(pkl_path, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                pass  # Fallback to Excel if pickle is corrupt/incompatible

    # 2. If no pickle, load Excel (slow) and save as pickle
    for p in POSSIBLE_PATHS:
        if os.path.exists(p):
            try:
                df = pd.read_excel(p, dtype=str)
                df = df.fillna('')
                # Normalize column names to a canonical set
                cols = {c.strip(): c for c in df.columns}
                # Build mapping from IFSC (upper) to row dict
                mapping = {}
                
                # Pre-calculate column names to avoid searching inside the loop
                ifsc_col = next((cols[c] for c in ['IFSC', 'Ifsc Code', 'Ifsc', 'IFSC Code'] if c in cols), None)
                if not ifsc_col:
                     # Fallback search
                     ifsc_col = next((c for c in df.columns if 'ifsc' in c.lower()), None)
                
                if not ifsc_col:
                    continue # Cannot process this file without IFSC column

                branch_col = next((c for c in ['BRANCH', 'Branch', 'BRANCH_NAME', 'Branch Name', 'BranchName', 'BRANCH NAME'] if c in cols), None)
                if not branch_col:
                     branch_col = next((c for c in df.columns if 'branch' in str(c).lower()), None)

                phone_col = next((c for c in ['Phone', 'PHONE', 'Contact', 'Telephone', 'Contact Number', 'Phone No', 'PhoneNumber'] if c in cols), None)
                if not phone_col:
                     phone_col = next((c for c in df.columns if 'phone' in str(c).lower() or 'contact' in str(c).lower() or 'tel' in str(c).lower()), None)

                # Use to_dict('records') for faster iteration than iterrows
                records = df.to_dict('records')
                
                for row in records:
                    ifsc_val = str(row.get(ifsc_col, '')).strip()
                    if not ifsc_val:
                        continue
                        
                    key = ifsc_val.upper()
                    
                    # Convert row keys to string and stripped
                    rowdict = {str(k).strip(): (v if v is not None else '') for k, v in row.items()}
                    
                    # Add normalized fields
                    rowdict['BRANCH'] = str(row.get(branch_col, '')).strip() if branch_col else ''
                    rowdict['PHONE'] = str(row.get(phone_col, '')).strip() if phone_col else ''
                    
                    mapping[key] = rowdict

                # Save to pickle for next time
                try:
                    pkl_out = os.path.splitext(p)[0] + '.pkl'
                    with open(pkl_out, 'wb') as f:
                        pickle.dump(mapping, f)
                except Exception as e:
                    print(f"Warning: Could not save IFSC cache to {pkl_out}: {e}")

                return mapping
            except Exception as e:
                print(f"Error loading IFSC Excel {p}: {e}")
                continue
    return {}


def get_ifsc_info(ifsc):
    if not ifsc:
        return None
    table = load_ifsc_table()
    return table.get(ifsc.upper())


def get_state(ifsc):
    if not ifsc:
        return 'Unknown'
    info = get_ifsc_info(ifsc)
    if not info:
        return 'Unknown'
    # try common state column names
    for key in ['STATE', 'State', 'STATE_NAME', 'state']:
        if key in info and info[key]:
            return str(info[key]).strip()
    return 'Unknown'
