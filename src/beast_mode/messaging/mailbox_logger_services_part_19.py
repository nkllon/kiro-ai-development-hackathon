from datetime import datetime
from typing import Dict, List, Any

        def run_logger():
            """Run the logger in its own event loop"""
            try:
                self.event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.event_loop)
                self.event_loop.run_until_complete(self.logger.start_logging())
                self.event_loop.run_forever()
            except Exception as e:
                logger.error(f'Error in background logger thread: {e}')
            finally:
                if self.event_loop:
                    self.event_loop.close()
        self.background_thread = threading.Thread(target=run_logger, daemon=True)
        self.background_thread.start()
        self.is_running = True
        logger.info('MailboxLogger started in background thread')
