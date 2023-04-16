# digital-odyssey

Digital Odyssey is an ecommerce web application built using Python Flask framework. The application provides features such as browsing products, adding them to cart, and making orders. The application also uses Elasticsearch for search functionality. In this README, we will provide detailed instructions on how to install and run Digital Odyssey.

## Prerequisites
Before installing and running Digital Odyssey, you need to have the following prerequisites:
  - Python 3.7 or higher
  - Pip (Python package manager)
  - Docker
 
 ## Installation
 To install Digital Odyssey, follow these steps:
  1. Clone the repository:
```bash
git clone https://github.com/your-username/digital-odyssey.git
```
  2. Navigate to the project directory:
```bash
cd digital-odyssey
```
  4. Create a virtual environment:
```bash
python -m venv env
```
  6. Activate the virtual environment:
```bash
source env/bin/activate
```
  8. Install the required Python packages:
```bash
pip install -r requirements.txt
```
  10. Build the Elasticsearch Docker container:
```bash
docker build -t elasticsearch -f Dockerfile.el .
```
## Running
  1. Activate the virtual environment:
```bash
source env/bin/activate
```
  3. Start Elasticsearch container (or use your own and edit the configuration files):
```bash
docker run --name myelasticsearch -m 1gb elasticsearch
```
  4. Start the Flask application:
```bash
flask run
```
This will start the Flask application at http://localhost:5000.
 
## Options
```python
flask --help
Usage: flask [OPTIONS] COMMAND [ARGS]...

  A general utility script for Flask applications.

  An application to load must be given with the '--app' option, 'FLASK_APP'
  environment variable, or with a 'wsgi.py' or 'app.py' file in the current
  directory.

Options:
  -e, --env-file FILE   Load environment variables from this file. python-
                        dotenv must be installed.
  -A, --app IMPORT      The Flask application or factory function to load, in
                        the form 'module:name'. Module can be a dotted import
                        or file path. Name is not required if it is 'app',
                        'application', 'create_app', or 'make_app', and can be
                        'name(args)' to pass arguments.
  --debug / --no-debug  Set debug mode.
  --version             Show the Flask version.
  --help                Show this message and exit.

Commands:
  db      Perform database migrations.
  fake
  routes  Show the routes for the app.
  run     Run a development server.
  shell   Run a shell in the app context.

```