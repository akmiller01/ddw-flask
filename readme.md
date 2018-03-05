#DDW Flask

An experimental DDW GUI

##To install:
1. Install python 2.7
2. Ensure you have pip installed
3. Clone this repo
4. `pip install -r requirements.txt`

##To run:
`python app.py`

##To bundle:
`pyinstaller --add-data "config:config" --add-data "static:static" --add-data "templates:templates" app.py`