from flask import Flask, request
app = Flask(__name__, static_folder='static/search/', static_url_path='')
import json
import sys

import coffeescript

from searcher import Searcher

@app.route('/')
def root():
    """
    Default route of the project that loads static resources
    """
    return app.send_static_file('index.html')

@app.route('/search-api', methods=['POST'])
def search_api():
    """
    Route to query the Search API for movies
    """
    return app.searcher.search(request.get_json())

def server(config):
    """
    Function to initialize the server using the config file
    @param config: Configuration file
    """
    app.searcher = Searcher(config)
    return app

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: {} config.toml".format(sys.argv[0]))
        sys.exit(1)

    server(sys.argv[1]).run(debug=True)
