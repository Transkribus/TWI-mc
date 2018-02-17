from django.db import models


#Store dynamic content of the page
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
  