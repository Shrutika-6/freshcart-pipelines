import json
import random
import time
from datetime import datetime
import pika

def generate_order(msg_id, valid=True):
    cities = ['Bangalore', 'Chennai']
    zones = ['koramangala', 'indiranagar', 'whitefield', 'tnagar', 'velachery']
    types = ['ride', 'food']
    
    city = random.choice(cities)
    zone = random.choice(zones)
    order_type = random.choice(types)
    
    msg = {
        "id": f"REQ-{msg_id:04d}",
        "city": city,
        "type": order_type,
        "ts": datetime.now().isoformat()
    }
    
    # D3 requirement: every 10th message is bad (missing zone)
    if valid:
        msg["zone"] = zone
        routing_key = f"{city.lower()}.{zone.lower()}.{order_type.lower()}"
    else:
        # Invalid message: missing zone
        routing_key = f"{city.lower()}.unknown.{order_type.lower()}"
        
    return routing_key, msg

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declare topic exchange
    channel.exchange_declare(exchange='rapido-dispatch', exchange_type='topic')
    print("[*] Dispatcher started. Publishing messages to exchange 'rapido-dispatch'...")

    msg_id = 1
    try:
        while True:
            # Send one bad message every 10 messages (e.g. msg_id % 10 == 0)
            is_valid = (msg_id % 10 != 0)
            routing_key, message = generate_order(msg_id, valid=is_valid)
            body = json.dumps(message)
            
            channel.basic_publish(
                exchange='rapido-dispatch',
                routing_key=routing_key,
                body=body
            )
            status = "VALID" if is_valid else "INVALID (missing zone)"
            print(f" [x] Sent [{routing_key}] ({status}): {body}")
            
            msg_id += 1
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nDispatcher stopped.")
    finally:
        connection.close()

if __name__ == '__main__':
    main()
