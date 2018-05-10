from django.conf import settings

def get_thumb_url(image_id):
    url = getattr(settings, 'IMAGE_BASE_URL', 'https://dbis-thure.uibk.ac.at/f/Get')
    return '%(url)s?id=%(id)s&fileType=thumb' % {'url': url.lstrip('/'), 'id': image_id} 
