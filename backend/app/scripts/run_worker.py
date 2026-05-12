from app.workers.celery_app import celery_app


def main() -> None:
    celery_app.worker_main(["worker", "--loglevel=info"])


if __name__ == "__main__":
    main()
