from flask import Flask
from kubelet_stats_exporter.config import EXPORTER_PORT
from kubelet_stats_exporter.exporter import bp
from kubelet_stats_exporter.logging import logger

def main():
    """Main Function
    Flask Application handling
    """
    logger.info(f"Starting Kubelet Stats Exporter App in port: {EXPORTER_PORT}")
    application = Flask(__name__)
    application.register_blueprint(bp)
    application.run(host='0.0.0.0', port=EXPORTER_PORT)

if __name__ == "__main__":
    main()
