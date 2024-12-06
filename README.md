# Pronote Notifier

Pronote Notifier is a Python script that periodically checks for new grades on Pronote and sends notifications to a Discord channel using webhooks.

### This project is open source, so you can create a Pull request for new functionality

## Requirements

- Python 3.6+
- `discord_webhook`
- `pronotepy`
- `python-dotenv`
- `requests`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Awakno/PronoteNotifier.git
    cd PronoteNotifier
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.env` file based on the `.env.example` file and fill in your Pronote credentials and Discord webhook URL:
    ```sh
    cp .env.example .env
    ```

4. Edit the `.env` file with your credentials and webhook URLs:
    ```properties
    # Crendentials for the pronote account
    PRONOTE_URL="https://your-pronote-url"
    PRONOTE_USERNAME="your-username"
    PRONOTE_PASSWORD="your-password"

    # Webhook
    DISCORD_WEBHOOK_URL="your-discord-webhook-url"
    CUSTOM_WEBHOOK_URL="your-custom-webhook-url"
    CUSTOM_WEBHOOK_PASS="your-custom-webhook-pass"
    ```

## Usage

Run the script:
```sh
python pronotenotifier.py
```

## Todo

#### Add planning change notification: ❌
#### Add canceled / absent teacher notification: ❌
#### Add anothers method for notification: ❌

Enjoy ⭐