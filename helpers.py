from django.conf import settings

def get_thumb_url(image_id):
    url = settings.IMAGE_BASE_URL
    return '%(url)s?id=%(id)s&fileType=thumb' % {'url': url.lstrip('/'), 'id': image_id} 
