from src.consumers.event_router import EventRouter


def main():
    router = EventRouter()
    router.start()


if __name__ == "__main__":
    main()
