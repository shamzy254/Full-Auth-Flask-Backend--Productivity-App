"""
Database seeding script with Faker-generated test data.
"""
from faker import Faker
from app import create_app
from models import db, User, Note

fake = Faker()

def seed_database():
    """Seed the database with test data."""
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        Note.query.delete()
        User.query.delete()
        
        # Create test users
        print("Creating test users...")
        users = []
        for i in range(5):
            user = User(
                username=f'user{i+1}',
                email=f'user{i+1}@example.com'
            )
            user.set_password('password123')
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(users)} users")
        
        # Create test notes for each user
        print("Creating test notes...")
        note_count = 0
        for user in users:
            # Create 5-15 notes per user
            num_notes = fake.random_int(min=5, max=15)
            for _ in range(num_notes):
                note = Note(
                    title=fake.sentence(nb_words=5),
                    content=fake.paragraph(nb_sentences=fake.random_int(min=3, max=8)),
                    user_id=user.id
                )
                db.session.add(note)
                note_count += 1
        
        db.session.commit()
        print(f"Created {note_count} notes")
        
        print("\nDatabase seeding complete!")
        print("\nTest users created:")
        for user in users:
            print(f"  - {user.username} ({user.email})")
        print("\nPassword for all users: password123")

if __name__ == '__main__':
    seed_database()
