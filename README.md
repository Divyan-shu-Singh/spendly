# Spendly ◈

**Track every rupee. Own your finances.**

Spendly is a clean, modern personal finance tracker designed to help users log expenses, understand their spending patterns, and take control of their financial life without the headache of complex spreadsheets.

## 🚀 Features

- **Instant Expense Logging**: Quickly add transactions with categories, amounts, dates, and descriptions.
- **Spending Insights**: Visualize where your money goes with category breakdowns and monthly summaries.
- **Flexible Filtering**: View spending across various time periods—last week, last month, or custom ranges.
- **User Authentication**: Secure registration and login system to keep your financial data private.
- **Professional Landing Page**: A high-conversion landing page featuring a modern design, a "How it works" video modal, and legal pages (Terms & Privacy).

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Templating**: Jinja2
- **Typography**: DM Serif Display, DM Sans (Google Fonts)

## 📦 Installation & Setup

### Prerequisites
- Python 3.x installed on your machine

### Setup
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd expense-tracker
   ```

2. **Install dependencies**:
   ```bash
   pip install flask
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the app**:
   Open your browser and navigate to `http://127.0.0.1:5001`

## 📁 Project Structure

```text
expense-tracker/
├── app.py              # Main Flask application & routing
├── static/             # Static assets
│   ├── css/            # Stylesheets (style.css, landing.css)
│   └── js/             # Client-side JavaScript
└── templates/          # Jinja2 HTML templates
    ├── base.html       # Global layout wrapper
    ├── landing.html    # Landing page
    ├── login.html      # User login
    ├── register.html   # User registration
    ├── terms.html      # Terms and Conditions
    └── privacy.html    # Privacy Policy
```

## 🗺️ Roadmap

The following features are currently in development:
- [ ] User Profile management
- [ ] Logout functionality
- [ ] Full Expense CRUD (Add, Edit, Delete)
- [ ] Database integration for persistent storage
- [ ] Advanced spending analytics and charts

## 📄 License

This project is for educational purposes.
