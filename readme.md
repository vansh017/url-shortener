# URL Shortener Service

This project is a URL Shortener Service implemented in Python using FastAPI and SQLAlchemy. It allows users to shorten URLs, track usage analytics, and set expiration times for shortened links.

## Features

1. **Shorten URLs**: Convert long URLs into shortened versions.
2. **Expiration**: Optionally specify an expiration time (in hours) for each shortened URL. Defaults to 24 hours if not provided.
3. **Analytics**: Track the number of times a shortened URL has been accessed, including timestamps and IP addresses.
4. **Data Persistence**: Store data in an SQLite database.
5. **Endpoints**:
   - `POST /shorten`: Create a shortened URL.
   - `GET /<short_url>`: Redirect to the original URL if not expired.
   - `GET /analytics/<short_url>`: Retrieve analytics for a specific shortened URL.

## Prerequisites

- Python 3.8 or later
- Pip

### Clone the Repository

```bash
# HTTPS
https://github.com/vansh017/url-shortener.git

# or SSH
git@github.com:vansh017/url-shortener.git

# Change to project directory
cd url-shortener
```


## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirement.txt 
   ```



## Running the Application

1. Start the server:
   ```bash
   python app.py
   ```

### Security Features

- Optional password protection
- Secure password hashing (MD-5)
- Configurable URL expiration
- Prevents unauthorized access

### Error Scenarios

- **No Password Provided**: 401 Unauthorized
- **Incorrect Password**: 403 Forbidden
- **Expired URL**: 410 Gone

## Best Practices

- Use strong, unique passwords
- Set appropriate expiration times
- Avoid sharing sensitive URLs in public spaces

## API Endpoints

### 1. `POST /shorten`

**Description**: Create a shortened URL.

- **Request Body**:
  ```json
  {
    "original_url": "https://example.com",
    "expiration_hours": 24
  }
  ```
- **Response**:
  ```json
  {
    "shortened_url": "https://short.ly/abc123"
  }
  ```

### 2. `GET /<short_url>`

**Description**: Redirect to the original URL if the shortened URL is still valid.

- **Response**:
  ```json
  {
    "redirect_to": "https://example.com"
  }
  ```

### 3. `GET /analytics/<short_url>`

**Description**: Retrieve analytics data for a specific shortened URL.

- **Response**:
  ```json
  {
    "original_url": "https://example.com",
    "access_count": 5,
    "access_logs": [
      { "timestamp": "2025-01-18T12:00:00", "ip_address": "192.168.1.1" },
      { "timestamp": "2025-01-18T12:05:00", "ip_address": "192.168.1.2" }
    ]
  }
  ```

## Database Schema

1. **`urls` Table**:

   - `id`: Primary key
   - `original_url`: Original long URL
   - `shortened_url`: Unique shortened URL
   - `creation_time`: Timestamp of creation
   - `expiration_time`: Expiration timestamp
   - `access_count`: Number of times the shortened URL has been accessed

2. **`access_logs` Table**:

   - `id`: Primary key
   - `url_id`: Foreign key to `urls` table
   - `timestamp`: Access timestamp
   - `ip_address`: IP address of the client

## Troubleshooting

- Ensure the database path exists and is writable.
- Verify that the server is running on the correct host and port.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
