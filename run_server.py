#!/usr/bin/env python3
"""
FastAPI server startup script for Mindora ADK Agents.
Reuses logic from backend/run.py and calls backend/fast_api.py.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import click
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.fast_api import get_fast_api_app


@click.command()
@click.option(
    "--agents-dir",
    default="agents",
    help="Directory containing agent subdirectories",
)
@click.option(
    "--host",
    default="127.0.0.1",
    help="Host to bind the server to",
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="Port to bind the server to",
)
@click.option(
    "--reload",
    is_flag=True,
    default=True,
    help="Enable auto-reload for development",
)
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level",
)
@click.option(
    "--session-service-uri",
    help="Session service URI",
)
@click.option(
    "--artifact-service-uri", 
    help="Artifact service URI",
)
@click.option(
    "--memory-service-uri",
    help="Memory service URI",
)
@click.option(
    "--eval-storage-uri",
    help="Evaluation storage URI",
)
@click.option(
    "--allow-origins",
    multiple=True,
    help="Allowed CORS origins",
)
@click.option(
    "--trace-to-cloud",
    is_flag=True,
    default=False,
    help="Enable tracing to Google Cloud",
)
@click.option(
    "--a2a",
    is_flag=True,
    default=False,
    help="Enable A2A (Agent-to-Agent) support",
)
@click.option(
    "--reload-agents",
    is_flag=True,
    default=False,
    help="Enable agent auto-reload",
)
def main(
    agents_dir: str,
    host: str,
    port: int,
    reload: bool,
    log_level: str,
    session_service_uri: Optional[str],
    artifact_service_uri: Optional[str],
    memory_service_uri: Optional[str],
    eval_storage_uri: Optional[str],
    allow_origins: tuple[str, ...],
    trace_to_cloud: bool,
    a2a: bool,
    reload_agents: bool,
):
    """Start the FastAPI server for Mindora ADK Agents."""
    
    # Set up logging
    logging.basicConfig(level=getattr(logging, log_level.upper()))
    logger = logging.getLogger(__name__)
    
    # Convert tuple to list for allow_origins
    allow_origins_list = list(allow_origins) if allow_origins else None
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan manager."""
        click.secho(
            f"""
+-----------------------------------------------------------------------------+
| Mindora ADK Agents Server Started                                          |
|                                                                             |
| Access at: http://{host}:{port}{' ' * (49 - len(f'{host}:{port}'))}|
+-----------------------------------------------------------------------------+
""",
            fg="green",
        )
        yield
        click.secho(
            """
+-----------------------------------------------------------------------------+
| Mindora ADK Agents Server Shutting Down...                                 |
+-----------------------------------------------------------------------------+
""",
            fg="green",
        )
    
    logger.info(f"Starting FastAPI server with agents directory: {agents_dir}")
    logger.info(f"Server will be available at: http://{host}:{port}")
    
    # Create FastAPI app using the existing function
    app = get_fast_api_app(
        agents_dir=agents_dir,
        session_service_uri=session_service_uri,
        artifact_service_uri=artifact_service_uri,
        memory_service_uri=memory_service_uri,
        eval_storage_uri=eval_storage_uri,
        allow_origins=allow_origins_list,
        web=False,  # Enable web interface
        trace_to_cloud=trace_to_cloud,
        a2a=a2a,
        host=host,
        port=port,
        reload_agents=reload_agents,
        lifespan=lifespan,
    )
    
    # Configure and run the server
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level.lower(),
    )
    
    server = uvicorn.Server(config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()