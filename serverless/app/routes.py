import json
import logging

from fastapi.routing import APIRoute

logger = logging.getLogger(__name__)


class LoggingRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def custom_route_handler(request):
            url = str(request.url)
            method = request.method
            try:
                req = json.loads((await request.body()).decode())
            except Exception:
                req = ""
            logger.info("dump req: %s %s: %s", method, url, req)

            # Execute the path operation
            response = await original(request)

            status_code = response.status_code
            try:
                res = json.loads(response.body.decode())
            except Exception:
                res = ""
            logger.info("dump res: %s %s %s: %s", status_code, method, url, res)
            return response

        return custom_route_handler
