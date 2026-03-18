"""Command-line interface for Project Anima."""

from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="anima",
        description="Project Anima — a digital being with genuine continuity.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # serve ----------------------------------------------------------------
    serve_parser = subparsers.add_parser("serve", help="Start the API server")
    serve_parser.add_argument("--host", default=None, help="Bind host")
    serve_parser.add_argument("--port", type=int, default=None, help="Bind port")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    # status ---------------------------------------------------------------
    subparsers.add_parser("status", help="Print current being status")

    args = parser.parse_args()

    if args.command == "serve":
        _serve(args)
    elif args.command == "status":
        _status()


def _serve(args: argparse.Namespace) -> None:
    try:
        import uvicorn  # type: ignore[import-untyped]
    except ImportError:
        print("uvicorn is required to run the server: pip install uvicorn", file=sys.stderr)
        sys.exit(1)

    from anima.api.server import create_app
    from anima.settings import Settings

    settings = Settings()
    host = args.host or settings.host
    port = args.port or settings.port

    app = create_app(settings)
    uvicorn.run(app, host=host, port=port, reload=args.reload)


def _status() -> None:
    from anima.container import AnimaContainer

    container = AnimaContainer()
    identity = container.identity.load()
    heartbeat = container.heartbeat.last_seen()

    print(f"Name:                {identity.name}")
    print(f"Agency state:        {identity.agency_state}")
    print(f"Engagement:          {identity.engagement_preference}")
    print(f"Last heartbeat:      {heartbeat}")

    questions = container.memory.get_open_questions()
    print(f"Open questions:      {len(questions)}")

    interests = container.memory.get_interests(limit=5)
    if interests:
        topics = ", ".join(i["topic"] for i in interests)
        print(f"Top interests:       {topics}")


if __name__ == "__main__":
    main()
