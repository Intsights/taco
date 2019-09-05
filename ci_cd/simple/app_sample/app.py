import json


def my_example_lambda(events, context):
    print('Got events: {event}', format(event=str(events)))
    for received_event in events['Records']:
        event_body = json.loads(received_event['body'])
        print('Event body: {event_body}'.format(event_body=event_body))
