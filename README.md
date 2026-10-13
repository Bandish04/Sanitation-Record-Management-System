# 🧼 Sanitation Record Management System

<p align="center">
  <strong>A Django-Based Web Application for Digital Sanitation Record Management</strong>
</p>

<p align="center">
  Manage sanitation activities, chemical titrations, inspections, ATP reports, and daily records through one centralized platform.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Django-6.x-092E20?logo=django" alt="Django">
  <img src="https://img.shields.io/badge/Django%20REST%20Framework-API-red" alt="Django REST Framework">
  <img src="https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-blue" alt="Database">
  <img src="https://img.shields.io/badge/Frontend-HTML%20%7C%20CSS%20%7C%20JavaScript-orange" alt="Frontend">
</p>

---

## 📌 Table of Contents

- [📖 About the Project](#-about-the-project)
- [✨ Features](#-features)
- [👥 User Roles and Permissions](#-user-roles-and-permissions)
- [🧪 Sanitation Calculations](#-sanitation-calculations)
- [🛠️ Technology Stack](#️-technology-stack)
- [🏗️ Project Structure](#️-project-structure)
- [🔌 API Integration](#-api-integration)
- [🖼️ Screenshots](#️-screenshots)
- [⚙️ Installation and Setup](#️-installation-and-setup)
- [🔐 Demo Login Accounts](#-demo-login-accounts)
- [🧪 Running Tests](#-running-tests)
- [🚀 Deployment Notes](#-deployment-notes)
- [🔒 Security Notes](#-security-notes)
- [🐛 Troubleshooting](#-troubleshooting)
- [🔮 Future Improvements](#-future-improvements)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👨‍💻 Author](#-author)

---

## 📖 About the Project

The **Sanitation Record Management System** is designed to digitize and simplify the management of sanitation-related operations.

Instead of relying entirely on manual paperwork and spreadsheets, users can manage sanitation information through a centralized web application.

The application supports plant management, sanitizer and Chloragel titrations, daily sanitation inspections, ATP report uploads, record searching, PDF report generation, corrective actions, user management, and audit logging.

It also uses **Django REST Framework APIs** to handle communication between the frontend and backend, making the system easier to organize and extend.

### 🎯 Project Objectives

- Digitize sanitation recordkeeping.
- Reduce manual data entry and improve consistency.
- Calculate chemical titration results automatically.
- Organize inspection and ATP report information.
- Provide searchable daily records and downloadable reports.
- Control access based on user roles.
- Maintain accountability through audit logging.
- Provide API endpoints for application data and operations.

---

## ✨ Features

### 🏭 Plant Management
- Manage plant information.
- View plant details and status.
- Support administrative plant management operations.
- Restrict management actions according to user permissions.

### 🧴 Sanitizer Titrations
- Record sanitizer titration measurements.
- Calculate PPM and percentage values automatically.
- Save records as drafts and submit completed records.
- Display calculation results and applicable statuses.
- Track record creation and submission information.

### 🧪 Chloragel Titrations
- Record Chloragel titration measurements.
- Calculate the result percentage automatically.
- Save and submit titration records.
- Display the applicable result status.
- Maintain records for future reference and reporting.

### 📋 Daily Sanitation Inspections
- Record daily sanitation inspection information.
- Associate inspection records with plants.
- Capture responses to inspection questions.
- Track inspection details and completion status.

### 🧫 ATP Reports
- Upload ATP-related reports and supporting files.
- Associate reports with plants and inspections when applicable.
- Store notes and upload information.
- Support common file formats such as PDF, JPG, JPEG, PNG, and WebP, subject to application validation.

### 📚 Daily Combined Records
- View sanitation records organized by plant and date.
- Bring together relevant titration, inspection, and ATP report information.
- Search and review existing records.
- Generate PDF reports for supported record selections.

### 🔎 Search Records
- Search records using available filters.
- Filter by plant, date range, record type, and status where supported.
- Review record details through the interface.

### 👤 User Management
- Support user accounts and role-based permissions.
- Organize users into Inspector, Team Lead, and Admin roles.
- Restrict administrative actions according to permissions.

### 🛠️ Corrective Actions
- Support corrective action records for sanitation-related issues.
- Track relevant action information and statuses.

### 📝 Audit Logs
- Maintain audit-related information for supported application activities.
- Help administrators review recorded actions and changes.

### 📄 PDF Reporting
- Generate PDF reports for supported sanitation records.
- Provide a convenient format for reviewing, sharing, and archiving information.

### 🔌 REST API Integration
- Use Django REST Framework to expose backend functionality.
- Support structured data exchange between the frontend and backend.
- Organize application operations through API endpoints.
- Support authentication and permission checks for protected endpoints.

---

## 👥 User Roles and Permissions

The application uses three primary roles.

| Role | Responsibilities |
|---|---|
| 👑 **Admin** | Administrative access, user management, plant management, and access to supported application modules. |
| 🧑‍🔬 **Inspector** | Performs assigned sanitation activities, including supported titration and inspection operations. |
| 🧑‍💼 **Team Lead** | Performs permitted operational activities and reviews or manages records according to configured permissions. |

**Note:** Actual permissions depend on the application's backend permission classes, group assignments, and endpoint configuration. The table describes the intended roles and does not override the permissions implemented in the code.

---

## 🧪 Sanitation Calculations

The application calculates titration results using the following formulas.

### 🧴 Sanitizer / Maxquat

| Parameter | Value |
|---|---|
| Sample volume | 5 mL |
| Supported drop-count range | 1–32 drops |
| PPM calculation | Drops × 12.5 |
| Percentage calculation | Drops × 0.0125 |

**Example:** If the titration uses 4 drops:

- PPM = 4 × 12.5 = **50 ppm**
- Percentage = 4 × 0.0125 = **0.05%**

### 🧪 Chloragel

| Parameter | Value |
|---|---|
| Sample volume | 15 mL |
| Supported drop-count range | 1–50 drops |
| Result percentage calculation | Drops × 0.198 |

**Example:** If the titration uses 10 drops:

- Result percentage = 10 × 0.198 = **1.98%**

Result statuses and pass/fail thresholds depend on the application's configured rules. If the required configuration is unavailable, the application may return a review-required status.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| 🐍 Python | Core programming language |
| 🌿 Django | Web framework and application backend |
| 🔌 Django REST Framework | REST API development |
| 🔐 JWT Authentication | Token-based authentication where configured |
| 🌐 HTML5 | Page structure |
| 🎨 CSS3 | Styling and layout |
| ⚡ JavaScript | Frontend interactions and API requests |
| 🅱️ Bootstrap | Responsive UI components |
| 🗄️ SQLite | Local development database |
| 🐘 PostgreSQL | Production database support |
| 📄 PDF generation libraries | Generating downloadable reports |
| 🧪 Django Test Framework | Application testing |
| 🌍 Git and GitHub | Version control and source code hosting |

The exact dependencies and versions used by the project are listed in `requirements.txt`.

---

## 🏗️ Project Structure

The repository is organized around Django applications and shared templates.

```text
Sanitation-Record-Management-System/
│
├── accounts/                 # User accounts, authentication, permissions
├── plants/                   # Plant management
├── titrations/               # Sanitizer and Chloragel titrations
├── inspections/              # Daily inspections and ATP reports
├── records/                  # Daily records, search, and PDF reports
├── corrective_actions/       # Corrective action management
├── audit/                    # Audit logging
├── config/                   # Django project settings and URLs
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── admin/
│   ├── audit/
│   ├── corrective_actions/
│   ├── inspections/
│   ├── plants/
│   ├── records/
│   ├── registration/
│   └── titrations/
│
├── static/
│   └── css/
│       └── tailadmin.css
│
├── media/                    # Uploaded files during local development
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

The structure above illustrates the main project components. Individual files, additional applications, and directories may differ as the project evolves.

---

## 🔌 API Integration

**This project uses Django REST Framework APIs** to connect frontend operations with backend functionality.

The API layer handles requests, data validation, authentication, permissions, and responses for supported application operations.

### 🔄 How API Communication Works

1. A user interacts with a page in the frontend.
2. JavaScript sends an HTTP request to the relevant API endpoint.
3. Django REST Framework processes the request.
4. Authentication and permission checks are applied where configured.
5. The backend validates and processes the data.
6. The API returns a response that the frontend uses to update the interface.

### 📡 API Endpoint Examples

The following endpoints are representative examples based on the application's API structure. Confirm the current URL configuration in the repository before relying on them.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/auth/login/` | Authenticate a user, if configured at this path |
| `GET` | `/api/auth/users/` | Retrieve user information, subject to permissions |
| `GET` | `/api/records/daily/` | Retrieve daily sanitation records |
| `GET` | `/api/records/daily/pdf/` | Generate or retrieve a PDF report for supported filters |

Other API routes may support plants, titrations, inspections, ATP reports, corrective actions, and audit information.

### 🧰 Testing APIs

You can use tools such as:

- **Postman** — to send requests and inspect API responses.
- **Browser Developer Tools** — to inspect frontend requests and errors.
- **Django runserver output** — to diagnose backend errors during local development.

Example request for daily records:

```http
GET /api/records/daily/?plant=1&date=2026-10-12
```

Example request for a PDF report:

```http
GET /api/records/daily/pdf/?plant=1&date=2026-10-12
```

These examples assume the corresponding routes are enabled in the current version of the project. Replace the plant ID and date with valid values from your database.

---

## 🖼️ Screenshots

Screenshots help demonstrate the application's interface and functionality.

### 📸 Application Preview

Here are some screenshots of the Sanitation Record Management System.

| Screenshot 1 | Screenshot 2 |
|---|---|
| ![Screenshot 1](ScreenShots/1.png) | ![Screenshot 2](ScreenShots/2.png) |

| Screenshot 3 | Screenshot 4 |
|---|---|
| ![Screenshot 3](ScreenShots/3.png) | ![Screenshot 4](ScreenShots/4.png) |

| Screenshot 5 | Screenshot 6 |
|---|---|
| ![Screenshot 5](ScreenShots/5.png) | ![Screenshot 6](ScreenShots/6.png) |

| Screenshot 7 | Screenshot 8 |
|---|---|
| ![Screenshot 7](ScreenShots/7.png) | ![Screenshot 8](ScreenShots/8.png) |

| Screenshot 9 | Screenshot 10 |
|---|---|
| ![Screenshot 9](ScreenShots/9.png) | ![Screenshot 10](ScreenShots/10.png) |

| Screenshot 11 | Screenshot 12 |
|---|---|
| ![Screenshot 11](ScreenShots/11.png) | ![Screenshot 12](ScreenShots/12.png) |

| Screenshot 13 | Screenshot 14 |
|---|---|
| ![Screenshot 13](ScreenShots/13.png) | ![Screenshot 14](ScreenShots/14.png) |

| Screenshot 15 | Screenshot 16 |
|---|---|
| ![Screenshot 15](ScreenShots/15.png) | ![Screenshot 16](ScreenShots/16.png) |

### 🖥️ Additional Screenshot

![Screenshot 17](ScreenShots/17.png)



> **📌 Note:** Add the image files with the exact filenames shown above. Until those files exist in the repository, the screenshot previews will not display.

---

## ⚙️ Installation and Setup

Follow these steps to clone the repository and run the application locally.

### ✅ Prerequisites

Install the following before getting started:

- Python compatible with the project's dependencies.
- Git.
- A terminal such as PowerShell, Command Prompt, or Bash.
- A code editor such as Visual Studio Code.

The project was developed using Python 3.14.7 and Django 6.1.1. Use the project's actual dependency requirements if your environment differs.

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Bandish04/Sanitation-Record-Management-System.git
```

Move into the project directory:

```bash
cd Sanitation-Record-Management-System
```

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment.

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the project's dependencies:

```bash
python -m pip install -r requirements.txt
```

If a package installation fails, verify your Python version and the dependency versions listed in `requirements.txt`.

### 4️⃣ Configure Environment Variables

Create a local `.env` file if the project is configured to load environment variables from one.

Typical configuration values may include:

```env
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=replace-with-a-local-development-secret
DATABASE_URL=
```

Use the variable names expected by `config/settings.py`. The example above is illustrative; it does not guarantee that every variable is required or that the project automatically loads `.env` files.

For local SQLite development, leave `DATABASE_URL` unset or empty if the settings support that behavior. For PostgreSQL, provide a valid database URL in the format expected by the application.

**Never commit real passwords, production database URLs, API secrets, or other credentials to GitHub.**

### 5️⃣ Apply Database Migrations

```bash
python manage.py migrate
```

This creates the database tables required by the application.

### 6️⃣ Create User Roles

If the repository includes the `create_roles` management command, run:

```bash
python manage.py create_roles
```

This command is intended to create the application's configured user groups. If Django reports that the command does not exist, inspect the management commands in the repository and follow the setup instructions implemented by the current version.

### 7️⃣ Create an Administrator Account

For a new local installation, the standard Django command is:

```bash
python manage.py createsuperuser
```

Follow the prompts to create an administrator account.

If the project includes a custom `setup_deployment_admin` management command, it may also support creating or promoting a deployment administrator using the environment variables required by that command. Check its implementation before running it.

### 8️⃣ Start the Development Server

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

The dashboard or login page should be available at the appropriate route configured in the project.

### 🎉 Setup Complete!

You can now log in with the local account you created and explore the application.

---

## 🔐 Demo Login Accounts

The following usernames identify the example accounts used during project development.

| Username | Role |
|---|---|
| `Admin` | 👑 Admin |
| `Ajay` | 🧑‍🔬 Inspector |
| `Deep` | 🧑‍💼 Team Lead |

### 🔑 How to Log In After Cloning

**Important:** Cloning the GitHub repository does not automatically copy the original development database or its users. You must create the accounts in your own local database.

To set up your own accounts:

1. Complete the installation and run database migrations.
2. Create the users through Django's user management functionality or the project's registration interface.
3. Assign each user to the correct Django group: `Admin`, `Inspector`, or `Team Lead`, according to the groups configured in the application.
4. Set a password for each account locally.
5. Log in using the username and password you configured.

If the project provides a supported management command or fixture for initializing roles and demo accounts, you can use it after reviewing its implementation.

> 🔒 **Security note:** Demo passwords should not be published in this public repository. Use locally configured passwords, and never reuse development credentials in a production environment.

---

## 🧪 Running Tests

Django provides a built-in testing framework.

Run the complete test suite:

```bash
python manage.py test
```

To check for common configuration issues:

```bash
python manage.py check
```

If the project contains separate test modules for individual applications, you can run tests for a specific application. For example:

```bash
python manage.py test accounts
```

Replace `accounts` with the relevant application name as needed.

---

## 🚀 Deployment Notes

The project can be configured for deployment using a production WSGI server and PostgreSQL.

Potential deployment components include:

- **Web hosting:** a platform such as Render.
- **Database:** PostgreSQL.
- **Application server:** Gunicorn.
- **Static files:** Django static-file configuration and a suitable static-file serving solution.
- **Environment variables:** production settings and secrets.

### Production Checklist

Before deploying:

- [ ] Set `DEBUG=False`.
- [ ] Configure a strong, unique `DJANGO_SECRET_KEY`.
- [ ] Configure the production `DATABASE_URL`.
- [ ] Set the correct allowed hosts.
- [ ] Configure HTTPS and secure cookies as appropriate.
- [ ] Configure static-file handling.
- [ ] Configure media-file storage for uploaded ATP reports.
- [ ] Run database migrations.
- [ ] Create or configure the administrator account securely.
- [ ] Verify API authentication and role permissions.
- [ ] Run tests and Django's deployment checks.

For production checks, use:

```bash
python manage.py check --deploy
```

Review any warnings before exposing the application publicly.

---

## 🔒 Security Notes

Security is important because the application handles user accounts and sanitation records.

- Keep secrets and passwords out of source control.
- Use environment variables for production configuration.
- Do not publish real demo passwords in a public repository.
- Assign only the permissions required for each user role.
- Validate uploaded files and enforce file-size limits.
- Configure authentication and permissions for protected API endpoints.
- Use HTTPS in production.
- Review audit logging and error handling before deployment.
- Change any credentials that have been exposed or shared publicly.

The repository should not contain a production database, private keys, or a `.env` file with real secrets.

---

## 🐛 Troubleshooting

### ❌ `ModuleNotFoundError`

Install dependencies and confirm that the virtual environment is active:

```bash
python -m pip install -r requirements.txt
```

### ❌ Database or Migration Errors

Run:

```bash
python manage.py migrate
```

If errors persist, verify your database configuration and confirm that the database is accessible.

### ❌ Login Fails After Cloning

The original development database is not automatically included when you clone the repository.

Create a local user, set a password, and assign the appropriate role group.

### ❌ Permission Errors

Verify that the user belongs to the correct Django group and that the corresponding API permission classes allow the requested operation.

### ❌ Static Files Are Missing

Confirm the static-file configuration and file paths. For a production environment, review the `STATIC_URL`, `STATIC_ROOT`, and static-file serving setup.

### ❌ PDF or File Upload Errors

Check the installed PDF dependencies, media configuration, upload validation, and file permissions. Uploaded media files may require separate storage in production.

### ❌ A Management Command Is Not Recognized

Confirm that the command exists in the repository under the appropriate application's `management/commands/` directory before running it.

---

## 🔮 Future Improvements

Possible enhancements for future versions include:

- 📊 Advanced analytics and sanitation dashboards.
- 📈 Trend charts for titration and inspection results.
- 📧 Email notifications and reminders.
- 📱 Improved mobile responsiveness.
- 🧾 More customizable PDF reports.
- 🔍 Enhanced filtering and reporting.
- 🧪 Expanded automated test coverage.
- ☁️ Improved production media storage.
- 🔐 More comprehensive security and permission testing.
- 📷 Automated data extraction from supported report images and documents.

These are potential improvements, not claims that the features are already implemented.

---

## 🤝 Contributing

Contributions and suggestions are welcome.

To contribute:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes and test them locally.
4. Commit your changes with a descriptive message.
5. Push your branch to your fork.
6. Open a pull request describing your improvements.

Please avoid committing secrets, private user data, database files, or unnecessary generated files.

---

## 📄 License

No license has been specified in this README.

Before reusing, modifying, or distributing the project, check the repository for a `LICENSE` file. If you want others to use and contribute to the project under defined terms, consider adding an appropriate open-source license.

---

## 👨‍💻 Author

**Bandish Vaidya**

Software Engineer | Django Developer

- **GitHub:** [@Bandish04](https://github.com/Bandish04)
- **Project Repository:** [Sanitation Record Management System](https://github.com/Bandish04/Sanitation-Record-Management-System)

---

<p align="center">
  🧼 <strong>Sanitation Record Management System</strong>
  <br>
  <em>Digitizing sanitation records, one record at a time.</em>
</p>
