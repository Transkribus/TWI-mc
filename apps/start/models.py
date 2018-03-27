from django.db import models


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



class Institution(models.Model):
    name = models.CharField( max_length=200)
    lat= models.DecimalField(decimal_places=4, max_digits=12) #latitude
    lng= models.DecimalField(decimal_places=4, max_digits=12) #longitude
    loclabel=models.CharField(max_length=30) #the label of the location for displaying on the map
    link = models.CharField(max_length=512, null=False) #the link to the institution

class InstitutionDescription(models.Model):
    desc = models.TextField() # full description
    lang = models.CharField(max_length=2)
    inst = models.ForeignKey(Institution, on_delete=models.CASCADE, blank=True, null=True)
    
class InstitutionProject(models.Model):
    inst = models.ForeignKey(Institution, on_delete=models.CASCADE, blank=True, null=True)
    
class InstitutionProjectEntries(models.Model):
    title = models.CharField("Title", max_length=200)
    desc = models.TextField() # full description
    lang = models.CharField(max_length=2)
    project = models.ForeignKey(InstitutionProject, on_delete=models.CASCADE, blank=True, null=True)
    
    
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

# TODO add image per article?
# Storage of the top carousel articles
class Article (models.Model):
    a_key = models.IntegerField()
    language = models.CharField("Title", max_length=2)
    title = models.CharField("Title", max_length=200)
    content = models.TextField()
    changed = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = (("a_key", "language"),)
       
    def __str__(self):
        return str(self.title) + ":"  + str(self.content) + "(" + str(self.changed) + ")\n" 
  