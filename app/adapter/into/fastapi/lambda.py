from mangum import Mangum

from .main import app

# To plug into lambda
handler = Mangum(app)
