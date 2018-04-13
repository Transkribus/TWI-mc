from django.db import models


# Storage of the top carousel articles
class HomeArticle (models.Model):
    changed = models.DateField(auto_now_add=True)
    image = models.FilePathField(max_length=512, null=True)
    
class HomeArticleEntry (models.Model):
    lang = models.CharField("Title", max_length=2)
    title = models.CharField("Title", max_length=200)
    shortdesc = models.TextField()
    content = models.TextField()
    changed = models.DateField(auto_now_add=True)
    article = models.ForeignKey(HomeArticle, on_delete=models.CASCADE, blank=True, null=True, related_name='article')
    
# Main Class for blogs, linked to the entries, which do contain real content
class Blog(models.Model):
    changed = models.DateField(auto_now_add=True)
    image = models.FilePathField(max_length=512, null=True)
    
class BlogEntry(models.Model):
    title = models.CharField("Title", max_length=200)
    subtitle = models.CharField("Title", max_length=512, null=True)
    content = models.TextField()
    lang = models.CharField(max_length=2)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, blank=True, null=True, related_name='blog')
    changed = models.DateField(auto_now_add=True)


class Institution(models.Model):
    lat= models.DecimalField(decimal_places=4, max_digits=12) #latitude
    lng= models.DecimalField(decimal_places=4, max_digits=12) #longitude  
    link = models.CharField(max_length=512, null=False) #the link to the institution
    image = models.FilePathField(max_length=512, null=True)
    changed = models.DateField(auto_now_add=True)

class InstitutionDescription(models.Model):
    name = models.CharField( max_length=200)
    loclabel=models.CharField(max_length=30) #the label of the location for displaying on the map
    desc = models.TextField() # full description
    lang = models.CharField(max_length=2)
    inst = models.ForeignKey(Institution, on_delete=models.CASCADE, blank=True, null=True)
    changed = models.DateField(auto_now_add=True)
    
class InstitutionProject(models.Model):
    inst = models.ForeignKey(Institution, on_delete=models.CASCADE, blank=True, null=True)
    changed = models.DateField(auto_now_add=True)
    
class InstitutionProjectEntries(models.Model):
    title = models.CharField("Title", max_length=200)
    desc = models.TextField() # full description
    lang = models.CharField(max_length=2)
    project = models.ForeignKey(InstitutionProject, on_delete=models.CASCADE, blank=True, null=True)
    changed = models.DateField(auto_now_add=True)

class Service(models.Model):
    image_css = models.CharField(max_length=512, null=True)
    
class ServiceEntries(models.Model):    
    title = models.CharField("Title", max_length=200)
    subtitle = models.CharField("Title", max_length=512, null=True)
    content = models.TextField()
    lang = models.CharField(max_length=2)
    changed = models.DateField(auto_now_add=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, blank=True, null=True)
 
class Quote(models.Model): 
    name = models.CharField( max_length=200)
    image = models.FilePathField(max_length=512, null=True)
    changed = models.DateField(auto_now_add=True)
 
class QuoteEntries(models.Model):
    content = models.TextField()
    role = models.CharField( max_length=200)
    changed = models.DateField(auto_now_add=True)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, blank=True, null=True)
    lang = models.CharField(max_length=2)
    
class Video(models.Model):
    vid = models.CharField(max_length=200)
    
class VideoDesc(models.Model):
    title = models.CharField( max_length=200)
    desc = models.TextField()       
    lang = models.CharField(max_length=2)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, blank=True, null=True)
    
    
class Document(models.Model):  
    icon = models.CharField( max_length=200)
    changed = models.DateField(auto_now_add=True)
    
class DocumentEntries(models.Model):
    title = models.CharField( max_length=200)
    desc = models.TextField()    
    content = models.TextField()
    lang = models.CharField(max_length=2)
    doc = models.ForeignKey(Document, on_delete=models.CASCADE, blank=True, null=True)
    changed = models.DateField(auto_now_add=True)
          