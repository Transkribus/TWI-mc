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
  