# Dockerfile
# Stage 1: Import data
FROM mongo:6.0 as builder

# Install Node.js and npm for the import script
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create app directory and copy files
WORKDIR /app
COPY data.csv ./
COPY import-script.js ./
COPY package.json ./

# Install dependencies
RUN npm install

# Create directory for mongodb data
RUN mkdir -p /mongodb_data

# Set environment variables
ENV MONGODB_DATA_DIR=/mongodb_data \
    MONGO_INITDB_DATABASE=laptop_specs

# Start MongoDB and import data
RUN mongod --fork --logpath /var/log/mongodb.log --dbpath $MONGODB_DATA_DIR && \
    mongosh $MONGO_INITDB_DATABASE /app/import-script.js && \
    mongod --dbpath $MONGODB_DATA_DIR --shutdown

# Stage 2: Final image
FROM mongo:6.0

# Copy the pre-built database from builder
COPY --from=builder /mongodb_data /data/db

# Set environment variables for the final image
ENV MONGO_INITDB_DATABASE=laptop_specs

# Expose MongoDB port
EXPOSE 27017

# Start MongoDB
CMD ["mongod", "--bind_ip_all"]