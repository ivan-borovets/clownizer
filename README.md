# Clownizer

Telegram UserBot to make fun of your friends by reacting with emoji to their messages

## Workflow

1. [Specify preferences in `src/config.yaml`](#explaining-srcconfigyaml)
2. [Pull or build a Docker container with the app](#installation)
3. Launch the app and have fun!

Find detailed instructions below

## Features

1. Processing messages of a correct type:
    - from the list of allowed chats
    - from the list of allowed people
2. Generating random response emoticons:
    - from the list of allowed emoticons
    - with regard to chat preferences
    - considering target friendship status
3. Converting emoticons to emojis
4. Attaching emojis to a target's message:
    - immediately upon receipt
    - in the amount of 1-3 (Telegram Premium for 2+)
5. Replacing attached emojis with different ones:
    - in a randomly selected one from recent target's messages
    - at preset time intervals
6. Handling Telegram limitations
7. Logging its actions extensively

## Explaining `src/config.yaml`

- `api_id: 123456`
    - replace `123456` with `api_id` from [here](https://core.telegram.org/api/obtaining_api_id)
- `api_hash: 12345a678b9c0d12ef123g45ef678g90`
    - replace `12345a...` with `api_hash` from [here](https://core.telegram.org/api/obtaining_api_id)
- `msg_queue_size: 10`
    - (optional) replace `10` with any positive integer of recent messages the app should remember
- `update_timeout: 5` (seconds)
    - (optional) replace `5` with any integer `>=2` to set the timeout between replacing emojis
- `update_jitter: 2` (seconds)
    - (optional) replace `2` with any non-negative integer to set the maximum delay after `update_timeout`
- `chats_allowed:`
    - `"-12345": Test Chat Name`

    1. Replace `-12345` with valid `chat_id` (try this [bot](https://t.me/GetChatID_IL_BOT))
    2. Replace `Test Chat Name` placeholder with anything
    3. You can add any number of chats using the above template
    4. At least one chat must be present
- `targets:`
    - `"123456789":`
        - `Alice`
        - `Enemy`

    1. Replace `123456789` with valid `target_id` (try this [bot](https://t.me/GetChatID_IL_BOT))
    2. Replace `Alice` name placeholder with anything
    3. Replace `Enemy` with one of the values: `Friend` or `Enemy`
    4. You can add any number of targets using the above template
    5. At least one target must be present
- `emoticons_for_enemies:`
    - `🤡`
    - `...`

    1. (optional) Replace any emoticon with the valid one (see `src/constants.py`)
    2. You can add any number of emoticons using the above template
    3. At least one emoticon must be present
- `emoticons_for_friends:`
    - `👍`
    - `...`

    1. Same as `emoticons_for_enemies`

## Installation

1. Make sure you have Docker and Docker Compose installed
2. Download [`docker-compose.yaml`](https://github.com/ivan-borovets/clownizer/blob/master/docker-compose.yaml)
3. Download [`src/config.yaml`](https://github.com/ivan-borovets/clownizer/blob/master/src/config.yaml)
4. The project structure should be as follows:

```
    .
    ├── docker-compose.yaml
    └── src
        └── config.yaml
```
5. Set [the correct settings](#explaining-srcconfigyaml) in `src/config.yaml`
6. Restart Docker: 

    ```shell
    sudo systemctl restart docker
    ```
7. Get app image:
    ```shell
    sudo docker compose pull
    ```
8. Launch the app:
    ```shell
    sudo docker compose run clownizer
    ```
9. Auth in Telegram (once)
10. Wait for message: `"Handlers are registered. App is ready to work"`. From this point on, the app will perform
    its task. `Ctrl+C` to stop execution

## Installation alternatives
1. Clone this repo

    ```shell
    git clone https://github.com/ivan-borovets/clownizer.git
    ```
2. Set [the correct settings](#explaining-srcconfigyaml) in `src/config.yaml`

### With Docker-Compose:
3. Make sure you have Docker and Docker Compose installed
4. Restart Docker: 

    ```shell
    sudo systemctl restart docker
    ```
5. Build app image:

    ```shell
    sudo docker compose build
    ```
6. Launch the app:
    ```shell
    sudo docker compose run clownizer
    ```
7. Auth in Telegram (once)
8. Wait for message: `"Handlers are registered. App is ready to work"`. From this point on, the app will perform
    its task. `Ctrl+C` to stop execution

### With Poetry:
3. Use [Poetry](https://python-poetry.org/) to set up a virtual environment. If Poetry is already installed in the
   root folder, try:

-   ```sh
    poetry shell
    ```
-   ```sh
    poetry install
    ```

Instead, you can set up venv using `pyproject.toml`

4. Run `src/main.py` with Python from venv
5. Auth in Telegram (once)
6. Wait for message: `"Handlers are registered. App is ready to work"`. From this point on, the app will perform
    its task. `Ctrl+C` to stop execution

## Troubleshooting installation
1. If `UserWarning: Can not find any timezone configuration, defaulting to UTC.` but correct log times are
      important, try:
   1. Choose your timezone from
        ```sh
        timedatectl list-timezones
        ```
   2. Set your timezone with
        ```sh
        sudo timedatectl set-timezone <your_timezone>
        ```
   3. `/etc/localtime` should appear (check with `ls /etc/localtime`)
