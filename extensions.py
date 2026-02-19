from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Limiter
# We use get_remote_address to identify users by IP
# storage_uri="memory://" means rate limits are stored in memory (RAM),
# which is fine for a single process. For multi-process/production with
# multiple workers, you'd want Redis or Memcached.
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"
)
