from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://mongo:27017/'))
db = client['extracted_laptop_data']
collection = db['extracted_specs']

# Add template context processors
@app.context_processor
def utility_processor():
    return {
        'min': min,
        'max': max,
        'len': len
    }

@app.route('/')
def index():
    try:
        # Get page number from query parameters
        try:
            page = max(1, int(request.args.get('page', 1)))
        except (TypeError, ValueError):
            page = 1
        
        per_page = 20  # Number of laptops per page
        
        # Calculate skip value for pagination
        skip = (page - 1) * per_page
        
        # Get total count for pagination
        total_laptops = collection.count_documents({})
        total_pages = max(1, (total_laptops + per_page - 1) // per_page)
        
        # Ensure page is within valid range
        page = min(page, total_pages)
        
        # Get laptops for current page with sorting
        laptops = collection.find().sort([
            ('extracted_specs.brand', 1),
            ('extracted_specs.price', -1)
        ]).skip(skip).limit(per_page)
        
        return render_template(
            'index.html',
            laptops=laptops,
            page=page,
            total_pages=total_pages,
            total_laptops=total_laptops
        )
        
    except Exception as e:
        app.logger.error(f"Error in index route: {str(e)}")
        flash(f"An error occurred while loading the data: {str(e)}", "danger")
        return render_template(
            'index.html',
            laptops=[],
            page=1,
            total_pages=1,
            total_laptops=0
        )

@app.route('/laptop/<string:id>')
def view_laptop(id):
    try:
        laptop = collection.find_one({'_id': ObjectId(id)})
        if laptop:
            return render_template('view_laptop.html', laptop=laptop)
        flash('Laptop not found', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/laptop/<string:id>/edit', methods=['GET', 'POST'])
def edit_laptop(id):
    try:
        if request.method == 'POST':
            # Extract form data with safe type conversion
            specs = {
                'title': request.form.get('title', ''),
                'url': request.form.get('url', ''),
                'brand': request.form.get('brand', ''),
                'price': float(request.form.get('price', 0) or 0),
                'processor_brand': request.form.get('processor_brand', ''),
                'processor_gen': request.form.get('processor_gen', ''),
                'processor_model': request.form.get('processor_model', ''),
                'graphics_brand': request.form.get('graphics_brand', ''),
                'graphics_cardname': request.form.get('graphics_cardname', ''),
                'display_size': float(request.form.get('display_size', 0) or 0),
                'display_resolution': request.form.get('display_resolution', ''),
                'display_refresh_rate': int(request.form.get('display_refresh_rate', 0) or 0),
                'ram_size': int(request.form.get('ram_size', 0) or 0),
                'ram_speed': request.form.get('ram_speed', ''),
                'storage': request.form.get('storage', ''),
                'ports': {
                    'usb': int(request.form.get('ports_usb', 0) or 0),
                    'hdmi': int(request.form.get('ports_hdmi', 0) or 0),
                    'thunderbolt': int(request.form.get('ports_thunderbolt', 0) or 0),
                    'ethernet': int(request.form.get('ports_ethernet', 0) or 0)
                }
            }
            
            # Update database
            result = collection.update_one(
                {'_id': ObjectId(id)},
                {
                    '$set': {
                        'extracted_specs': specs,
                        'last_modified': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                flash('Laptop information updated successfully', 'success')
            else:
                flash('No changes were made', 'info')
                
            return redirect(url_for('view_laptop', id=id))
        
        laptop = collection.find_one({'_id': ObjectId(id)})
        if laptop:
            return render_template('edit_laptop.html', laptop=laptop)
        
        flash('Laptop not found', 'danger')
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))
    
    # Search in multiple fields
    search_filter = {
        '$or': [
            {'extracted_specs.title': {'$regex': query, '$options': 'i'}},
            {'extracted_specs.brand': {'$regex': query, '$options': 'i'}},
            {'extracted_specs.processor_brand': {'$regex': query, '$options': 'i'}},
            {'extracted_specs.graphics_brand': {'$regex': query, '$options': 'i'}},
            {'extracted_specs.graphics_cardname': {'$regex': query, '$options': 'i'}}
        ]
    }
    
    laptops = collection.find(search_filter)
    return render_template('search_results.html', laptops=laptops, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)