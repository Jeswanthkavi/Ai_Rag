"""
Migration script to add the 'status' column to documents table
"""
from app.database import engine
from sqlalchemy import text

def add_status_column():
    """Add status column to documents table if it doesn't exist"""
    with engine.connect() as connection:
        try:
            # Check if column exists
            result = connection.execute(
                text("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'documents' AND COLUMN_NAME = 'status'
                """)
            )
            
            if result.fetchone():
                print("✓ 'status' column already exists in documents table")
                connection.commit()
                return True
            
            # Add the column if it doesn't exist
            print("Adding 'status' column to documents table...")
            connection.execute(
                text("""
                    ALTER TABLE documents 
                    ADD COLUMN status VARCHAR(30) 
                    DEFAULT 'uploaded' NOT NULL
                """)
            )
            connection.commit()
            print("✓ Successfully added 'status' column to documents table")
            return True
            
        except Exception as e:
            print(f"✗ Error during migration: {e}")
            connection.rollback()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION: Add status column")
    print("=" * 60)
    
    success = add_status_column()
    
    if success:
        print("=" * 60)
        print("✓ Migration completed successfully")
        print("=" * 60)
    else:
        print("=" * 60)
        print("✗ Migration failed")
        print("=" * 60)
        exit(1)
