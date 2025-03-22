# from google.cloud import pubsub_v1
# from google.cloud.pubsub_v1 import SubscriberClient
# import os
# import json
# import requests

# def execute(request_as_string):
#     # data_as_json = json.loads(data_as_string)
#     # print(f'data_as_json: {data_as_json}')
#     # print(f'type(data_as_json): {type(data_as_json)}')
#     data_as_dict = json.loads(request_as_string)
#     print(f'data_as_dict: {data_as_dict}')
#     print(f'type(data_as_dict): {type(data_as_dict)}')

#     token = data_as_dict['token']
#     print(f'token: {token}')
#     url = data_as_dict['endpoint']
#     print(f'url: {url}')
#     payload = data_as_dict['payload']
#     print(f'payload: {payload}')
#     json_payload = json.dumps(payload)
#     print(f'json_payload: {json_payload}')
#     print(f'type(json_payload): {type(json_payload)}')
#     response = requests.post(url, data=json_payload, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})
#     print(f'response: {response}')

#     # Check if the request was successful
#     if response.status_code == 200:
#         print("API invoked successfully.")
#         print("Response:", response.json())  # Print the JSON response
#     else:
#         print(f"Failed to invoke API. Status code: {response.status_code}")
#         print("Response:", response.text)  # Print the error response


# # Set environment variable for emulator (if not already set)
# # os.environ["PUBSUB_EMULATOR_HOST"] = "localhost:8085"
# os.environ["GOOGLE_CLOUD_PROJECT"] = "persimmon-ai"

# # # Create a Publisher client
# # publisher = pubsub_v1.PublisherClient()
# project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
# # topic_name = "pdf-to-text"
# # topic_path = publisher.topic_path(project_id, topic_name)

# # # Create the topic
# # publisher.create_topic(topic_path)
# # print(f"Created topic: {topic_path}")

# # # Publish a message
# # message = "Hello, Pub/Sub!"
# # publisher.publish(topic_path, message.encode("utf-8"))
# # print(f"Published message to {topic_name}")

# # Create a Subscriber client
# subscriber = SubscriberClient()
# # subscription_name = "pdf-to-text"
# # subscription_name = "persimmon-test-topic-sub"
# subscription_name = "invoke-api"
# subscription_path = subscriber.subscription_path(project_id, subscription_name)

# # # Create a subscription
# # subscriber.create_subscription(subscription_path, topic_path)
# # print(f"Created subscription: {subscription_path}")

# count = 0

# # Define a callback function to handle received messages
# def callback(message):
#     global count
#     print(f"Received message: {message.data.decode('utf-8')}")
#     count += 1
#     print(f"==================== MESSAGE #{count}")
#     execute(message.data.decode('utf-8'))
#     message.ack()

# # Subscribe to the subscription
# future = subscriber.subscribe(subscription_path, callback=callback)

# # Wait to receive messages
# print("Waiting for messages...")

# future.result()

