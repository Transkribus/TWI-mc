from django.db import models


class Blog(models.Model):
  a_key = models.IntegerField()
  language = models.CharField("Title", max_length=2)
  title = models.CharField("Title", max_length=200)
  content = models.TextField()
  changed = models.DateField(auto_now_add=True)
  image = models.FilePathField(max_length=512, null=True)
  
  class Meta:
      unique_together = (("a_key", "language"),)
       
  def __str__(self):
      return str(self.title) + ":"  + str(self.content) + "(" + str(self.changed) + ")\n" 
    

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
  