
import sys
import os
from datetime import datetime, date

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Memo

def verify_memo_feature():
    app = create_app('testing')
    with app.app_context():
        print("1. Creating Memo Table if not exists...")
        db.create_all()
        
        # Cleanup previous test data
        Memo.query.filter(Memo.created_by == 'test_verifier').delete()
        db.session.commit()
        
        print("2. Testing Create Memo...")
        today = date.today()
        memo1 = Memo(
            content="Test Memo 1",
            memo_date=today,
            created_by='test_verifier'
        )
        db.session.add(memo1)
        db.session.commit()
        print(f"   Created Memo ID: {memo1.id}")
        
        print("3. Testing Read Memos...")
        memos = Memo.query.filter_by(memo_date=today, created_by='test_verifier').all()
        assert len(memos) >= 1
        assert memos[0].content == "Test Memo 1"
        print("   Read success.")
        
        print("4. Testing Update Memo (Complete)...")
        memo1.is_completed = True
        db.session.commit()
        
        updated_memo = Memo.query.get(memo1.id)
        assert updated_memo.is_completed == True
        print("   Update success.")
        
        print("5. Testing Soft Delete...")
        memo1.active = False
        db.session.commit()
        
        deleted_memo = Memo.query.filter_by(id=memo1.id, active=True).first()
        assert deleted_memo is None
        print("   Soft delete success.")
        
        print("\nAll verification steps passed!")

if __name__ == "__main__":
    verify_memo_feature()
