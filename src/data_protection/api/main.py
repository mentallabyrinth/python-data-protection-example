import uvicorn


def run() -> None:
    uvicorn.run(
        "data_protection.api.app:create_app",
        factory=True,
        host="127.0.0.1",
        port=8000,
    )


if __name__ == "__main__":
    run()
