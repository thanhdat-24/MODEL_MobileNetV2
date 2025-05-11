from supabase import create_client, Client
from postgrest import APIError
import time
from config import SUPABASE_URL, SUPABASE_ANON_KEY

def get_supabase_client(max_retries=3, retry_delay=1) -> Client:
    retry_count = 0
    last_error = None
    
    while retry_count < max_retries:
        try:
            client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            client.table('taikhoan').select('id').limit(1).execute()
            return client
        except (APIError, Exception) as e:
            last_error = e
            retry_count += 1
            time.sleep(retry_delay * (2 ** (retry_count - 1)))
    
    error_msg = f"Không thể kết nối đến Supabase sau {max_retries} lần thử: {str(last_error)}"
    raise Exception(error_msg)
