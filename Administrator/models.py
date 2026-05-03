from django.db import models
class Skill(models.Model):
    # skill_id = models.AutoField(
    #     primary_key=True
    # )
    
    skill_name = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        blank=False
    )

    def __str__(self):
        return self.skill_name
