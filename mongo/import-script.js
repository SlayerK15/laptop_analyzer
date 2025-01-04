// import-script.js
const fs = require('fs');
const { parse } = require('csv-parse/sync');

// Read and parse the CSV file
const fileContent = fs.readFileSync('./data.csv', 'utf-8');
const records = parse(fileContent, {
    columns: true,
    skip_empty_lines: true,
    trim: true
});

// Connect to MongoDB
const db = db.getSiblingDB('laptop_specs');

// Create collection
db.createCollection('laptops');

// Process and insert records
const processedRecords = records.map(record => {
    // Convert string numbers to actual numbers
    const numericFields = [
        'extracted_specs.price',
        'extracted_specs.display_size',
        'extracted_specs.display_refresh_rate',
        'extracted_specs.ram_size',
        'extracted_specs.ports',
        'extracted_specs.ports.ethernet',
        'extracted_specs.ports.usb',
        'extracted_specs.ports.hdmi',
        'extracted_specs.ports.thunderbolt'
    ];

    numericFields.forEach(field => {
        if (record[field] && record[field].trim() !== '') {
            record[field] = parseFloat(record[field]);
        }
    });

    return record;
});

// Insert the processed records in batches
const batchSize = 100;
for (let i = 0; i < processedRecords.length; i += batchSize) {
    const batch = processedRecords.slice(i, i + batchSize);
    db.laptops.insertMany(batch, { ordered: false });
}

// Create indexes for better query performance
db.laptops.createIndex({ "extracted_specs.brand": 1 });
db.laptops.createIndex({ "extracted_specs.price": 1 });
db.laptops.createIndex({ "extracted_specs.processor_brand": 1 });

// Print import results
print('Data import completed');
print('Total documents imported:', db.laptops.count());