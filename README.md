# CloudTask - Cloud-Based Task Management System

A modern, cloud-based task management system built with Django 5.x and styled with Tailwind CSS. Designed for teams and individuals to collaborate, organize, and boost productivity.

## Tech Stack

- **Backend**: Django 5.0.1
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Tailwind CSS (via CDN)
- **Server**: Gunicorn
- **Static Files**: Whitenoise
- **Python**: 3.11+

## Project Structure

```
cloudtask/
├── cloudtask/          # Main project configuration
│   ├── settings.py     # Django settings
│   ├── urls.py         # URL routing
│   ├── wsgi.py         # WSGI configuration
│   └── asgi.py         # ASGI configuration
├── accounts/           # User authentication & profiles
├── tasks/              # Task management
├── landing/            # Landing pages
├── templates/          # Project-level templates
├── static/             # Project-level static files
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── .gitignore          # Git ignore rules
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository** (or create a new one):
   ```bash
   git checkout -b chore/project-setup
   ```

2. **Create a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   
   Copy the example environment file and configure:
   ```bash
   # Windows
   copy dev.env.example .env

   # macOS/Linux
   cp dev.env.example .env
   ```

   Edit `.env` and set your values:
   - `SECRET_KEY`: Generate a new Django secret key
   - `DEBUG`: Set to `True` for development, `False` for production
   - `DATABASE_URL`: PostgreSQL connection string (optional for production)

5. **Run database migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Landing Page: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Environment Variables

Create a `.env` file in the project root with the following variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key (keep this secret!) | Auto-generated placeholder |
| `DEBUG` | Debug mode (True/False) | `True` |
| `DATABASE_URL` | PostgreSQL connection string | SQLite (dev) |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` |

## Development

### Running Tests

```bash
python manage.py test
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Production Deployment

### PostgreSQL Configuration

Uncomment the PostgreSQL section in `settings.py` and set the `DATABASE_URL` environment variable:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/cloudtask
```

### Running with Gunicorn

```bash
gunicorn cloudtask.wsgi:application --bind 0.0.0.0:8000
```

### Static Files

Static files are served using Whitenoise. Run `collectstatic` before deployment:

```bash
python manage.py collectstatic --noinput
```

## Apps Overview

### 1. Landing (`landing/`)
- Marketing and informational pages
- Homepage with Tailwind CSS styling
- Features showcase

### 2. Accounts (`accounts/`)
- User authentication (login, register, logout)
- User profiles
- Password reset
- **Note**: Phase 2 will implement CustomUser model

### 3. Tasks (`tasks/`)
- Task CRUD operations
- Task assignment and collaboration
- Status tracking and priorities
- **Note**: Phase 2 will implement full task models

## Initial Git Commit

This project is set up on branch `chore/project-setup`. Use the following commit message:

```
chore: initial project scaffold with landing, accounts, tasks apps

- Created Django 5.x project with cloudtask configuration
- Added three apps: accounts, tasks, landing
- Configured Tailwind CSS via CDN
- Set up Whitenoise for static files
- Added PostgreSQL support with SQLite default
- Created landing page templates
- Configured timezone to Asia/Kolkata
- Added requirements.txt with pinned dependencies
- Created comprehensive .gitignore
```

## Next Steps (Phase 2)

- [ ] Implement CustomUser model in accounts app
- [ ] Create Task and Tag models in tasks app
- [ ] Build authentication views (login, register, logout)
- [ ] Develop task CRUD views and templates
- [ ] Add user dashboard
- [ ] Implement task filtering and search
- [ ] Add real-time notifications
- [ ] Create REST API endpoints

## Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## License

This project is for educational/portfolio purposes.

## Support

For questions or issues, please open a GitHub issue.
