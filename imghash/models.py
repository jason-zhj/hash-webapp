from django.db import models

# Create your models here.
class ImageLabel(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def get_image_num(self,domains=None):
        "return number of images with this label"
        if (not domains):
            return self.image_set.all().count()
        else: # filter domains
            return self.image_set.filter(domain__in=domains).count()

class Image(models.Model):
    label = models.ForeignKey(ImageLabel)
    file_path = models.TextField()
    domain = models.CharField(choices=[
        ("amazon","amazon"),
        ("webcam","webcam"),
        ("dslr","dslr")
    ],max_length=50)

# hash code table for image, this can have multiple implementations
class HashCode(models.Model):
    image = models.OneToOneField(Image)
    code = models.CharField(max_length=200,db_index=True)
    # non-DB fields
    name = "abstract hash code table"
    hash_size = None

    class Meta:
        abstract = True


class NonTransferLatentHashCode(HashCode):
    name = "Non-transfer latent hash code"
    hash_size = 16