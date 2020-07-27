from flask_cors import CORS

import server

# server.app.debug = True
# server.logger.setLevel("DEBUG")
# CORS(server.app, supports_credentials=True)

if __name__ == '__main__':
    server.dbInit()
    server.app.run(port=5000)
