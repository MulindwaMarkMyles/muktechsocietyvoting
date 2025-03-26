# MTS Voting System

A Django-based voting system designed for managing student elections with secure user authentication and role-based access control.

## Features

- User Authentication System
- Role-based Access (Admin/Voter)
- Student Number Verification
- Custom Admin User Creation
- Profile Management
- Voting Control System (Enable/Disable voting)

## Requirements

- Python 3.8+
- Django 4.0+
- Other dependencies in requirements.txt

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd mts_voting
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply migrations:

```bash
python manage.py migrate
```

## Creating Admin Users

Use the custom management command to create an admin user:

```bash
python manage.py createadminuser
```

You will be prompted for:

- Username
- First Name
- Last Name
- Student Number
- Password (with confirmation)

Or use non-interactive mode:

```bash
python manage.py createadminuser --username=admin --email=admin@example.com --stud-no=12345 --first-name=John --last-name=Doe
```

## User Types

1. Admin (user_type='1')

   - Full system access
   - Can approve voters
   - Manage elections

2. Voter (user_type='2')
   - Limited access
   - Can participate in voting
   - Requires approval

## Voting Control

Administrators can enable or disable voting system-wide:

1. Navigate to the admin panel
2. Go to "Voting Controls"
3. Click the "Enable Voting" or "Disable Voting" button to toggle voting status

When voting is disabled, users won't be able to access the voting interface.

## Development

To run the development server:

```bash
python manage.py runserver
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License
