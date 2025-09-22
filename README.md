# Aethermere City Map

An interactive web application for managing and visualizing the districts of Aethermere, a fantasy city for tabletop RPG campaigns. Built with Flask and featuring a dynamic SVG map with real-time editing capabilities.

## Features

- 🗺️ **Interactive SVG Map** - Click districts to view/edit information
- 🎨 **Visual District Types** - Color-coded districts (Commercial, Residential, Sealed, etc.)
- ✏️ **Live Editing** - Update district names, descriptions, status, and colors
- 💾 **Database Persistence** - All changes saved to SQLite database
- 🎯 **Smart UI** - Auto-edit for undefined districts, info panel for defined ones
- 🌈 **Dynamic Styling** - Info panel border matches selected district color

## World Background

Twenty years after The Weeping, Aethermere stands as the largest surviving city with ~150,000 inhabitants. Once the magnificent city of Aetherspire built around a great crystal spire, it now arranges twelve districts like the hours of a clock around the dark pool where the spire fell.

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AethermereMap
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Seed the database**
   ```bash
   python seed_data.py
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Visit** `http://localhost:5001` in your browser

## Usage

### Viewing Districts
- Click any district on the map to view its information
- Defined districts show an info panel with description and status
- Undefined districts automatically open the edit form

### Editing Districts
- **Undefined districts**: Click to auto-open edit form
- **Defined districts**: Click to view info, then click "Edit" button
- **Any district**: Ctrl+Click or right-click to force edit mode

### District Types
- **Gray**: To Be Determined
- **Gold**: Commercial/Active
- **Blue**: Working Class/Industrial  
- **Green**: Residential/Productive
- **Purple**: Religious/Administrative
- **Red**: Dangerous/Polluted
- **Dark Purple**: Wealthy/Elite
- **Red Pattern**: Sealed District

## Project Structure

```
AethermereMap/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # Database models
│   │   ├── district.py      # District model
│   │   └── user.py          # User model
│   ├── routes/              # Route blueprints
│   │   ├── main.py          # Main routes
│   │   └── api.py           # API endpoints
│   ├── templates/           # Jinja2 templates
│   │   └── index.html       # Main map template
│   └── static/              # Static files
│       ├── css/style.css    # Styles
│       └── js/map.js        # Map interactions
├── config/
│   └── config.py            # Configuration
├── instance/                # Instance-specific files
│   └── aethermere.db        # SQLite database
├── run.py                   # Application entry point
├── seed_data.py             # Database seeding script
└── requirements.txt         # Dependencies
```

## API Endpoints

- `GET /api/districts` - List all districts
- `GET /api/districts/<id>` - Get single district
- `PUT /api/districts/<id>` - Update district
- `DELETE /api/districts/<id>` - Delete district

## Configuration

Environment variables can be set in `.env`:
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///path/to/database.db
FLASK_ENV=development
```

## Database Schema

### District Model
- `id` - Primary key
- `name` - District name
- `info` - Description (nullable)
- `status` - Current status (nullable)
- `color` - Display color
- `district_number` - Position (1-12)
- `svg_path` - SVG path data for rendering
- `label_x`, `label_y` - Label coordinates
- `created_at`, `updated_at` - Timestamps

## Development

### Running Tests
```bash
# TODO: Add test commands when implemented
```

### Adding New Districts
Districts are seeded from `seed_data.py`. Modify the `districts_data` array to add or update districts.

### Customizing Appearance
- Update `app/static/css/style.css` for styling
- Modify `app/templates/index.html` for layout changes
- Edit `app/static/js/map.js` for interaction behavior

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Your chosen license]

## Campaign Notes

This application is designed for tabletop RPG campaigns. The districts can be customized for any fantasy city setting. The twelve-district clock layout provides an intuitive way to organize urban areas for campaign management.