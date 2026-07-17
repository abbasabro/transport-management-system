# BBSUTSD Transport Logs Management System

A professional desktop application for managing vehicles, drivers, daily logs, repairs, and reports at **Benazir Bhutto Shaheed University of Technology & Skills Development (BBSUTSD)**. Built with PySide6, SQLite, and ReportLab, and designed for offline‑first usage with future centralised synchronisation via FastAPI and PostgreSQL.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## 📋 Features

- **Role‑Based Access Control** – Transport Head (full access) and Transport Clerk (restricted).
- **Vehicle Management** – Add, update, soft‑delete, and track active/inactive status.
- **Driver Management** – Assign drivers to vehicles, spare driver support, lifecycle management.
- **Daily Logs** – Log trips with automatic mileage calculation and driver auto‑fill.
- **All Logs** – Paginated, date‑filterable view of all vehicle logs.
- **Repair Management** – Track repairs with cost summaries and search.
- **Report Generation** – Professional PDF reports (Vehicle Log, Driver List, Vehicle List, Repair Report) with university branding.
- **User Management** – Add/edit users, change passwords, deactivate accounts.
- **Offline First** – Local SQLite database ensures uninterrupted work.
- **Centralised Error Handling** – User‑friendly dialogs and automatic logging.
- **PyInstaller + Inno Setup** – Single installer for easy deployment on Windows.

---

## 🛠 Technology Stack

| Component         | Technology                          |
|-------------------|-------------------------------------|
| Desktop Framework | PySide6                             |
| Local Database    | SQLite3                             |
| PDF Reports       | ReportLab                           |
| Authentication    | bcrypt                              |
| Packaging         | PyInstaller                         |
| Installer         | Inno Setup                          |
| Sync API (future) | FastAPI, PostgreSQL                 |

---

## 📸 Screenshots

> *(Add screenshots of the login screen, dashboard, vehicle list, and a sample report here)*

![Dashboard](screenshots/dashboard.png)  
*Dashboard with role‑based action cards*

![Vehicle List](screenshots/vehicles.png)  
*Vehicle list showing active/inactive status*

![Report](screenshots/report.png)  
*Professional PDF report with university branding*

---

## 🚀 Installation

### For End Users (Windows)

1. Download the latest installer (`BBSTUD‑TMS_Setup_1.0.exe`) from the [Releases](https://github.com/abbasabro/bbsutsd-transport-logs-management-system/releases) page.
2. Run the installer as Administrator.
3. Follow the wizard. A desktop shortcut and Start Menu entry are created.
4. Launch the application and log in with the default credentials:
   - **Transport Head:** `admin` / `admin123`
   - **Transport Clerk:** `clerk` / `clerk123`
5. Change the default passwords immediately.

The application stores all data in `%APPDATA%\BBSUTSD‑TMS\transport_db.db`.  
⚠️ **Back up this file regularly.**

### For Developers

```bash
# Clone the repository
git clone https://github.com/abbasabro/bbsutsd-transport-logs-management-system.git
cd bbsutsd-transport-management-system

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py