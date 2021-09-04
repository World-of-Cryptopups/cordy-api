# cordy-api

API Data for Cordy

This is to minimize library use of Deta Base SDK in various programming languages and apps.

## Development

- `.env` file setup

  ```
    DETA_PROJECT_KEY=your-project-key
  ```

- Run using `uvicorn` in development
  ```
    uvicorn main:app --reload --env-file .env
  ```

&copy; 2021 | World of Cryptopups
