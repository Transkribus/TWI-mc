def get_thumb_url(image_id):
    url = 'https://dbis-thure.uibk.ac.at/f/Get'
    return '%s(url)s?id=%(id)&fileType=thumb' % {'url': url.lstrip('/'), 'id': image_id} 
