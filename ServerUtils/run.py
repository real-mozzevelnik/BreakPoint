from app import app
from app.config import DEBUG, IP

if __name__=='__main__':
    app.run(debug = DEBUG, host = IP)
