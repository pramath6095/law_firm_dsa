"""
Fix Status for Existing Cases
Run this once to update status of already-claimed cases
"""

# This is a manual fix - paste this into Python console while backend is running
# Or add it temporarily to app.py initialization

# Add this function to app.py after init_sample_data():

def fix_existing_case_statuses():
    """One-time fix: Update status for cases that were claimed before status update feature"""
    for case_id, case in case_store.cases.items():
        # If case has a lawyer but status is still 'created', update to 'in_review'
        if case.get('lawyer_id') and case.get('status') == 'created':
            case['status'] = 'in_review'
            case['updated_at'] = datetime.now().isoformat()
            case_store.cases[case_id] = case
            print(f"Updated {case_id} status to 'in_review'")

# Call it once when backend starts (add after init_sample_data() call):
# fix_existing_case_statuses()
