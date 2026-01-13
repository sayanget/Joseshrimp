
import sys
import os
from datetime import datetime, date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db
from app.models import Memo

def verify_memo_edit():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Setup
        Memo.query.filter(Memo.created_by == 'test_verifier_edit').delete()
        
        memo = Memo(content="Original Content", memo_date=date.today(), created_by='test_verifier_edit')
        db.session.add(memo)
        db.session.commit()
        
        print(f"Created Memo {memo.id}: {memo.content}")
        
        # Test Edit
        memo.content = "Edited Content"
        db.session.commit()
        
        updated = Memo.query.get(memo.id)
        assert updated.content == "Edited Content"
        print(f"Verified Update: {updated.content}")
        
        # Cleanup
        db.session.delete(updated)
        db.session.commit()
        print("Verification Passed")

if __name__ == "__main__":
    verify_memo_edit()
