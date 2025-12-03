# CloudTask - Cloud-Based Task Management System

A modern, full-featured cloud-based task management system built with Django 5.x and styled with Tailwind CSS. Designed for organizations, teams, and individuals to collaborate, organize tasks, and boost productivity.

## 🚀 Features

### User Management
- **Multi-role System**: Enterprise Admin, Manager, and Employee roles
- **Organization Structure**: Organizations with departments and staff IDs
- **User Profiles**: Extended profiles with role-based permissions

### Project Management
- **Project CRUD**: Create, edit, delete projects
- **Team Assignment**: Add/remove team members to projects
- **Project Comments**: Discussion threads on projects
- **Status Tracking**: Active, On Hold, Completed, Archived

### Task Management
- **Task CRUD**: Full task lifecycle management
- **Kanban Board**: Drag-and-drop visual task board
- **Task Dependencies**: Link related tasks with blocking dependencies
- **Priority Levels**: Low, Medium, High, Urgent
- **Status Workflow**: To Do → In Progress → In Review → Done
- **File Attachments**: Upload files to tasks (up to 10MB)
- **Task Templates**: Reusable task configurations
- **Time Tracking**: Start/stop timer and manual time entry

### Notifications & Activity
- **Real-time Notifications**: Alerts for task assignments, updates, comments
- **Activity Log**: Track all changes across projects and tasks
- **Notification Center**: View and manage all notifications

### Dashboard
- **Real-time Analytics**: Project counts, task statistics, team metrics
- **Task Status Overview**: Visual progress bars
- **Recent Activity Feed**: Latest actions across the organization
- **Role-based Views**: Different dashboards for Enterprise, Manager, Employee

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| **Backend** | Django 5.0.1 |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Frontend** | Tailwind CSS (CDN) |
| **Server** | Gunicorn |
| **Static Files** | Whitenoise |
| **Python** | 3.11+ |

## 📁 Project Structure

```
cloudtask/
├── cloudtask/          # Main project configuration
│   ├── settings.py     # Django settings
│   ├── urls.py         # URL routing
│   └── wsgi.py         # WSGI configuration
├── accounts/           # User authentication & profiles
│   ├── models.py       # UserProfile, Organization
│   ├── views.py        # Login, Register, Staff management
│   └── templates/      # Auth templates
├── projects/           # Project management
│   ├── models.py       # Project, ProjectMember, ProjectComment
│   ├── views.py        # Project CRUD, member management
│   └── templates/      # Project templates
├── tasks/              # Task management
│   ├── models.py       # Task, TaskComment, TaskAttachment, TimeEntry, TaskTemplate
│   ├── views.py        # Task CRUD, Kanban, Time tracking
│   └── templates/      # Task templates including Kanban board
├── notifications/      # Notifications & activity
│   ├── models.py       # Notification, ActivityLog
│   ├── views.py        # Notification list, mark read
│   ├── utils.py        # Helper functions for notifications
│   └── templates/      # Notification templates
├── dashboard/          # Dashboard views
│   ├── views.py        # Role-based dashboards
│   └── templates/      # Dashboard templates
├── landing/            # Landing pages
├── templates/          # Project-level templates
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── db.sqlite3          # SQLite database
```

## 🚦 Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/amol1027/cloudtask.git
   cd cloudtask
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

4. **Set up environment variables** (optional):
   ```bash
   copy dev.env.example .env
   ```

5. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Landing Page: http://127.0.0.1:8000/
   - Dashboard: http://127.0.0.1:8000/dashboard/
   - Admin Panel: http://127.0.0.1:8000/admin/

## 📱 Application URLs

| URL | Description |
|-----|-------------|
| `/` | Landing page |
| `/accounts/login/` | User login |
| `/accounts/register/` | User registration |
| `/dashboard/` | Main dashboard |
| `/projects/` | Project list |
| `/projects/create/` | Create new project |
| `/tasks/` | Task list |
| `/tasks/kanban/` | Kanban board |
| `/tasks/templates/` | Task templates |
| `/notifications/` | Notification center |
| `/notifications/activity/` | Activity log |

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Enterprise** | Full access: manage organization, projects, users |
| **Manager** | Manage assigned projects, create tasks, view team |
| **Employee** | View assigned tasks, update status, add comments |

## 🔧 Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

## 🚀 Production Deployment

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Auto-generated |
| `DEBUG` | Debug mode | `True` |
| `DATABASE_URL` | PostgreSQL connection string | SQLite |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |

### Running with Gunicorn
```bash
gunicorn cloudtask.wsgi:application --bind 0.0.0.0:8000
```

## 📊 Features by Phase

### ✅ Phase 1: Foundation
- Django project setup
- User authentication system
- Organization & UserProfile models
- Landing page

### ✅ Phase 2: Core Features
- Project CRUD operations
- Task CRUD operations
- Team member management
- Role-based dashboards

### ✅ Phase 3: Enhanced Features
- Notification system
- Activity logging
- File attachments
- Project comments
- Task dependencies

### ✅ Phase 4: Advanced Features
- Kanban board with drag-and-drop
- Time tracking
- Task templates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is for educational/portfolio purposes.

## 💬 Support

For questions or issues, please open a GitHub issue.
