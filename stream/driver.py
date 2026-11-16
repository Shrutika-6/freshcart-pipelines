import sys
import json
import pika

def main():
    if len(sys.argv) < 3:
        print("Usage: python driver.py <DRIVER_NAME> <BINDING_PATTERN>")
        sys.exit(1)

    driver_name = sys.argv[1]
    binding_pattern = sys.argv[2]

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declare topic exchange matching dispatcher
    channel.exchange_declare(exchange='rapido-dispatch', exchange_type='topic')

    # Declare private exclusive queue
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind queue to exchange with given pattern
    channel.queue_bind(exchange='rapido-dispatch', queue=queue_name, routing_key=binding_pattern)

    print(f"[*] Driver '{driver_name}' listening on pattern '{binding_pattern}'. To exit press CTRL+C")

    def callback(ch, method, properties, body):
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception as e:
            print(f"[{driver_name}] ERROR: Failed to parse JSON: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        # D3 Requirement: If message is missing 'zone', reject with basic_nack(requeue=False)
        if 'zone' not in payload or not payload['zone']:
            print(f"[{driver_name}] [NACK] REJECTED (Missing 'zone'): {payload['id']} | Key: {method.routing_key}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        else:
            print(f"[{driver_name}] [ACK] ACCEPTED: {payload['id']} | Key: {method.routing_key} | Payload: {payload}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nDriver exited.")
