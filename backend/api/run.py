from app import create_app
from app.mqtt_subscriber import MQTTSubscriber
import signal
import sys


app = create_app()
subscriber = None





def signal_handler(sig, frame):
    print("Shutting down gracefully...")
    if subscriber:
        subscriber.disconnect()
    sys.exit(0)




if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    subscriber = MQTTSubscriber(app)
    subscriber.connect()


    app.run(host='0.0.0.0', port=5000, debug=False)