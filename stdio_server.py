#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standard Input/Output MCP Server
Communicates with clients through stdin/stdout
"""

import sys
import json
import asyncio
import logging
from mcp_server import MCPServer


class StdioServer:
    """Standard Input/Output Server class"""
    
    def __init__(self):
        self.mcp_server = MCPServer()
        self.logger = logging.getLogger(__name__)
        
        # Configure logging to stderr to avoid confusion with stdout communication
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging output"""
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    async def run(self):
        """Run standard input/output server"""
        self.logger.info("PixelMug MCP Standard I/O Server started")
        
        try:
            while True:
                # Read request from stdin
                line = await self._read_line()
                if not line:
                    break
                
                try:
                    # Process request
                    response = await self.mcp_server.handle_request(line)
                    
                    # Send response to stdout
                    await self._write_line(response)
                    
                except Exception as e:
                    self.logger.error(f"Error occurred while processing request: {str(e)}")
                    error_response = self._create_error_response(None, -32603, str(e))
                    await self._write_line(error_response)
        
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down server")
        except Exception as e:
            self.logger.error(f"Error occurred while running server: {str(e)}")
        finally:
            self.logger.info("Server closed")
    
    async def _read_line(self) -> str:
        """Read a line asynchronously"""
        loop = asyncio.get_event_loop()
        line = await loop.run_in_executor(None, sys.stdin.readline)
        return line.strip()
    
    async def _write_line(self, content: str):
        """Write a line asynchronously"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._write_stdout, content)
    
    def _write_stdout(self, content: str):
        """Write to standard output"""
        sys.stdout.write(content + '\n')
        sys.stdout.flush()
    
    def _create_error_response(self, request_id, code: int, message: str) -> str:
        """Create error response"""
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        }
        return json.dumps(response, ensure_ascii=False)


async def main():
    """Main function"""
    server = StdioServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
