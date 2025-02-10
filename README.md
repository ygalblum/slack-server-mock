# Slack Server Mock
Slack server mock is intended to be used for sub-system testing of Slack applications.

## Running the Server

### Required files

#### settings.yaml
Create a settings.yaml file based on the [sample file](./settings.yaml).

#### Channels file
If you wish to return a list of channels, create a JSON file with an array of channel objects.
At minimum, each entry must have a name and an ID.

In the `settings.yaml` file, set `slack_server.channels_path` to the location of the file.

#### Response Data Configuration
The `settings.yaml` file contains a `response_data` section that allows you to configure the responses of the server for specific endpoints.

The responses definied in the `response_data` section are JSON files that contain the response data for the endpoint.

The directory structure should be as follows:
```
response_data_path
  / endpoint_name
    / ID-VALUE.json
```
See the `test/responses` directory for examples.

For endpoints with multiple query parameters, the file should be named with the query parameters separated by a dash. For example, `conversations.history/channel-ts.json`.

In the `settings.yaml` file, set the `response_data` section to the base path for the JSON files.

### Using Poetry

#### Prerequisites
Install [poetry](https://python-poetry.org/docs/)

#### Installation
- Download the code and change to the downloaded directory:
  ```bash
  git clone https://github.com/ygalblum/slack-server-mock.git
  cd slack-server-mock
  ```
- Install all the requirements using poetry:
  ```bash
  poetry install --no-root
  ```
- Run the application:
  ```bash
  poetry run python -m slack_server_mock
  ```

### Using a Podman/Docker

The server is published in a container image on [quay](https://quay.io/repository/yblum/slack_server_mock).

#### Running the latest version
```bash
podman run --rm -it -d --name slack_server_mock --publish 3001:3001 --publish 8080:8080 --publish 8888:8888 --volume ${PWD}/settings.yaml:/app/settings.yaml:z quay.io/yblum/slack_server_mock:latest
```

#### Channels file
If you are using a channels file, make sure to mount it into the container as well.

## Configure your Slack application
In order to make your Slack application connect with the mock server you need to override its `base_url`.

### Socket mode
Instead of:
```python
handler = SocketModeHandler(
    App(token=BOT_TOKEN),
    APP_TOKEN
)
```

Use:
```python
handler = SocketModeHandler(
    app=App(
        client=WebClient(
            token=BOT_TOKEN,
            base_url="http://localhost:8888"
        )
    ),
    app_token=settings.slackbot.app_token
)
```

## Interacting with the application
The mock server provides an endpoint to send a message to the application,
wait for the application response and return the accumulated ephemeral messages (if sent) and the response.

### Message payload
The request payload is a JSON with the key `message` whose value is a string

### Response payload
The response payload is a JSON with two keys:

- `ephemeral`: List of strings. All accumulated ephemeral message
- `response`: string. The application's response

### Example
Send a message using `curl` and see the response:
```bash
$ curl http://localhost:8080/message -d'{"message": "hello"}'
{"answer": "Hello to you too", "ephemeral": ["I'll be right with you"]}
```
